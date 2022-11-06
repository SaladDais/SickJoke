#include "generated/constants.inc.lsl"
#include "include/macros.inc.lsl"
#include "include/typed_json.inc.lsl"

#include "extern/key_compression.inc.lsl"

// information about what instruction pointer starts on which notecard
// line. Assumes the list is sorted in ascending order, according to IP.
list gCodeLines = [];

list gEventHandlers = [];

// LRU cache for specific code lines from the notecard,
// should be sorted in ascending order, according to LAST_USED.
list gCachedCode = [];

// what state we're in for the initial notecard load
integer gLoadState = LOADSTATE_NONE;

key gNotecardInventoryID = NULL_KEY;

// increases by one every time the VM requests code,
// only used to tag the LRU cache entries. No rollover handling.
integer gCodeRequestNum = 0;
key gNotecardRequestID;
integer gNotecardLine;
// in case we ever have variable-length notecard headers.
integer gHeaderLines;
// What the IP of the line we're currently fetching is
integer gFetchingIP;
integer gFetchingNCAndLine;

// which state the VM's script is in. 0 for "default".
integer gScriptState;

integer gInvokingHandler;
list gQueuedEvents;
// used to respond to llDetected*() calls
list gDetectedStack;

// so we don't re-trigger bootstrapping when state changes
integer gInitialized;

#define EVENT_FOR_STATE(_eh_type) ((gScriptState << 16) | (_eh_type))

lslAssert(integer val) {
    if (!val) {
        llOwnerSay("Assertion failed!");
        llOwnerSay((string)(0.0/0.0));
    }
}

loadNotecard() {
    gScriptState = 0;
    gCodeRequestNum = 0;
    gNotecardLine = 0;
    gHeaderLines = 0;
    gCachedCode = [];
    gCodeLines = [];
    gLoadState = LOADSTATE_NONE;
    gNotecardInventoryID = llGetInventoryKey("script");

    if (gNotecardInventoryID == NULL_KEY) {
        llOwnerSay("Couldn't find script notecard!");
        return;
    }

    integer i;
    integer j;
    for (i=0; i<NUM_CACHED_CODES; ++i) {
        for (j=0; j<CACHEDCODE_STRIDE; ++j) {
            gCachedCode += [-0x7FffFFff];
        }
    }

    gLoadState = LOADSTATE_HANDLERS;
    gNotecardRequestID = llGetNotecardLine("script", 0);
}

sortCachedCode() {
    // Sort the LRU so older entries are nearer the end.
    gCachedCode = llListSort(CLEARABLE_LIST(gCachedCode), CACHEDCODE_STRIDE, FALSE);
}

integer getHandlerIP(integer state_and_event) {
    integer i;
    integer len = llGetListLength(gEventHandlers);
    for(; i<len; i += HANDLERINDEX_STRIDE) {
        if(state_and_event == llList2Integer(gEventHandlers, i + HANDLERINDEX_STATE_AND_EVENT)) {
            return llList2Integer(gEventHandlers, i + HANDLERINDEX_IP);
        }
    }
    return -1;
}

invokeEventHandler(integer eh_type, list args, integer num_detected) {
    integer state_and_event = EVENT_FOR_STATE(eh_type);
    integer ip = getHandlerIP(state_and_event);
    if (ip == -1)
        return;
    string serialized_event = SERIALIZE_LIST(CLEARABLE_LIST(args));

    integer i;
    list detected;
    for(; i<num_detected; ++i) {
        detected += [
            (key)compress_key(llDetectedKey(i)),
            (key)compress_key(llDetectedOwner(i))
        ];
    }

    if (gInvokingHandler) {
        if (llGetListLength(gQueuedEvents) >= MAX_EVENT_QUEUE_SIZE) {
            llOwnerSay("Oops, dropping event on the floor due to queue overflow!");
            return;
        }
        string serialized_detected = SERIALIZE_LIST(CLEARABLE_LIST(detected));
        gQueuedEvents += [state_and_event, ip, serialized_event, serialized_detected];
    } else {
        gInvokingHandler = TRUE;
        gDetectedStack = CLEARABLE_LIST(detected);
        SEND_IPC(IPCTYPE_INVOKE_HANDLER, serialized_event, ip);
    }
}

