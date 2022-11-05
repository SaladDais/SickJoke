#include "generated/constants.lsli"
#include "include/macros.lsli"
#include "include/typed_json.lsli"

// we assume that the code list can have typed literals, within reason.
// notably, list literals and key literals may not be present.
list gCode;
integer gCodeSize = 0;

// base instruction pointer, points to start of gCode in global indices
integer gIPB = 0;
// instruction pointer, relative to start of gCode
integer gIP = 0;
integer gCodeFetchNeeded;
// base pointer, where the locals start
// function parameters are negative relative to this.
integer gBP = 0;
integer gSP = 0;
integer gFault = 0;
integer gInvokingHandler = 0;
integer gYielded = 0;
integer gIgnoreYields;
integer gExpectingCallLibReply;

list gStack = [];
list gGlobals = [];


resetVMState() {
    gCode = [];
    gCodeSize = 0;
    gStack = [];
    gGlobals = [];
    gIP = 0;
    gIPB = 0;
    gBP = 0;
    gSP = 0;
    gFault = 0;
    gYielded = 0;
    gCodeFetchNeeded = TRUE;
    gInvokingHandler = FALSE;
    gExpectingCallLibReply = FALSE;
}


popStack(integer start, integer end) {
    gStack = llDeleteSubList(CLEARABLE_LIST(gStack), start, end);
}

// This is kind of a hack to deal with deferred pops where we still need
// to save memory immediately by making something GCable.
// Might make sense to remove later.
tombstoneStack(integer idx) {
    gStack = llListReplaceList(CLEARABLE_LIST(gStack), [0], idx, idx);
}

checkCodeFetchNeeded() {
    gCodeFetchNeeded = gIP < 0 || gIP >= gCodeSize;
}

pushOp(integer lsl_type, integer whence, integer index) {
    // Abuse single-element `list` as a boxed object.
    list what;

    if (whence == WHENCE_LOCAL) {
        integer local_ptr = gBP + index;
        what = llList2List(gStack, local_ptr, local_ptr);
    } else if (whence == WHENCE_ARG) {
        // gBP points to the first local, before that is the registers
        // that the caller pushed. Just above those is the arguments and
        // just above _those_ is the retval. Technically we could address
        // these with a negative WHENCE_LOCAL, but this is a bit nicer.
        // Note that a index of 0 will point at the LAST argument.
        integer local_ptr = gBP - (index + 1 + CALL_REGISTERS_LEN);
        what = llList2List(gStack, local_ptr, local_ptr);
    } else if (whence == WHENCE_GLOBAL) {
        LSL_ASSERT(index >= 0 && index < llGetListLength(gGlobals));
        what = llList2List(gGlobals, index, index);
    } else if (whence == WHENCE_CONST) {
        if (index) {
            // if index & 1 when pushing a constant we know we don't have to
            // look at the next instruction for the constant value.
            if (lsl_type == LSLTYPE_INTEGER) {
                // Allow specifying small signed integer values inline in index
                what = [index >> 1];
            } else {
                // no other value makes sense for other types
                LSL_ASSERT(index == 1);
                what = getDefault(lsl_type, TRUE);
            }
        } else {
            // no index provided for const, look for one in the code at gIP
            LSL_ASSERT(index == 0);
            // pushing constants is a little special because things that would normally
            // have correct types may just be strings, and won't be pulled out correctly
            // if we do `llList2*Type*()`. These do NOT benefit from automatic casting from
            // string that normally happens when the list access function is called.
            if (lsl_type == LSLTYPE_ROTATION) {
                what = [(rotation)llList2String(gCode, gIP)];
            } else if (lsl_type == LSLTYPE_VECTOR) {
                what = [(vector)llList2String(gCode, gIP)];
            } else if (lsl_type == LSLTYPE_FLOAT) {
                // float constant may be a string like "infinity", JSON has no way to represent
                // inf or nan natively.
                what = [llList2Float(gCode, gIP)];
            } else if (lsl_type == LSLTYPE_STRING) {
                // strip workaround padding for https://jira.secondlife.com/browse/BUG-227035
                string str_val = llList2String(gCode, gIP);
                integer str_len = llStringLength(str_val);
                if (str_len < 3) {
                    // too short to be anything other than empty string. just treat
                    // it as empty string.
                    what = [""];
                } else {
                    what = [llGetSubString(str_val, 1, -2)];
                }
                str_val = "";
            } else {
                // we expect the thing to already be typed correctly (there are no key constants!)
                // We can just slice off a bit of the list without casting.
                what = llList2List(gCode, gIP, gIP);
            }
            ++gIP;
        }
    } else {
        LSL_ASSERT(0);
    }

    gStack += what;
}

