from lummao import *


class Script(BaseLSLScript):
    LIBFUNC_LLDETECTEDKEY: int
    LIBFUNC_LLDETECTEDOWNER: int
    LSLTYPE_KEY: int
    SPECIAL_FUNCTIONS: list
    gCodeLines: list
    gEventHandlers: list
    gCachedCode: list
    gLoadState: int
    gNotecardInventoryID: Key
    gCodeRequestNum: int
    gNotecardRequestID: Key
    gNotecardLine: int
    gHeaderLines: int
    gFetchingIP: int
    gFetchingNCAndLine: int
    gScriptState: int
    gInvokingHandler: int
    gQueuedEvents: list
    gDetectedStack: list
    gInitialized: int

    def __init__(self):
        super().__init__()
        self.LIBFUNC_LLDETECTEDKEY = 47
        self.LIBFUNC_LLDETECTEDOWNER = 50
        self.LSLTYPE_KEY = 3
        self.SPECIAL_FUNCTIONS = [12, 13, 20, 21, 26, 38, 44, 47, 50, 62, 83, 86, 90, 91, 160, 161, 198, 210, 260, 261, 262, 266, 275, 277, 281, 310, 326, 332, 336, 337, 338, 339, 349, 369, 373, 416, 429, 433, 435, 437, 438, 447, 453, 459]
        self.gCodeLines = []
        self.gEventHandlers = []
        self.gCachedCode = []
        self.gLoadState = 0
        self.gNotecardInventoryID = typecast("00000000-0000-0000-0000-000000000000", Key)
        self.gCodeRequestNum = 0
        self.gNotecardRequestID = Key("")
        self.gNotecardLine = 0
        self.gHeaderLines = 0
        self.gFetchingIP = 0
        self.gFetchingNCAndLine = 0
        self.gScriptState = 0
        self.gInvokingHandler = 0
        self.gQueuedEvents = []
        self.gDetectedStack = []
        self.gInitialized = 0

    async def JSONTypeDump(self, _val: list) -> str:
        _i: int = 0
        _len: int = rneq([], _val)
        while True == True:
            if not cond(rless(_len, _i)):
                break
            _tag: str = typecast(await self.builtin_funcs.llGetListEntryType(_val, _i), str)
            _str_val: list = typecast(radd(_tag, radd(await self.builtin_funcs.llList2String(_val, _i), _tag)), list)
            _val = await self.builtin_funcs.llListReplaceList(radd(_val, ((_val := []))), _str_val, _i, _i)
            _i += 1
        return await self.builtin_funcs.llList2Json("﷒", radd(_val, ((_val := []))))

    async def JSONTypeParse(self, _str: str) -> list:
        _val: list = await self.builtin_funcs.llJson2List(radd(_str, ((_str := ""))))
        _i: int = 0
        _len: int = rneq([], _val)
        while True == True:
            if not cond(rless(_len, _i)):
                break
            _new: list = []
            _str_val: str = await self.builtin_funcs.llList2String(_val, _i)
            _type: int = typecast(await self.builtin_funcs.llGetSubString(_str_val, 0, 0), int)
            _str_len: int = await self.builtin_funcs.llStringLength(_str_val)
            if cond(rless(3, _str_len)):
                _str_val = ""
            else:
                _str_val = await self.builtin_funcs.llGetSubString(_str_val, 1, (typecast(-2, int)))
            if cond(boolnot(bitnot(neg(_type)))):
                _new = typecast(typecast(_str_val, int), list)
            elif cond(req(2, _type)):
                _new = typecast(typecast(_str_val, float), list)
            elif cond(req(3, _type)):
                _new = typecast(_str_val, list)
            elif cond(req(5, _type)):
                _new = typecast(typecast(_str_val, Vector), list)
            elif cond(req(6, _type)):
                _new = typecast(typecast(_str_val, Quaternion), list)
            elif cond(req(4, _type)):
                _new = typecast(typecast(_str_val, Key), list)
            _str_val = ""
            _val = await self.builtin_funcs.llListReplaceList(radd(_val, ((_val := []))), _new, _i, _i)
            _i += 1
        return _val

    async def str_replace(self, _subject: str, _search: str, _replace: str) -> str:
        return await self.builtin_funcs.llDumpList2String(await self.builtin_funcs.llParseStringKeepNulls(_subject, typecast(_search, list), []), _replace)

    async def compress_key(self, _k: Key) -> str:
        if cond(_k):
            pass
        elif cond(req("00000000-0000-0000-0000-000000000000", _k)):
            return ""
        else:
            return radd(typecast(_k, str), "-")
        _s: str = await self.builtin_funcs.llToLower(radd("0", await self.str_replace(typecast(_k, str), "-", "")))
        _ret: str = ""
        _i: int = 0
        _A: str = ""
        _B: str = ""
        _C: str = ""
        _D: str = ""
        _i = 0
        while True == True:
            if not cond(rless(32, _i)):
                break
            _A = await self.builtin_funcs.llGetSubString(_s, _i, _i)
            _i += 1
            _B = await self.builtin_funcs.llGetSubString(_s, _i, _i)
            _i += 1
            _C = await self.builtin_funcs.llGetSubString(_s, _i, _i)
            _i += 1
            _D = "b"
            if cond(req("0", _A)):
                _A = "e"
                _D = "8"
            elif cond(req("d", _A)):
                _A = "e"
                _D = "9"
            elif cond(req("f", _A)):
                _A = "e"
                _D = "a"
            _ret = radd((radd(_C, radd("%b", radd(_B, radd(_D, radd("%", radd(_A, "%e"))))))), _ret)
        return await self.builtin_funcs.llUnescapeURL(_ret)

    async def pad_dash(self, _s: str) -> str:
        return radd(await self.builtin_funcs.llGetSubString(_s, 20, 31), radd("-", radd(await self.builtin_funcs.llGetSubString(_s, 16, 19), radd("-", radd(await self.builtin_funcs.llGetSubString(_s, 12, 15), radd("-", radd(await self.builtin_funcs.llGetSubString(_s, 8, 11), radd("-", await self.builtin_funcs.llGetSubString(_s, 0, 7)))))))))

    async def uncompress_key(self, _s: str) -> Key:
        if cond(req("-", await self.builtin_funcs.llGetSubString(_s, 0, 0))):
            return typecast(await self.builtin_funcs.llGetSubString(_s, 1, 2147483647), Key)
        elif cond(req("", _s)):
            return typecast("00000000-0000-0000-0000-000000000000", Key)
        _i: int = 0
        _ret: str = ""
        _A: str = ""
        _B: str = ""
        _C: str = ""
        _D: str = ""
        _s = await self.builtin_funcs.llToLower(await self.builtin_funcs.llEscapeURL(_s))
        _i = 0
        while True == True:
            if not cond(rless(99, _i)):
                break
            _A = await self.builtin_funcs.llGetSubString(_s, neg(bitnot(neg(bitnot(_i)))), neg(bitnot(neg(bitnot(_i)))))
            _B = await self.builtin_funcs.llGetSubString(_s, radd(_i, 5), radd(_i, 5))
            _C = await self.builtin_funcs.llGetSubString(_s, radd(_i, 8), radd(_i, 8))
            _D = await self.builtin_funcs.llGetSubString(_s, radd(_i, 4), radd(_i, 4))
            if cond(req("8", _D)):
                _A = "0"
            elif cond(req("9", _D)):
                _A = "d"
            elif cond(req("a", _D)):
                _A = "f"
            _ret = radd(_C, radd(_B, radd(_A, _ret)))
            _i = radd(_i, 9)
        return typecast(await self.pad_dash(_ret), Key)

    async def lslAssert(self, _val: int) -> None:
        if cond(boolnot(_val)):
            await self.builtin_funcs.llOwnerSay("Assertion failed!")
            await self.builtin_funcs.llOwnerSay(typecast(rdiv((0.0), (0.0)), str))

    async def loadNotecard(self) -> None:
        self.gScriptState = 0
        self.gCodeRequestNum = 0
        self.gNotecardLine = 0
        self.gHeaderLines = 0
        self.gCachedCode = []
        self.gCodeLines = []
        self.gLoadState = 0
        self.gNotecardInventoryID = await self.builtin_funcs.llGetInventoryKey("script")
        if cond(req("00000000-0000-0000-0000-000000000000", self.gNotecardInventoryID)):
            await self.builtin_funcs.llOwnerSay("Couldn't find script notecard!")
            return
        _i: int = 0
        _j: int = 0
        _i = 0
        while True == True:
            if not cond(rless(15, _i)):
                break
            _j = 0
            while True == True:
                if not cond(rless(3, _j)):
                    break
                self.gCachedCode = radd((typecast(-2147483647, int)), self.gCachedCode)
                _j += 1
            _i += 1
        self.gLoadState = 1
        self.gNotecardRequestID = await self.builtin_funcs.llGetNotecardLine("script", 0)

    async def sortCachedCode(self) -> None:
        self.gCachedCode = await self.builtin_funcs.llListSort(radd(self.gCachedCode, (assign(self.__dict__, "gCachedCode", []))), 3, 0)

    async def getHandlerIP(self, _state_and_event: int) -> int:
        _i: int = 0
        _len: int = rneq([], self.gEventHandlers)
        while True == True:
            if not cond(rless(_len, _i)):
                break
            if cond(req(await self.builtin_funcs.llList2Integer(self.gEventHandlers, _i), _state_and_event)):
                return await self.builtin_funcs.llList2Integer(self.gEventHandlers, neg(bitnot(_i)))
            _i = neg(bitnot(neg(bitnot(_i))))
        return (typecast(-1, int))

    async def invokeEventHandler(self, _eh_type: int, _args: list, _num_detected: int) -> None:
        _state_and_event: int = rbitor(_eh_type, rmul(65536, self.gScriptState))
        _ip: int = await self.getHandlerIP(_state_and_event)
        if cond(boolnot(bitnot(_ip))):
            return
        _serialized_event: str = await self.JSONTypeDump(radd(_args, ((_args := []))))
        _i: int = 0
        _detected: list = []
        while True == True:
            if not cond(rless(_num_detected, _i)):
                break
            _detected = radd([typecast(await self.compress_key(await self.builtin_funcs.llDetectedKey(_i)), Key), typecast(await self.compress_key(await self.builtin_funcs.llDetectedOwner(_i)), Key)], _detected)
            _i += 1
        if cond(self.gInvokingHandler):
            if cond(rless((rneq([], self.gQueuedEvents)), 19)):
                await self.builtin_funcs.llOwnerSay("Oops, dropping event on the floor due to queue overflow!")
                return
            _serialized_detected: str = await self.JSONTypeDump(radd(_detected, ((_detected := []))))
            self.gQueuedEvents = radd(_serialized_detected, radd(_serialized_event, radd(_ip, radd(_state_and_event, self.gQueuedEvents))))
        else:
            self.gInvokingHandler = 1
            self.gDetectedStack = radd(_detected, ((_detected := [])))
            await self.builtin_funcs.llMessageLinked((typecast(-4, int)), 61953, _serialized_event, typecast(typecast(_ip, str), Key))

    async def getDetectedDefault(self, _lsl_type: int) -> list:
        if cond(boolnot(_lsl_type)):
            return typecast(0, list)
        if cond(req(2, _lsl_type)):
            return typecast("", list)
        elif cond(boolnot(bitnot(neg(_lsl_type)))):
            return typecast(0.0, list)
        elif cond(req(self.LSLTYPE_KEY, _lsl_type)):
            return typecast(typecast("00000000-0000-0000-0000-000000000000", Key), list)
        elif cond(req(4, _lsl_type)):
            return typecast(Vector(((0.0), (0.0), (0.0))), list)
        elif cond(req(5, _lsl_type)):
            return typecast(Quaternion(((0.0), (0.0), (0.0), (0.0))), list)
        else:
            await self.lslAssert(0)
        return typecast("", list)

    async def sendQueuedEvent(self) -> None:
        await self.lslAssert(boolnot(self.gInvokingHandler))
        if cond(rneq([], self.gQueuedEvents)):
            _ip: int = await self.builtin_funcs.llList2Integer(self.gQueuedEvents, 1)
            _args: str = await self.builtin_funcs.llList2String(self.gQueuedEvents, 2)
            _detected: str = await self.builtin_funcs.llList2String(self.gQueuedEvents, 3)
            self.gQueuedEvents = await self.builtin_funcs.llDeleteSubList(radd(self.gQueuedEvents, (assign(self.__dict__, "gQueuedEvents", []))), 0, 3)
            self.gDetectedStack = []
            self.gDetectedStack = await self.JSONTypeParse(radd(_detected, ((_detected := ""))))
            self.gInvokingHandler = 1
            await self.builtin_funcs.llMessageLinked((typecast(-4, int)), 61953, radd(_args, ((_args := ""))), typecast(typecast(_ip, str), Key))

    async def edefaultstate_entry(self) -> None:
        if cond(boolnot(self.gInitialized)):
            await self.builtin_funcs.llMessageLinked((typecast(-4, int)), 61957, "", (typecast("", Key)))
            await self.loadNotecard()
            self.gInitialized = 1
        else:
            await self.lslAssert(self.gInvokingHandler)
            self.gInvokingHandler = 0
            await self.sendQueuedEvent()

    @with_goto
    async def edefaultlink_message(self, _sender_num: int, _num: int, _str: str, _id: Key) -> None:
        if cond(boolnot((rbitand(rless(_num, 61950), rless(61960, _num))))):
            await self.invokeEventHandler(17, [_sender_num, _num, radd(_str, ((_str := ""))), _id], 0)
            if True == True:
                return
        if cond(req(61955, _num)):
            if cond(req([], self.gCodeLines)):
                await self.builtin_funcs.llOwnerSay("No code, sorry!")
                if True == True:
                    return
            if cond(self.gLoadState):
                await self.builtin_funcs.llOwnerSay(radd(typecast(self.gLoadState, str), "Received code request while still in load state "))
                await self.lslAssert(0)
                if True == True:
                    return
            if cond(self.gNotecardRequestID):
                await self.lslAssert(0)
                if True == True:
                    return
            self.gCodeRequestNum += 1
            _requested_ip: int = typecast(typecast(_id, str), int)
            _i: int = 0
            _len: int = rneq([], self.gCodeLines)
            _last_valid_line: int = (typecast(-1, int))
            _last_valid_ip: int = (typecast(-1, int))
            _i = 0
            while True == True:
                if not cond(rless(_len, _i)):
                    break
                _ip: int = await self.builtin_funcs.llList2Integer(self.gCodeLines, _i)
                if cond(rless(_ip, _requested_ip)):
                    goto ._found_bigger
                _last_valid_ip = _ip
                _last_valid_line = await self.builtin_funcs.llList2Integer(self.gCodeLines, neg(bitnot(_i)))
                _i = neg(bitnot(neg(bitnot(_i))))
            label ._found_bigger
            if cond(boolnot(bitnot(_last_valid_line))):
                await self.builtin_funcs.llOwnerSay(radd(typecast(_requested_ip, str), "Requested invalid IP "))
                if True == True:
                    return
            _i = 0
            while True == True:
                if not cond(rless(45, _i)):
                    break
                if cond(req(_last_valid_line, await self.builtin_funcs.llList2Integer(self.gCachedCode, neg(bitnot(_i))))):
                    self.gCachedCode = await self.builtin_funcs.llListReplaceList(radd(self.gCachedCode, (assign(self.__dict__, "gCachedCode", []))), typecast(self.gCodeRequestNum, list), _i, _i)
                    _code_line: str = await self.builtin_funcs.llList2String(self.gCachedCode, neg(bitnot(neg(bitnot(_i)))))
                    await self.builtin_funcs.llMessageLinked((typecast(-4, int)), 61956, _code_line, typecast(typecast(_last_valid_ip, str), Key))
                    await self.sortCachedCode()
                    if True == True:
                        return
                _i = radd(_i, 3)
            self.gFetchingIP = _last_valid_ip
            self.gFetchingNCAndLine = _last_valid_line
            self.gLoadState = 3
            _notecard_num: int = rbitand(65535, rshr(16, _last_valid_line))
            _line_num: int = rbitand(65535, _last_valid_line)
            _notecard_name: str = "script"
            if cond(_notecard_num):
                _notecard_name = radd(typecast(_notecard_num, str), _notecard_name)
            else:
                _line_num = radd(self.gHeaderLines, _line_num)
            self.gNotecardRequestID = await self.builtin_funcs.llGetNotecardLine(_notecard_name, _line_num)
        elif cond(req(61954, _num)):
            self.gInvokingHandler = 0
            await self.sendQueuedEvent()
        elif cond(req(61959, _num)):
            await self.lslAssert(self.gInvokingHandler)
            self.gQueuedEvents = []
            await self.invokeEventHandler(33, [], 0)
            self.gScriptState = typecast(typecast(_id, str), int)
            await self.invokeEventHandler(32, [], 0)
            raise StateChangeException('dump_events')
        elif cond(req(61951, _num)):
            _lib_num: int = typecast(typecast(_id, str), int)
            _no_wait: int = rbitand((typecast(-65536, int)), _lib_num)
            _lib_num = rbitand(65535, _lib_num)
            if cond(boolnot(bitnot(await self.builtin_funcs.llListFindList(self.SPECIAL_FUNCTIONS, typecast(_lib_num, list))))):
                if True == True:
                    return
            _det_func_offset: int = 0
            _args: list = await self.JSONTypeParse(radd(_str, ((_str := ""))))
            _ret: list = []
            _ret_type: int = 0
            if cond(rbitor(req(336, _lib_num), req(62, _lib_num))):
                await self.builtin_funcs.llResetScript()
            elif cond(req(12, _lib_num)):
                await self.builtin_funcs.llAttachToAvatar(await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 0))
            elif cond(req(13, _lib_num)):
                await self.builtin_funcs.llAttachToAvatarTemp(await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 0))
            elif cond(req(20, _lib_num)):
                await self.builtin_funcs.llBreakAllLinks()
            elif cond(req(21, _lib_num)):
                await self.builtin_funcs.llBreakLink(await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 0))
            elif cond(req(26, _lib_num)):
                await self.builtin_funcs.llClearCameraParams()
            elif cond(req(38, _lib_num)):
                await self.builtin_funcs.llCreateLink(await self.builtin_funcs.llList2Key(_args, 0), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 1))
            elif cond(req(44, _lib_num)):
                await self.builtin_funcs.llDetachFromAvatar()
            elif cond(req(83, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetAndResetTime(), list)
                _ret_type = 1
            elif cond(req(86, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetAnimationOverride(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(90, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetCameraPos(), list)
                _ret_type = 1
            elif cond(req(91, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetCameraRot(), list)
                _ret_type = 1
            elif cond(req(160, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetPermissions(), list)
                _ret_type = 1
            elif cond(req(161, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetPermissionsKey(), list)
                _ret_type = 1
            elif cond(req(198, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetTime(), list)
                _ret_type = 1
            elif cond(req(210, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGiveMoney(await self.builtin_funcs.llList2Key(_args, 0), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 1)), list)
                _ret_type = 1
            elif cond(req(260, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llListen(await self.builtin_funcs.llList2Integer(_args, 0), await self.builtin_funcs.llList2String(_args, 1), await self.builtin_funcs.llList2Key(_args, 2), await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 3)), list)
                _ret_type = 1
            elif cond(req(261, _lib_num)):
                await self.builtin_funcs.llListenControl(await self.builtin_funcs.llList2Integer(_args, 0), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 1))
            elif cond(req(262, _lib_num)):
                await self.builtin_funcs.llListenRemove(await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 0))
            elif cond(req(266, _lib_num)):
                await self.builtin_funcs.llLookAt(await self.builtin_funcs.llList2Vector(_args, 0), await self.builtin_funcs.llList2Float(_args, 1), await self.builtin_funcs.llList2Float(radd(_args, ((_args := []))), 2))
            elif cond(req(275, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llManageEstateAccess(await self.builtin_funcs.llList2Integer(_args, 0), await self.builtin_funcs.llList2Key(radd(_args, ((_args := []))), 1)), list)
                _ret_type = 1
            elif cond(req(277, _lib_num)):
                await self.builtin_funcs.llMessageLinked(await self.builtin_funcs.llList2Integer(_args, 0), await self.builtin_funcs.llList2Integer(_args, 1), await self.builtin_funcs.llList2String(_args, 2), await self.builtin_funcs.llList2Key(radd(_args, ((_args := []))), 3))
            elif cond(req(281, _lib_num)):
                await self.builtin_funcs.llMoveToTarget(await self.builtin_funcs.llList2Vector(_args, 0), await self.builtin_funcs.llList2Float(radd(_args, ((_args := []))), 1))
            elif cond(req(310, _lib_num)):
                await self.builtin_funcs.llReleaseControls()
            elif cond(req(326, _lib_num)):
                await self.builtin_funcs.llRequestPermissions(await self.builtin_funcs.llList2Key(_args, 0), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 1))
            elif cond(req(332, _lib_num)):
                await self.builtin_funcs.llResetAnimationOverride(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0))
            elif cond(req(337, _lib_num)):
                await self.builtin_funcs.llResetTime()
            elif cond(req(338, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llReturnObjectsByID(await self.JSONTypeParse(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0))), list)
                _ret_type = 1
            elif cond(req(339, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llReturnObjectsByOwner(await self.builtin_funcs.llList2Key(_args, 0), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 1)), list)
                _ret_type = 1
            elif cond(req(349, _lib_num)):
                await self.builtin_funcs.llRotLookAt(await self.builtin_funcs.llList2Rot(_args, 0), await self.builtin_funcs.llList2Float(_args, 1), await self.builtin_funcs.llList2Float(radd(_args, ((_args := []))), 2))
            elif cond(req(369, _lib_num)):
                await self.builtin_funcs.llSetAnimationOverride(await self.builtin_funcs.llList2String(_args, 0), await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 1))
            elif cond(req(373, _lib_num)):
                await self.builtin_funcs.llSetCameraParams(await self.JSONTypeParse(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0)))
            elif cond(req(416, _lib_num)):
                await self.builtin_funcs.llSetTimerEvent(await self.builtin_funcs.llList2Float(radd(_args, ((_args := []))), 0))
            elif cond(req(429, _lib_num)):
                await self.builtin_funcs.llSleep(await self.builtin_funcs.llList2Float(radd(_args, ((_args := []))), 0))
            elif cond(req(433, _lib_num)):
                await self.builtin_funcs.llStartAnimation(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0))
            elif cond(req(435, _lib_num)):
                await self.builtin_funcs.llStopAnimation(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0))
            elif cond(req(437, _lib_num)):
                await self.builtin_funcs.llStopLookAt()
            elif cond(req(438, _lib_num)):
                await self.builtin_funcs.llStopMoveToTarget()
            elif cond(req(447, _lib_num)):
                await self.builtin_funcs.llTakeControls(await self.builtin_funcs.llList2Integer(_args, 0), await self.builtin_funcs.llList2Integer(_args, 1), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 2))
            elif cond(req(453, _lib_num)):
                await self.builtin_funcs.llTeleportAgent(await self.builtin_funcs.llList2Key(_args, 0), await self.builtin_funcs.llList2String(_args, 1), await self.builtin_funcs.llList2Vector(_args, 2), await self.builtin_funcs.llList2Vector(radd(_args, ((_args := []))), 3))
            elif cond(req(459, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llTransferLindenDollars(await self.builtin_funcs.llList2Key(_args, 0), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 1)), list)
                _ret_type = 1
            elif cond(bitnot(((_det_func_offset := await self.builtin_funcs.llListFindList(radd(50, typecast(47, list)), typecast(_lib_num, list)))))):
                _ret_type = 1
                _offset: int = radd(_det_func_offset, rmul(2, await self.builtin_funcs.llList2Integer(_args, 0)))
                if cond(boolnot((rless((rneq([], self.gDetectedStack)), _offset)))):
                    _default_type: int = await self.builtin_funcs.llList2Integer(radd(3, typecast(3, list)), _det_func_offset)
                    _ret = await self.getDetectedDefault(_default_type)
                else:
                    _ret = await self.builtin_funcs.llList2List(self.gDetectedStack, _offset, _offset)
                    if cond(req(4, await self.builtin_funcs.llGetListEntryType(_ret, 0))):
                        _ret = typecast(await self.uncompress_key(await self.builtin_funcs.llList2String(radd(_ret, ((_ret := []))), 0)), list)
            else:
                await self.lslAssert(0)
            _args = []
            if cond(boolnot(_no_wait)):
                _ret_str: str = ""
                if cond(_ret_type):
                    _ret_str = await self.JSONTypeDump(radd(_ret, ((_ret := []))))
                await self.builtin_funcs.llMessageLinked((typecast(-4, int)), 61952, radd(_ret_str, ((_ret_str := ""))), typecast(typecast(_ret_type, str), Key))

    async def edefaultchanged(self, _change: int) -> None:
        if cond(rbitand(1, _change)):
            _new_notecard_id: Key = await self.builtin_funcs.llGetInventoryKey("script")
            if cond(boolnot((req(self.gNotecardInventoryID, _new_notecard_id)))):
                await self.builtin_funcs.llOwnerSay("Script notecard change detected, restarting!")
                await self.builtin_funcs.llResetScript()
        await self.invokeEventHandler(3, typecast(_change, list), 0)

    async def edefaultdataserver(self, _queryid: Key, _data: str) -> None:
        if cond(boolnot((req(self.gNotecardRequestID, _queryid)))):
            await self.invokeEventHandler(8, typecast(radd(_data, ((_data := ""))), list), 0)
            return
        self.gNotecardRequestID = typecast("00000000-0000-0000-0000-000000000000", Key)
        await self.lslAssert(boolnot(boolnot(self.gLoadState)))
        if cond(req("\n\n\n", _data)):
            if cond(rbitxor(3, self.gLoadState)):
                await self.builtin_funcs.llOwnerSay("Early end of script notecard???")
                await self.lslAssert(0)
                self.gCodeLines = []
                self.gEventHandlers = []
            self.gLoadState = 0
            return
        if cond(boolnot(bitnot(neg(self.gLoadState)))):
            self.gEventHandlers = await self.builtin_funcs.llJson2List(radd(_data, ((_data := ""))))
            self.gLoadState = 2
            self.gNotecardRequestID = await self.builtin_funcs.llGetNotecardLine("script", preincr(self.__dict__, "gNotecardLine"))
            self.gHeaderLines += 1
        elif cond(req(2, self.gLoadState)):
            self.gCodeLines = await self.builtin_funcs.llJson2List(radd(_data, ((_data := ""))))
            self.gLoadState = 0
            await self.builtin_funcs.llMessageLinked((typecast(-4, int)), 61958, "", (typecast("", Key)))
            self.gInvokingHandler = 1
            await self.builtin_funcs.llMessageLinked((typecast(-4, int)), 61953, "", (typecast("0", Key)))
            await self.invokeEventHandler(32, [], 0)
            self.gHeaderLines += 1
        elif cond(req(3, self.gLoadState)):
            self.gLoadState = 0
            self.gCachedCode = await self.builtin_funcs.llListReplaceList(radd(self.gCachedCode, (assign(self.__dict__, "gCachedCode", []))), radd(_data, radd(self.gFetchingNCAndLine, typecast(self.gCodeRequestNum, list))), (typecast(-3, int)), (typecast(-1, int)))
            await self.sortCachedCode()
            await self.builtin_funcs.llMessageLinked((typecast(-4, int)), 61956, _data, typecast(typecast(self.gFetchingIP, str), Key))

    async def edefaulttouch_start(self, _num_detected: int) -> None:
        await self.invokeEventHandler(37, typecast(_num_detected, list), _num_detected)

    async def edefaulttouch(self, _num_detected: int) -> None:
        await self.invokeEventHandler(35, typecast(_num_detected, list), _num_detected)

    async def edefaulttouch_end(self, _num_detected: int) -> None:
        await self.invokeEventHandler(36, typecast(_num_detected, list), _num_detected)

    async def edefaultlisten(self, _channel: int, _name: str, _id: Key, _msg: str) -> None:
        await self.invokeEventHandler(19, [_channel, _name, _id, radd(_msg, ((_msg := "")))], 0)

    async def edefaulton_rez(self, _start_param: int) -> None:
        await self.invokeEventHandler(27, typecast(_start_param, list), 0)

    async def edefaulttimer(self) -> None:
        _i: int = 0
        _len: int = rneq([], self.gQueuedEvents)
        _expected_eh: int = rbitor(34, rmul(65536, self.gScriptState))
        while True == True:
            if not cond(rless(_len, _i)):
                break
            if cond(req(_expected_eh, await self.builtin_funcs.llList2Integer(self.gQueuedEvents, _i))):
                return
            _i = radd(_i, 4)
        await self.invokeEventHandler(34, [], 0)

    async def edefaulthttp_response(self, _request_id: Key, _status: int, _metadata: list, _body: str) -> None:
        await self.invokeEventHandler(13, [_request_id, _status, await self.JSONTypeDump(radd(_metadata, ((_metadata := [])))), radd(_body, ((_body := "")))], 0)

    async def edefaulthttp_request(self, _id: Key, _method: str, _body: str) -> None:
        await self.invokeEventHandler(12, [_id, _method, radd(_body, ((_body := "")))], 0)

    async def edefaultrun_time_permissions(self, _perm: int) -> None:
        await self.invokeEventHandler(30, typecast(_perm, list), 0)

    async def edump_eventsstate_entry(self) -> None:
        raise StateChangeException('default')