list getDetectedDefault(integer lsl_type) {
    if (lsl_type == LSLTYPE_INTEGER)
        return [0];
    if (lsl_type == LSLTYPE_STRING)
        return [""];
    else if (lsl_type == LSLTYPE_FLOAT)
        return [0.0];
    else if (lsl_type == LSLTYPE_KEY)
        return [(key)NULL_KEY];
    else if (lsl_type == LSLTYPE_VECTOR)
        return [ZERO_VECTOR];
    else if (lsl_type == LSLTYPE_ROTATION)
        return [<0, 0, 0, 0>];
    else
        LSL_ASSERT(0);
    return [""];
}

sendQueuedEvent() {
    LSL_ASSERT(!gInvokingHandler);
    // do we have any events that were queued up?
    if (gQueuedEvents) {
        // pop an event and send it off
        integer ip = llList2Integer(gQueuedEvents, QUEUEDEVENT_IP);
        string args = llList2String(gQueuedEvents, QUEUEDEVENT_ARGS);
        string detected = llList2String(gQueuedEvents, QUEUEDEVENT_DETECTED_STACK);
        gQueuedEvents = llDeleteSubList(CLEARABLE_LIST(gQueuedEvents), 0, QUEUEDEVENT_STRIDE - 1);

        // use the stored llDetected* details so we can respond to llDetected* calls.
        gDetectedStack = [];
        gDetectedStack = DESERIALIZE_LIST(CLEARABLE_STR(detected));

        gInvokingHandler = TRUE;
        SEND_IPC(IPCTYPE_INVOKE_HANDLER, CLEARABLE_STR(args), ip);
    }
}