storeOp(integer opcode, integer lsl_type, integer whence, integer index) {
    list what;
    if (opcode == OPCODE_STORE) {
        what = llList2List(gStack, -1, -1);
        popStack(-1, -1);
    } else if (opcode == OPCODE_STORE_DEFAULT) {
        what = getDefault(lsl_type, TRUE);
    }

    if (whence == WHENCE_LOCAL || whence == WHENCE_ARG) {
        integer local_ptr;
        if (whence == WHENCE_LOCAL)
            local_ptr = gBP + index;
        else
            local_ptr = gBP - (index + 1 + CALL_REGISTERS_LEN);
        gStack = llListReplaceList(CLEARABLE_LIST(gStack), CLEARABLE_LIST(what), local_ptr, local_ptr);
    } else if (whence == WHENCE_GLOBAL) {
        gGlobals = llListReplaceList(CLEARABLE_LIST(gGlobals), CLEARABLE_LIST(what), index, index);
    } else {
        LSL_ASSERT(0);
    }
}

jumpOp(integer jump_type, integer jump_target) {
    integer should_jump = TRUE;
    if (jump_type == JUMPTYPE_ALWAYS) {
        // no check
    } else {
        should_jump = llList2Integer(gStack, -1);
        popStack(-1, -1);
        if (jump_type == JUMPTYPE_NIF)
            should_jump = !should_jump;
    }

    if (should_jump) {
        gIP += jump_target;
    }
}

callOp(integer call_type, integer call_target) {
    // If there are any arguments, they should be on the stack
    // underneath the retval slot. Once the CALL has been completed
    // the stack should look something like:
    //   [ret_slot, arg1, arg2, arg3, IP, BP, SP]
    // note that the caller MUST explicitly make space for the retval
    // and POP_N off all of the arguments on return!

    // Push registers, IP must be pushed in absolute form
    // since IPB may change
    gStack += [gIP + gIPB, gBP, gSP];
    gBP = llGetListLength(gStack);
    gSP = gBP;

    if (call_type == CALLTYPE_RELATIVE) {
        gIP += call_target;
    } else if (call_type == CALLTYPE_ABSOLUTE) {
        // we're using this to set gIP, which is relative to
        // gIPB. modify call_target such that it will result
        // in jumping to the absolute addr.
        gIP = call_target - gIPB;
    } else {
        LSL_ASSERT(0);
    }
}

callLibOp(integer num_args, integer lib_num, integer no_wait) {
    // We need to pop our args first since there won't be a
    // RET to do it for us.
    list args;
    if (num_args) {
        integer pop_start = num_args * -1;
        // args should have been pushed from left to right
        // so things should be in natural order already:
        // rightmost arg at top of stack.
        args = llList2List(gStack, pop_start, -1);
        popStack(pop_start, -1);
    }

    // Use non-yielding mode for void lib calls when no_wait is true. so long
    // as order of execution is maintained we don't really care.
    // Just because we've yielded doesn't mean that something else can kick off
    // another handler function, gInvokingHandler needs to be false for that!
    if (!no_wait) {
        // not really needed now, but might help if we add
        // async / await.
        gStack += [gIP + gIPB, gBP, gSP];
        gBP = llGetListLength(gStack);
        gSP = gBP;

        gYielded = 1;
        gExpectingCallLibReply = TRUE;
    }
    SEND_IPC(IPCTYPE_CALL_LIB, SERIALIZE_LIST(CLEARABLE_LIST(args)), (lib_num | (no_wait << 16)));
}

