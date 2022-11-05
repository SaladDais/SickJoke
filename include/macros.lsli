#pragma once

#ifdef DEBUG
#    define LSL_ASSERT(_arg) lslAssert((_arg))
#else
#    define LSL_ASSERT(_arg) ;
#endif

// trick to ensure the old list can be garbage collected immediately
// if we're passing it into a function that will return a mutated copy.
// Relies on LSL's right-to-left expr evaluation order.
#define CLEARABLE_LIST(_list) ((_list = []) + (_list))
#define CLEARABLE_STR(_str) ((_str = "") + (_str))

#define SERIALIZE_LIST(_list) (JSONTypeDump((_list)))
#define DESERIALIZE_LIST(_list) (JSONTypeParse((_list)))

// The optimizer should optimize away any of the casts that weren't actually necessary
#define SEND_IPC(_num, _str1, _str2) llMessageLinked(LINK_THIS, (_num), (string)(_str1), (key)((string)(_str2)))