default {
    state_entry() {
        if (!gInitialized) {
            SEND_IPC(IPCTYPE_MANAGER_RESTARTED, "", "");
            loadNotecard();
            gInitialized = TRUE;
        } else {
            // coming back from the state switch, send the queued events.
            LSL_ASSERT(gInvokingHandler);
            gInvokingHandler = FALSE;
            sendQueuedEvent();
        }
    }

    link_message(integer sender_num, integer num, string str, key id) {
        if (num >= IPCTYPE_MAX || num <= IPCTYPE_MIN) {
            // This isn't a link message internal to us, we can forward it to the interpreter
            invokeEventHandler(EH_LINK_MESSAGE, [sender_num, num, CLEARABLE_STR(str), id], 0);
            return;
        }

        if (num == IPCTYPE_REQUEST_CODE) {
            if (gCodeLines == []) {
                llOwnerSay("No code, sorry!");
                return;
            }
            if (gLoadState) {
                llOwnerSay("Received code request while still in load state " + (string)gLoadState);
                LSL_ASSERT(0);
                return;
            }
            // only one thing should ever request code at a time, anything else
            // is a logic error. There's only one VM!
            if (gNotecardRequestID) {
                LSL_ASSERT(0);
                return;
            }

            ++gCodeRequestNum;

            integer requested_ip = (integer)((string)id);
            integer i;
            integer len = llGetListLength(gCodeLines);
            integer last_valid_line = -1;
            integer last_valid_ip = -1;
            integer last_valid_idx = -1;
            for(i=0; i<len; i += CODEINDEX_STRIDE) {
                integer ip = llList2Integer(gCodeLines, i + CODEINDEX_IP);
                if (requested_ip < ip)
                    jump found_bigger;
                last_valid_ip = ip;
                last_valid_line = llList2Integer(gCodeLines, i + CODEINDEX_NC_AND_LINE);
                last_valid_idx = i;
            }
            @found_bigger;
            if (last_valid_line == -1) {
                llOwnerSay("Requested invalid IP " + (string)requested_ip);
                return;
            }

            // Check to see if we have the code in our cache so we don't have to eat
            // the cost of a forced llGetNotecardLine() sleep.
            for(i=0; i<NUM_CACHED_CODES; i += CACHEDCODE_STRIDE) {
                if (llList2Integer(gCachedCode, i + CACHEDCODE_NC_AND_LINE) == last_valid_line) {
                    // mark the code as having been read from the LRU cache
                    gCachedCode = llListReplaceList(
                        CLEARABLE_LIST(gCachedCode),
                        [gCodeRequestNum],
                        i + CACHEDCODE_LAST_USED,
                        i + CACHEDCODE_LAST_USED
                    );

                    // send off the code
                    string code_line = llList2String(gCachedCode, i + CACHEDCODE_CODE);
                    SEND_IPC(IPCTYPE_REQUEST_CODE_REPLY, code_line, last_valid_ip);

                    sortCachedCode();
                    return;
                }
            }

            gFetchingIP = last_valid_ip;
            gFetchingNCAndLine = last_valid_line;
            gLoadState = LOADSTATE_CODE;

            // figure out which notecard number this belongs to, and what line the code
            // should be on within that notecard
            integer notecard_num = (last_valid_line >> 16) & 0xFFff;
            integer line_num = last_valid_line & 0xFFff;
            string notecard_name = "script";
            if (notecard_num)
                // notecards after the first script notecard get a suffix
                notecard_name += (string)notecard_num;
            else
                // the first notecard has header lines that need to be skipped
                line_num += gHeaderLines;
            gNotecardRequestID = llGetNotecardLine(notecard_name, line_num);
        } else if (num == IPCTYPE_HANDLER_FINISHED) {
            // script finished a handler
            gInvokingHandler = FALSE;
            sendQueuedEvent();
        } else if (num == IPCTYPE_CHANGE_STATE) {
            // this should only happen mid-execution of a handler
            LSL_ASSERT(gInvokingHandler);

            // changing states kills queued events
            gQueuedEvents = [];

            // these should stay queued for now, we'll send them when
            // we return back to the default state so there's no race
            // condition with replies from the interpreter.
            invokeEventHandler(EH_STATE_EXIT, [], 0);
            gScriptState = (integer)((string)id);
            invokeEventHandler(EH_STATE_ENTRY, [], 0);

            // We need to mimic the side-effects of state changing (dropping listens, etc.) Actually change
            // state, then come back immediately.
            state dump_events;
        } else if (num == IPCTYPE_CALL_LIB) {
            // Some functions need special handling and can't be passed straight through to a "real" call.
            integer lib_num = (integer)((string)id);
            integer no_wait = lib_num & ~0xFFff;
            lib_num = lib_num & 0xFFff;
            if (llListFindList(SPECIAL_FUNCTIONS, (list)lib_num) == -1) {
                // this one is handled by a library script though
                return;
            }

            integer det_func_offset;
            list args = DESERIALIZE_LIST(CLEARABLE_STR(str));
            list ret;
            integer ret_type = LIBFUNCRET_NONE;
            if (lib_num == LIBFUNC_LLDIE || lib_num == LIBFUNC_LLRESETSCRIPT) {
                // Die doesn't die, just resets this script.
                llResetScript();
            }

// auto-generated wrappers for functions that must be executed from the manager script
#           include "generated/manager_funcs.inc.lsl"

            else if ((det_func_offset = llListFindList(DETECTED_FUNC_OFFSETS, (list)lib_num)) != -1) {
                ret_type = LIBFUNCRET_SIMPLE;
                // figure out where this function's data lives on the detected stack
                integer offset = (llList2Integer(args, 0) * DETECTENTRY_STRIDE) + det_func_offset;
                if (offset >= llGetListLength(gDetectedStack)) {
                    // past the end of the detected events!
                    // Get the default value for the expected default type
                    integer default_type = llList2Integer(DETECTED_FUNC_TYPES, det_func_offset);
                    ret = getDetectedDefault(default_type);
                } else {
                    ret = llList2List(gDetectedStack, offset, offset);
                    // keys are actually compressed on the detected stack, decompress them.
                    if (llGetListEntryType(ret, 0) == TYPE_KEY)
                        ret = (list)uncompress_key(llList2String(CLEARABLE_LIST(ret), 0));
                }
            } else {
                // This is a special function, shouldn't we have handled it?
                LSL_ASSERT(0);
            }
            args = [];

            if (!no_wait) {
                string ret_str = "";
                if (ret_type != LIBFUNCRET_NONE)
                    ret_str = SERIALIZE_LIST(CLEARABLE_LIST(ret));

                SEND_IPC(IPCTYPE_CALL_LIB_REPLY, CLEARABLE_STR(ret_str), ret_type);
            }
        }
    }

    changed(integer change) {
        if (change & CHANGED_INVENTORY) {
            key new_notecard_id = llGetInventoryKey("script");
            if (new_notecard_id != gNotecardInventoryID) {
                llOwnerSay("Script notecard change detected, restarting!");
                llResetScript();
            }
        }
        invokeEventHandler(EH_CHANGED, [change], 0);
    }

    dataserver(key queryid, string data) {
        if (queryid != gNotecardRequestID) {
            invokeEventHandler(EH_DATASERVER, [CLEARABLE_STR(data)], 0);
            return;
        }
        gNotecardRequestID = NULL_KEY;
        LSL_ASSERT(gLoadState != LOADSTATE_NONE);

        if (data == EOF) {
            if (gLoadState != LOADSTATE_CODE) {
                llOwnerSay("Early end of script notecard???");
                LSL_ASSERT(0);
                gCodeLines = [];
                gEventHandlers = [];
            }
            gLoadState = LOADSTATE_NONE;
            return;
        }

        if (gLoadState == LOADSTATE_HANDLERS) {
            gEventHandlers = llJson2List(CLEARABLE_STR(data));
            gLoadState = LOADSTATE_LINES;
            gNotecardRequestID = llGetNotecardLine("script", ++gNotecardLine);
            ++gHeaderLines;
        } else if (gLoadState == LOADSTATE_LINES) {
            // We're done loading for now, might ask to read a specific line later.
            gCodeLines = llJson2List(CLEARABLE_STR(data));
            gLoadState = LOADSTATE_NONE;
            SEND_IPC(IPCTYPE_SCRIPT_LOADED, "", "");
            // invoke the entrypoint
            gInvokingHandler = TRUE;
            SEND_IPC(IPCTYPE_INVOKE_HANDLER, "", "0");
            invokeEventHandler(EH_STATE_ENTRY, [], 0);
            ++gHeaderLines;
        } else if (gLoadState == LOADSTATE_CODE) {
            gLoadState = LOADSTATE_NONE;
            // replace the cache entry at the end since it's the least recently used.
            gCachedCode = llListReplaceList(
                CLEARABLE_LIST(gCachedCode),
                [gCodeRequestNum, gFetchingNCAndLine, data],
                -CACHEDCODE_STRIDE,
                -1
            );
            sortCachedCode();

            SEND_IPC(IPCTYPE_REQUEST_CODE_REPLY, data, gFetchingIP);
        }
    }

    touch_start(integer num_detected) {
        invokeEventHandler(EH_TOUCH_START, [num_detected], num_detected);
    }

    touch(integer num_detected) {
        invokeEventHandler(EH_TOUCH, [num_detected], num_detected);
    }

    touch_end(integer num_detected) {
        invokeEventHandler(EH_TOUCH_END, [num_detected], num_detected);
    }

    listen(integer channel, string name, key id, string msg) {
        invokeEventHandler(EH_LISTEN, [channel, name, id, CLEARABLE_STR(msg)], 0);
    }

    on_rez(integer start_param) {
        invokeEventHandler(EH_ON_REZ, [start_param], 0);
    }

    timer() {
        // timer() won't re-queue if there's already a queued event. need to check
        // to see if we already have one queued.
        integer i;
        integer len = llGetListLength(gQueuedEvents);
        integer expected_eh = EVENT_FOR_STATE(EH_TIMER);
        for (; i<len; i += QUEUEDEVENT_STRIDE) {
            if (llList2Integer(gQueuedEvents, i + QUEUEDEVENT_STATE_AND_EVENT) == expected_eh) {
                return;
            }
        }
        invokeEventHandler(EH_TIMER, [], 0);
    }

    http_response(key request_id, integer status, list metadata, string body) {
        invokeEventHandler(
            EH_HTTP_RESPONSE,
            [request_id, status, SERIALIZE_LIST(CLEARABLE_LIST(metadata)), CLEARABLE_STR(body)],
            0
        );
    }

    http_request(key id, string method, string body) {
        invokeEventHandler(EH_HTTP_REQUEST, [id, method, CLEARABLE_STR(body)], 0);
    }

    run_time_permissions(integer perm) {
        invokeEventHandler(EH_RUN_TIME_PERMISSIONS, [perm], 0);
    }
}

state dump_events {
    state_entry() {
        state default;
    }
}