retOp(integer args_to_pop) {
    // blow away all the locals, can't use -1 as end index
    // here or it kills the whole list :/
    integer stack_len = llGetListLength(gStack);
    gStack = llDeleteSubList(CLEARABLE_LIST(gStack), gBP, stack_len);
    integer next_ip = -1;
    if (gStack) {
        // restore the original stack frame
        gSP = llList2Integer(gStack, -1);
        gBP = llList2Integer(gStack, -2);
        // make stored absolute IP relative to current IPB
        next_ip = llList2Integer(gStack, -3);
        gIP = next_ip - gIPB;
        // Pop registers. Only thing left on stack related to
        // the original CALL will be a retval and args if the function
        // had them.
        popStack(-(CALL_REGISTERS_LEN + args_to_pop), -1);
    }
    // absolute next IP was -1, that means we're done here.
    if (next_ip == -1) {
        // stack is empty, return control.
        gIP = 0;
        gYielded = 1;
        if (gInvokingHandler) {
            // Tell the manager we're ready for another event if it has one
            SEND_IPC(IPCTYPE_HANDLER_FINISHED, "", "");
        }
        gInvokingHandler = FALSE;
    } else {
        // we're still executing, check if we need to fetch code
        // for the next instruction.
        checkCodeFetchNeeded();
    }
}

yieldOp(integer stack_to_yield) {
    if (gIgnoreYields) {
        integer i;
        for(i; i<stack_to_yield; ++i) {
            llSay(0, "Yielded " + llList2String(gStack, -1));
            popStack(-1, -1);
        }
    } else {
        // tell the embedder they need to pop this many
        gYielded = stack_to_yield + 1;
        return;
    }
}


lslAssert(integer val) {
    if (!val) {
        print("I messed up at " + (string)(gIPB + gIP - 1));
        llOwnerSay((string)(0.0/0.0));
    }
}


binOp(integer op, integer l_type, integer r_type) {
    if (l_type == LSLTYPE_INTEGER && r_type == LSLTYPE_INTEGER) {
        // this would be a poor choice in LSL because of the
        // cleanup code that must be splatted out on RET, but it's
        // fine in Mono.
        integerIntegerOperation(op);
        return;
    } else if (l_type == LSLTYPE_FLOAT && r_type == LSLTYPE_FLOAT) {
        floatFloatOperation(op);
        return;
    } else if (l_type == LSLTYPE_LIST) {
        listAnyOperation(op, r_type);
        return;
    } else if (r_type == LSLTYPE_LIST) {
        anyListOperation(op, l_type);
        return;
    } else if (l_type == LSLTYPE_STRING || l_type == LSLTYPE_KEY) {
        // assumes only (string or key)<->(string or key) ops
        LSL_ASSERT(r_type == LSLTYPE_STRING || r_type == LSLTYPE_KEY);
        stringStringOperation(op);
        return;
    } else if (l_type == LSLTYPE_VECTOR) {
        vectorOperation(op, r_type);
        return;
    } else if (l_type == LSLTYPE_ROTATION) {
        LSL_ASSERT(r_type == LSLTYPE_ROTATION);
        rotationRotationOperation(op);
        return;
    }
    LSL_ASSERT(0);
}

integerIntegerOperation(integer op) {
    integer l = llList2Integer(gStack, -1);
    integer r = llList2Integer(gStack, -2);
    integer res;
    if (op == OPERATION_PLUS) {
        res = l + r;
    } else if (op == OPERATION_MINUS) {
        res = l - r;
    } else if (op == OPERATION_MUL) {
        res = l * r;
    } else if (op == OPERATION_DIV) {
        res = l / r;
    } else if (op == OPERATION_MOD) {
        res = l % r;
    } else if (op == OPERATION_EQ) {
        res = l == r;
    } else if (op == OPERATION_NEQ) {
        res = l != r;
    } else if (op == OPERATION_GREATER) {
        res = l > r;
    } else if (op == OPERATION_LESS) {
        res = l < r;
    } else if (op == OPERATION_GEQ) {
        res = l >= r;
    } else if (op == OPERATION_LEQ) {
        res = l <= r;
    } else if (op == OPERATION_BOOLEAN_AND) {
        res = l && r;
    } else if (op == OPERATION_BOOLEAN_OR) {
        res = l || r;
    } else if (op == OPERATION_BIT_OR) {
        res = l | r;
    } else if (op == OPERATION_BIT_AND) {
        res = l & r;
    } else if (op == OPERATION_BIT_XOR) {
        res = l ^ r;
    } else if (op == OPERATION_SHIFT_LEFT) {
        res = l << r;
    } else if (op == OPERATION_SHIFT_RIGHT) {
        res = l >> r;
    } else {
        LSL_ASSERT(0);
    }

    gStack += res;
}

