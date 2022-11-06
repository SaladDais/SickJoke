#pragma once

// this is a template because we may actually need _two_ library scripts
// due to the 64kb bytecode limit in Mono. Just having all of the function
// calls we need puts us over the limit if we use one script!

#include "generated/constants.inc.lsl"
#include "include/macros.inc.lsl"
#include "include/typed_json.inc.lsl"

lslAssert(integer val) {
    if (!val) {
        llOwnerSay("Assertion failed!");
        llOwnerSay((string)(0.0/0.0));
    }
}

default {
    link_message(integer sender_num, integer num, string str, key id) {
        if (num >= IPCTYPE_MAX || num <= IPCTYPE_MIN)
            return;

        if (num == IPCTYPE_CALL_LIB) {
            integer lib_num = (integer)((string)id);
            integer no_wait = lib_num & ~0xFFff;
            lib_num = lib_num & 0xFFff;

            list args = DESERIALIZE_LIST(CLEARABLE_STR(str));
            list ret;
            integer ret_type = LIBFUNCRET_NONE;

            // give the following "else if"s something to chain off.
            if (FALSE) { ; }
#ifdef INCLUDE_LIBRARY_NUM_0
#           include "generated/library_funcs_0.inc.lsl"
#endif
#ifdef INCLUDE_LIBRARY_NUM_1
#           include "generated/library_funcs_1.inc.lsl"
#endif
#ifdef INCLUDE_LIBRARY_NUM_2
#           include "generated/library_funcs_2.inc.lsl"
#endif
            // might be handled by a different library script.
            else {
                return;
            }
            args = [];

            string ret_str = "";
            if (!no_wait) {
                if (ret_type != LIBFUNCRET_NONE)
                    ret_str = SERIALIZE_LIST(CLEARABLE_LIST(ret));

                SEND_IPC(IPCTYPE_CALL_LIB_REPLY, CLEARABLE_STR(ret_str), ret_type);
            }
        }
    }
}
