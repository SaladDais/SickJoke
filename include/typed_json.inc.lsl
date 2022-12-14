#pragma once
#include "macros.inc.lsl"

// Type-preserving list<->JSON serialization for heterogenous lists. About 2x faster
// than TightListType* examples on LSL wiki.

string JSONTypeDump(list val) {
    integer i;
    integer len = llGetListLength(val);
    for (; i<len; ++i) {
        // both pre and postfix each element with a type tag character so we know what type
        // this field originally was, and so llList2Json doesn't mangle our string by
        // stripping either leading or trailing whitespace :(
        // See https://wiki.secondlife.com/wiki/LlList2Json
        string tag = (string)llGetListEntryType(val, i);
        list str_val = (list)(tag + llList2String(val, i) + tag);
        val = llListReplaceList(CLEARABLE_LIST(val), str_val, i, i);
    }
    return llList2Json(JSON_ARRAY, CLEARABLE_LIST(val));
}

list JSONTypeParse(string str) {
    list val = llJson2List(CLEARABLE_STR(str));
    integer i;
    integer len = llGetListLength(val);
    for (; i<len; ++i) {
        list new;
        // get the type tag and value for the element
        string str_val = llList2String(val, i);
        integer type = (integer)llGetSubString(str_val, 0, 0);

        // LSL ranges are inclusive, so this is the only way we can correctly
        // handle blank strings with both leading and trailing type tags.
        integer str_len = llStringLength(str_val);
        if (str_len < 3) {
            // too short to be anything other than empty string. just treat
            // it as empty string.
            str_val = "";
        } else {
            str_val = llGetSubString(str_val, 1, -2);
        }


        // Cast the element back to its original type
        if (type == TYPE_INTEGER)
            new = (list)((integer)str_val);
        else if (type == TYPE_FLOAT)
            new = (list)((float)str_val);
        else if (type == TYPE_STRING)
            new = (list)str_val;
        else if (type == TYPE_VECTOR)
            new = (list)((vector)str_val);
        else if (type == TYPE_ROTATION)
            new = (list)((rotation)str_val);
        else if (type == TYPE_KEY)
            new = (list)((key)str_val);
        str_val = "";
        val = llListReplaceList(CLEARABLE_LIST(val), new, i, i);
    }
    return val;
}