floatFloatOperation(integer op) {
    float l = llList2Float(gStack, -1);
    float r = llList2Float(gStack, -2);
    list what;
    if (op == OPERATION_PLUS) {
        what = [l + r];
    } else if (op == OPERATION_MINUS) {
        what = [l - r];
    } else if (op == OPERATION_MUL) {
        what = [l * r];
    } else if (op == OPERATION_DIV) {
        what = [l / r];
    } else if (op == OPERATION_EQ) {
        what = [l == r];
    } else if (op == OPERATION_NEQ) {
        what = [l != r];
    } else if (op == OPERATION_GREATER) {
        what = [l > r];
    } else if (op == OPERATION_LESS) {
        what = [l < r];
    } else if (op == OPERATION_GEQ) {
        what = [l >= r];
    } else if (op == OPERATION_LEQ) {
        what = [l <= r];
    } else {
        LSL_ASSERT(0);
    }

    gStack += what;
}

stringStringOperation(integer op) {
    string l = llList2String(gStack, -1);
    string r = llList2String(gStack, -2);

    if (op == OPERATION_EQ || op == OPERATION_NEQ) {
        integer eq = l == r;
        if (op == OPERATION_NEQ)
            eq = !eq;
        gStack += eq;
    } else if (op == OPERATION_PLUS) {
        gStack += CLEARABLE_STR(l) + CLEARABLE_STR(r);
    } else {
        LSL_ASSERT(0);
    }
}

vectorOperation(integer op, integer r_type) {
    // LSL technically allows the order of some of these to be swapped.
    // we don't allow that to save bytecode size. If you need swapped
    // order like float * vector you'll have to use the SWAP bytecode
    // after pushing the operands.
    vector l = llList2Vector(gStack, -1);
    if (r_type == LSLTYPE_FLOAT) {
        float r = llList2Float(gStack, -2);
        if (op == OPERATION_MUL) {
            gStack += l * r;
        } else if (op == OPERATION_DIV) {
            gStack += l / r;
        } else {
            LSL_ASSERT(0);
        }
    } else if (r_type == LSLTYPE_VECTOR) {
        vector r = llList2Vector(gStack, -2);
        if (op == OPERATION_MUL) {
            gStack += l * r;
        } else if (op == OPERATION_MINUS) {
            gStack += l - r;
        } else if (op == OPERATION_PLUS) {
            gStack += l + r;
        } else if (op == OPERATION_MOD) {
            gStack += l % r;
        } else if (op == OPERATION_EQ || op == OPERATION_NEQ) {
            integer val = l == r;
            if (op == OPERATION_NEQ)
                val = !val;
            gStack += val;
            return;
        } else {
            LSL_ASSERT(0);
        }
    } else if (r_type == LSLTYPE_ROTATION) {
        rotation r = llList2Rot(gStack, -2);
        if (op == OPERATION_MUL) {
            gStack += l * r;
        } else if (op == OPERATION_DIV) {
            gStack += l / r;
        } else {
            LSL_ASSERT(0);
        }
    } else {
        LSL_ASSERT(0);
    }
}

rotationRotationOperation(integer op) {
    // see above notes about rotation * vector
    rotation l = llList2Rot(gStack, -1);
    rotation r = llList2Rot(gStack, -2);
    rotation ret;

    if (op == OPERATION_MUL) {
        ret = l * r;
    } else if (op == OPERATION_DIV) {
        ret = l / r;
    } else if (op == OPERATION_MINUS) {
        ret = l - r;
    } else if (op == OPERATION_PLUS) {
        ret = l + r;
    } else if (op == OPERATION_EQ || op == OPERATION_NEQ) {
        integer val = l == r;
        if (op == OPERATION_NEQ)
            val = !val;
        gStack += val;
        return;
    } else {
        LSL_ASSERT(0);
    }
    gStack += ret;
}

listAnyOperation(integer op, integer r_type) {
    string l_str = llList2String(gStack, -1);
    // make sure we're not holding onto a strong reference
    // to l_str anymore, it should be immediately GC-able,
    // but leave the slot on the stack
    tombstoneStack(-1);
    list l = DESERIALIZE_LIST(CLEARABLE_STR(l_str));

    list r;
    if (r_type == LSLTYPE_LIST) {
        string r_str = llList2String(gStack, -2);
        tombstoneStack(-2);
        r = DESERIALIZE_LIST(CLEARABLE_STR(r_str));
    } else {
        r = llList2List(gStack, -2, -2);
        tombstoneStack(-2);
    }

    if (op == OPERATION_PLUS) {
        gStack += SERIALIZE_LIST(CLEARABLE_LIST(l) + CLEARABLE_LIST(r));
        return;
    }

    LSL_ASSERT(r_type == LSLTYPE_LIST);

    if (op == OPERATION_EQ || op == OPERATION_NEQ) {
        // NEQ really gets length difference between two lists,
        // and EQ is implemented as `!(len(l) - len(r))`
        integer val = CLEARABLE_LIST(l) != CLEARABLE_LIST(r);
        if (op == OPERATION_EQ)
            val = !val;
        gStack += val;
        return;
    }
    LSL_ASSERT(0);
}

anyListOperation(integer op, integer l_type) {
    LSL_ASSERT(op == OPERATION_PLUS);
    string r_str = llList2String(gStack, -2);
    tombstoneStack(-2);
    list r = DESERIALIZE_LIST(CLEARABLE_STR(r_str));
    list l = llList2List(gStack, -1, -1);
    tombstoneStack(-1);
    gStack += SERIALIZE_LIST(CLEARABLE_LIST(l) + CLEARABLE_LIST(r));
}

unOp(integer op, integer un_type) {
    if (un_type == LSLTYPE_INTEGER) {
        integer l = llList2Integer(gStack, -1);
        integer res;
        if (op == OPERATION_MINUS) {
            res = -l;
        } else if (op == OPERATION_BIT_NOT) {
            res = ~l;
        } else if (op == OPERATION_BOOLEAN_NOT) {
            res = !l;
        } else {
            LSL_ASSERT(0);
        }
        gStack += res;
        return;
    } else if (un_type == LSLTYPE_FLOAT) {
        if (op == OPERATION_MINUS) {
            gStack += -llList2Float(gStack, -1);
            return;
        }
    } else if (un_type == LSLTYPE_VECTOR) {
        if (op == OPERATION_MINUS) {
            gStack += -llList2Vector(gStack, -1);
            return;
        }
    } else if (un_type == LSLTYPE_ROTATION) {
        if (op == OPERATION_MINUS) {
            gStack += -llList2Rot(gStack, -1);
            return;
        }
    }
    LSL_ASSERT(0);
}

castOp(integer from_type, integer to_type) {
    // This function assumes that no-op cast cases have been compiled away!

    if (to_type == LSLTYPE_LIST) {
        // take one item off the stack and put it in a new list
        buildListOp(1);
        return;
    }

    // These data types actually behave differently when casting to string
    // vs using llList2String, handle them specifically since we know they
    // can only be cast to string at this point.
    if (from_type == LSLTYPE_VECTOR) {
        LSL_ASSERT(to_type == LSLTYPE_STRING);
        gStack += (string)llList2Vector(gStack, -1);
        popStack(-2, -2);
        return;
    } else if (from_type == LSLTYPE_ROTATION) {
        LSL_ASSERT(to_type == LSLTYPE_STRING);
        gStack += (string)llList2Rot(gStack, -1);
        popStack(-2, -2);
        return;
    }

    // This is ok and doesn't cause precision loss (and might actually
    // lead to _increased_ precision!) The only valid casts for floating
    // point types is to string, or integer in the float case. Basically,
    // we're either going to do a float<->str conversion we would have done
    // anyway, or we're converting from float->int, in which case decimal
    // truncation doesn't matter since that `floor()`s.
    string val = llList2String(gStack, -1);
    popStack(-1, -1);
    if (from_type == LSLTYPE_LIST) {
        // list can only be cast to list or string, cast to list
        // is obviously a no-op that shouldn't happen.
        LSL_ASSERT(to_type == LSLTYPE_STRING);
        gStack += (string)DESERIALIZE_LIST(CLEARABLE_STR(val));
        return;
    }

    list what;
    if (to_type == LSLTYPE_INTEGER) {
        what = [(integer)val];
    } else if (to_type == LSLTYPE_FLOAT) {
        what = [(float)val];
    } else if (to_type == LSLTYPE_STRING) {
        what = [val];
    } else if (to_type == LSLTYPE_KEY) {
        what = [(key)val];
    } else if (to_type == LSLTYPE_VECTOR) {
        what = [(vector)val];
    } else if (to_type == LSLTYPE_ROTATION) {
        what = [(rotation)val];
    } else {
        LSL_ASSERT(0);
    }
    gStack += CLEARABLE_LIST(what);
}

list getDefault(integer lsl_type, integer for_initialize) {
    if (lsl_type == LSLTYPE_INTEGER)
        return [0];
    if (lsl_type == LSLTYPE_STRING)
        return [""];
    else if (lsl_type == LSLTYPE_FLOAT)
        return [0.0];
    else if (lsl_type == LSLTYPE_KEY)
        return [(key)""];
    else if (lsl_type == LSLTYPE_VECTOR)
        return [ZERO_VECTOR];
    else if (lsl_type == LSLTYPE_ROTATION) {
        // rotation has weird assymetry between its value at allocation time
        // and the value a initialization time. Try something like:
        //
        // jump foo;  // jump over the initializer
        // rotation baz;
        // @foo;
        // if (baz)
        //     llOwnerSay("Truthy!");
        // else
        //     llOwnerSay("Falsey!");
        //
        // it's truthy by default because it's <0,0,0,0>, which
        // is _not_ ZERO_ROTATION. Yuck.
        if (for_initialize)
            return [ZERO_ROTATION];
        else
            return [<0, 0, 0, 0>];
    }
    else if (lsl_type == LSLTYPE_LIST)
        // NOTE: actually SERIALIZE_LIST([])
        return ["[]"];
    LSL_ASSERT(0);
    return [];
}

allocSlotsOp(integer whence) {
    string types_str = llList2String(gCode, gIP);
    ++gIP;
    integer types_len = llStringLength(types_str);
    integer i;

    list defaults;
    for (i=0; i<types_len; ++i) {
        string char = llGetSubString(types_str, i, i);
        // no way to jump over initializer in a global, so we always choose
        // initialization-time rather than alloc-time defaults in that case.
        defaults += getDefault((integer)char, whence == WHENCE_GLOBAL);
    }

    if (whence == WHENCE_LOCAL) {
        // usually only used at head of a function
        gStack += CLEARABLE_LIST(defaults);
        // increment SP, can tell how many locals we have by doing gSP - gBP.
        gSP += types_len;
    } else if (whence == WHENCE_GLOBAL) {
        // only used at head of _start
        gGlobals += CLEARABLE_LIST(defaults);
    } else {
        LSL_ASSERT(0);
    }
}

swapOp() {
    // swap the order of the top two stack elements
    list top = llList2List(gStack, -1, -1);
    list under = llList2List(gStack, -2, -2);
    popStack(-2, -1);
    gStack += top + under;
}

boolOp(integer type) {
    integer bool_res;
    string stack_val = llList2String(gStack, -1);
    popStack(-1, -1);
    if (type == LSLTYPE_INTEGER || type == LSLTYPE_FLOAT) {
        if ((float)stack_val) bool_res = TRUE;
    } else if (type == LSLTYPE_VECTOR) {
        if ((vector)stack_val) bool_res = TRUE;
    } else if (type == LSLTYPE_ROTATION) {
        if ((rotation)stack_val) bool_res = TRUE;
    } else if (type == LSLTYPE_KEY) {
        if ((key)stack_val) bool_res = TRUE;
    } else if (type == LSLTYPE_STRING) {
        bool_res = CLEARABLE_STR(stack_val) != "";
    } else if (type == LSLTYPE_LIST) {
        // NOTE: have to change this if list serialization format changes!
        // actually SERIALIZE_LIST([]) !
        bool_res = stack_val != "[]";
    }
    gStack += bool_res;
}

takeMemberOp(integer type, integer idx) {
    float val;
    if (type == LSLTYPE_VECTOR) {
        vector v = llList2Vector(gStack, -1);
        if (idx == 0) val = v.x;
        else if (idx == 1) val = v.y;
        else val = v.z;
    } else {
        rotation r = llList2Rot(gStack, -1);
        if (idx == 0) val = r.x;
        else if (idx == 1) val = r.y;
        else if (idx == 2) val = r.z;
        else val = r.s;
    }
    popStack(-1, -1);
    gStack += val;
}

replaceMemberOp(integer type, integer idx) {
    float val = llList2Float(gStack, -2);
    if (type == LSLTYPE_VECTOR) {
        vector v = llList2Vector(gStack, -1);
        if (idx == 0) v.x = val;
        else if (idx == 1) v.y = val;
        else v.z = val;

        gStack += v;
    } else {
        rotation r = llList2Rot(gStack, -1);
        if (idx == 0) r.x = val;
        else if (idx == 1) r.y = val;
        else if (idx == 2) r.z = val;
        else r.s = val;

        gStack += r;
    }
    // pop the original args
    popStack(-3, -2);
}


buildCoordOp(integer type) {
    list what;
    integer to_pop = 3;
    if (type == LSLTYPE_VECTOR) {
        what = (list)<
            llList2Float(gStack, -3),
            llList2Float(gStack, -2),
            llList2Float(gStack, -1)
        >;
    } else if (type == LSLTYPE_ROTATION) {
        to_pop = 4;
        what = (list)<
            llList2Float(gStack, -4),
            llList2Float(gStack, -3),
            llList2Float(gStack, -2),
            llList2Float(gStack, -1)
        >;
    }
    popStack(-1 * to_pop, -1);
    gStack += what;
}

buildListOp(integer num_elems) {
    list val = [];
    while (num_elems--) {
        // Prepend element and pop. Remember, lists are pushed left to right!
        val = llList2List(gStack, -1, -1) + CLEARABLE_LIST(val);
        popStack(-1, -1);
    }
    gStack += SERIALIZE_LIST(CLEARABLE_LIST(val));
}

changeStateOp(integer state_num) {
    // changing state fully unwinds the stack and yields to the manager,
    // allowing it to kick off the state_exit() and state_entry() handlers.
    gStack = [];
    gBP = 0;
    gIP = 0;
    gSP = 0;
    gYielded = TRUE;
    gInvokingHandler = FALSE;
    SEND_IPC(IPCTYPE_CHANGE_STATE, "", state_num);
}

interpreterLoop() {
    gYielded = 0;
    while (!gCodeFetchNeeded && !gFault && !gYielded) {
        // we have to eat the cost of a 32-bit int, anyway, use any high bits
        // for arguments for the opcode. Putting args in the high bits has
        // the benefit that the string form of opcodes with fewer args will be
        // shorter.
        integer read = llList2Integer(gCode, gIP);
        integer op = read & ~(-1 << OPCODE_WIDTH);
        integer args = read >> OPCODE_WIDTH;

        ++gIP;

        if (op == OPCODE_NO_OP) {
            ;
        } else if (op == OPCODE_BIN_OP) {
            binOp(args & 0xFF, (args >> 8) & 0xFF, (args >> 16) & 0xFF);
            // belatedly pop the two operands
            popStack(-3, -2);
        } else if (op == OPCODE_UN_OP) {
            unOp(args & 0xFF, (args >> 8) & 0xFF);
            popStack(-2, -2);
        } else if (op == OPCODE_PUSH) {
            // what type to push (5 bits)
            // which storage to push from (3 bits)
            // index to push from (16 bits signed)
            pushOp(args & 0xF, (args >> 5) & 0x3, args >> 8);
        } else if (op == OPCODE_STORE || op == OPCODE_STORE_DEFAULT) {
            // what type to store (5 bits)
            // which storage to store to (3 bits)
            // index to store to (16 bits signed)
            storeOp(op, args & 0xF, (args >> 5) & 0x3, args >> 8);
        } else if (op == OPCODE_DUMP) {
#ifdef DEBUG
            print(llList2String(gStack, -1));
#else
            llSay(0, llList2String(gStack, -1));
#endif
            popStack(-1, -1);
        } else if (op == OPCODE_DUP) {
            gStack += llList2List(gStack, -1, -1);
        } else if (op == OPCODE_POP_N) {
            popStack(-1 * args, -1);
        } else if (op == OPCODE_CAST) {
            castOp(args & 0xFF, (args >> 8) & 0xFF);
        } else if (op == OPCODE_BOOL) {
            boolOp(args);
        } else if (op == OPCODE_ALLOC_SLOTS) {
            allocSlotsOp(args & 0xFF);
        } else if (op == OPCODE_JUMP) {
            // we want the sign extension behaviour on args here,
            // the jump target is signed!
            jumpOp(args & 0x3, args >> 3);
        } else if (op == OPCODE_CALL) {
            callOp(args & 0x3, args >> 3);
        } else if (op == OPCODE_CALL_LIB) {
            callLibOp(args & 0x0F, (args >> 4) & 0xFFf, args >> 16);
        } else if (op == OPCODE_RET) {
            retOp(args);
        } else if (op == OPCODE_SWAP) {
            swapOp();
        } else if (op == OPCODE_BUILD_LIST){
            buildListOp(args);
        } else if (op == OPCODE_BUILD_COORD) {
            buildCoordOp(args & 0xFF);
        } else if (op == OPCODE_YIELD) {
            yieldOp(args);
        } else if (op == OPCODE_TAKE_MEMBER) {
            takeMemberOp(args & 0xFF, (args >> 8) & 0xFF);
        } else if (op == OPCODE_REPLACE_MEMBER) {
            replaceMemberOp(args & 0xFF, (args >> 8) & 0xFF);
        } else if (op == OPCODE_CHANGE_STATE) {
            changeStateOp(args & 0xFF);
        } else {
            LSL_ASSERT(0);
        }

        // Check if we ran off the end of the code line
        checkCodeFetchNeeded();
    }

    if (gCodeFetchNeeded) {
        // request the code starting at the current absolute IP
        SEND_IPC(IPCTYPE_REQUEST_CODE, "", gIPB + gIP);
    }
}

handleCodeReload(integer new_ipb) {
    gCodeSize = llGetListLength(gCode);

    // make existing IP relative to the new IP base pointer
    gIP -= new_ipb - gIPB;
    gIPB = new_ipb;
    checkCodeFetchNeeded();
    // now that we've relocated our IP should be in bounds
    LSL_ASSERT(!gCodeFetchNeeded);
}

default {
    state_entry() {
        gIgnoreYields = TRUE;
        resetVMState();
    }

    link_message(integer link_num, integer num, string str, key id) {
        if (num >= IPCTYPE_MAX || num <= IPCTYPE_MIN)
            return;
        
        if (num == IPCTYPE_REQUEST_CODE_REPLY) {
            gCode = [];
            gCode = llJson2List(CLEARABLE_STR(str));

            // recalculate the IP relative to the new code section
            handleCodeReload((integer)((string)id));

            // we have the code we were waiting on, re-enter the interpretation loop
            if (!gExpectingCallLibReply)
                interpreterLoop();
        } else if (num == IPCTYPE_CALL_LIB_REPLY) {
#ifdef DEBUG
            if (!gExpectingCallLibReply) {
                llOwnerSay("Received unsolicited call lib response?");
                return;
            }
#endif
            gExpectingCallLibReply = FALSE;
            // pop registers, arguments aren't on the stack at this point so they
            // don't need to be popped
            retOp(0);
            integer retval_type = (integer)((string)id);

            // When doing a library call there's no empty pushed onto the stack, so
            // we don't have to pop or replace the empty.
            if (retval_type == LIBFUNCRET_NONE) {
                // do nothing
                LSL_ASSERT(str == "");
            } else if (retval_type == LIBFUNCRET_SIMPLE) {
                // should be a single-element list, can't return tuples!
                gStack += DESERIALIZE_LIST(CLEARABLE_STR(str));
            } else if (retval_type == LIBFUNCRET_LIST) {
                // string-serialized list, push as-is.
                gStack += CLEARABLE_STR(str);
            } else {
                LSL_ASSERT(0);
            }

            // we can re-enter the interpretation loop since we have
            // the reply the call_lib opcode was waiting on.
            if (!gCodeFetchNeeded)
                interpreterLoop();
        } else if (num == IPCTYPE_MANAGER_RESTARTED) {
            llResetScript();
        } else if (num == IPCTYPE_SCRIPT_LOADED) {
            resetVMState();
        } else if (num == IPCTYPE_INVOKE_HANDLER) {
            // Manager should know better than to ask us to execute an event
            // handler while we're still in the middle of a previous one.
            LSL_ASSERT(!gInvokingHandler);

            gInvokingHandler = TRUE;
            gStack += DESERIALIZE_LIST(CLEARABLE_STR(str));
            // set absolute IP to -1 so RET knows that this is the
            // "top" level function frame and to yield on RET.
            gIP = -(gIPB + 1);
            callOp(CALLTYPE_ABSOLUTE, (integer)((string)id));
            // This would normally happen at the end of the interpreter loop,
            // need to force this check now.
            checkCodeFetchNeeded();
            interpreterLoop();
        }
    }
}
