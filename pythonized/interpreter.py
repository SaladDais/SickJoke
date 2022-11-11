from lummao import *


class Script(BaseLSLScript):
    gCode: list
    gCodeSize: int
    gIPB: int
    gIP: int
    gCodeFetchNeeded: int
    gBP: int
    gSP: int
    gFault: int
    gInvokingHandler: int
    gYielded: int
    gIgnoreYields: int
    gExpectingCallLibReply: int
    gStack: list
    gGlobals: list

    def __init__(self):
        super().__init__()
        self.gCode = []
        self.gCodeSize = 0
        self.gIPB = 0
        self.gIP = 0
        self.gCodeFetchNeeded = 0
        self.gBP = 0
        self.gSP = 0
        self.gFault = 0
        self.gInvokingHandler = 0
        self.gYielded = 0
        self.gIgnoreYields = 0
        self.gExpectingCallLibReply = 0
        self.gStack = []
        self.gGlobals = []

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

    async def resetVMState(self) -> None:
        self.gCode = []
        self.gCodeSize = 0
        self.gStack = []
        self.gGlobals = []
        self.gIP = 0
        self.gIPB = 0
        self.gBP = 0
        self.gSP = 0
        self.gFault = 0
        self.gYielded = 0
        self.gCodeFetchNeeded = 1
        self.gInvokingHandler = 0
        self.gExpectingCallLibReply = 0

    async def popStack(self, _start: int, _end: int) -> None:
        self.gStack = await self.builtin_funcs.llDeleteSubList(radd(self.gStack, (assign(self.__dict__, "gStack", []))), _start, _end)

    async def tombstoneStack(self, _idx: int) -> None:
        self.gStack = await self.builtin_funcs.llListReplaceList(radd(self.gStack, (assign(self.__dict__, "gStack", []))), typecast(0, list), _idx, _idx)

    async def checkCodeFetchNeeded(self) -> None:
        self.gCodeFetchNeeded = boolnot((rbitand(rless(self.gCodeSize, self.gIP), rless(self.gIP, (typecast(-1, int))))))

    async def pushOp(self, _lsl_type: int, _whence: int, _index: int) -> None:
        _what: list = []
        if cond(boolnot(bitnot(neg(_whence)))):
            _local_ptr: int = radd(_index, self.gBP)
            _what = await self.builtin_funcs.llList2List(self.gStack, _local_ptr, _local_ptr)
        elif cond(req(3, _whence)):
            _local_ptr: int = radd((radd(bitnot(_index), (typecast(-3, int)))), self.gBP)
            _what = await self.builtin_funcs.llList2List(self.gStack, _local_ptr, _local_ptr)
        elif cond(req(2, _whence)):
            await self.lslAssert(boolnot(boolnot((rbitand(rless((rneq([], self.gGlobals)), _index), rless(_index, (typecast(-1, int))))))))
            _what = await self.builtin_funcs.llList2List(self.gGlobals, _index, _index)
        elif cond(boolnot(_whence)):
            if cond(_index):
                if cond(boolnot(_lsl_type)):
                    _what = typecast(rshr(1, _index), list)
                else:
                    await self.lslAssert(boolnot(bitnot(neg(_index))))
                    _what = await self.getDefault(_lsl_type, 1)
            else:
                await self.lslAssert(boolnot(_index))
                if cond(req(5, _lsl_type)):
                    _what = typecast(typecast(await self.builtin_funcs.llList2String(self.gCode, self.gIP), Quaternion), list)
                elif cond(req(4, _lsl_type)):
                    _what = typecast(typecast(await self.builtin_funcs.llList2String(self.gCode, self.gIP), Vector), list)
                elif cond(boolnot(bitnot(neg(_lsl_type)))):
                    _what = typecast(await self.builtin_funcs.llList2Float(self.gCode, self.gIP), list)
                elif cond(req(2, _lsl_type)):
                    _str_val: str = await self.builtin_funcs.llList2String(self.gCode, self.gIP)
                    _str_len: int = await self.builtin_funcs.llStringLength(_str_val)
                    if cond(rless(3, _str_len)):
                        _what = typecast("", list)
                    else:
                        _what = typecast(await self.builtin_funcs.llGetSubString(_str_val, 1, (typecast(-2, int))), list)
                    _str_val = ""
                else:
                    _what = await self.builtin_funcs.llList2List(self.gCode, self.gIP, self.gIP)
                self.gIP += 1
        else:
            await self.lslAssert(0)
        self.gStack = radd(_what, self.gStack)

    async def storeOp(self, _opcode: int, _lsl_type: int, _whence: int, _index: int) -> None:
        _what: list = []
        if cond(req(8, _opcode)):
            _what = await self.builtin_funcs.llList2List(self.gStack, (typecast(-1, int)), (typecast(-1, int)))
            await self.popStack((typecast(-1, int)), (typecast(-1, int)))
        elif cond(req(9, _opcode)):
            _what = await self.getDefault(_lsl_type, 1)
        if cond(rbitor(req(3, _whence), boolnot(bitnot(neg(_whence))))):
            _local_ptr: int = 0
            if cond(boolnot(bitnot(neg(_whence)))):
                _local_ptr = radd(_index, self.gBP)
            else:
                _local_ptr = radd((radd(bitnot(_index), (typecast(-3, int)))), self.gBP)
            self.gStack = await self.builtin_funcs.llListReplaceList(radd(self.gStack, (assign(self.__dict__, "gStack", []))), radd(_what, ((_what := []))), _local_ptr, _local_ptr)
        elif cond(req(2, _whence)):
            self.gGlobals = await self.builtin_funcs.llListReplaceList(radd(self.gGlobals, (assign(self.__dict__, "gGlobals", []))), radd(_what, ((_what := []))), _index, _index)
        else:
            await self.lslAssert(0)

    async def jumpOp(self, _jump_type: int, _jump_target: int) -> None:
        _should_jump: int = 1
        if cond(_jump_type):
            _should_jump = await self.builtin_funcs.llList2Integer(self.gStack, (typecast(-1, int)))
            await self.popStack((typecast(-1, int)), (typecast(-1, int)))
            if cond(req(2, _jump_type)):
                _should_jump = boolnot(_should_jump)
        if cond(_should_jump):
            self.gIP = radd(_jump_target, self.gIP)

    async def callOp(self, _call_type: int, _call_target: int) -> None:
        self.gStack = radd(self.gSP, radd(self.gBP, radd((radd(self.gIPB, self.gIP)), self.gStack)))
        self.gBP = rneq([], self.gStack)
        self.gSP = self.gBP
        if cond(boolnot(_call_type)):
            self.gIP = radd(_call_target, self.gIP)
        elif cond(boolnot(bitnot(neg(_call_type)))):
            self.gIP = radd(neg(self.gIPB), _call_target)
        else:
            await self.lslAssert(0)

    async def callLibOp(self, _num_args: int, _lib_num: int, _no_wait: int) -> None:
        _args: list = []
        if cond(_num_args):
            _pop_start: int = neg(_num_args)
            _args = await self.builtin_funcs.llList2List(self.gStack, _pop_start, (typecast(-1, int)))
            await self.popStack(_pop_start, (typecast(-1, int)))
        if cond(boolnot(_no_wait)):
            self.gStack = radd(self.gSP, radd(self.gBP, radd((radd(self.gIPB, self.gIP)), self.gStack)))
            self.gBP = rneq([], self.gStack)
            self.gSP = self.gBP
            self.gYielded = 1
            self.gExpectingCallLibReply = 1
        await self.builtin_funcs.llMessageLinked((typecast(-4, int)), 61951, await self.JSONTypeDump(radd(_args, ((_args := [])))), typecast(typecast(rbitor(rmul(65536, _no_wait), _lib_num), str), Key))

    async def retOp(self, _args_to_pop: int) -> None:
        _stack_len: int = rneq([], self.gStack)
        self.gStack = await self.builtin_funcs.llDeleteSubList(radd(self.gStack, (assign(self.__dict__, "gStack", []))), self.gBP, _stack_len)
        _next_ip: int = (typecast(-1, int))
        if cond(rneq([], self.gStack)):
            self.gSP = await self.builtin_funcs.llList2Integer(self.gStack, (typecast(-1, int)))
            self.gBP = await self.builtin_funcs.llList2Integer(self.gStack, (typecast(-2, int)))
            _next_ip = await self.builtin_funcs.llList2Integer(self.gStack, (typecast(-3, int)))
            self.gIP = radd(neg(self.gIPB), _next_ip)
            await self.popStack(neg((radd(_args_to_pop, 3))), (typecast(-1, int)))
        if cond(boolnot(bitnot(_next_ip))):
            self.gIP = 0
            self.gYielded = 1
            if cond(self.gInvokingHandler):
                await self.builtin_funcs.llMessageLinked((typecast(-4, int)), 61954, "", (typecast("", Key)))
            self.gInvokingHandler = 0
        else:
            await self.checkCodeFetchNeeded()

    async def yieldOp(self, _stack_to_yield: int) -> None:
        if cond(self.gIgnoreYields):
            _i: int = 0
            while True == True:
                if not cond(rless(_stack_to_yield, _i)):
                    break
                await self.builtin_funcs.llSay(0, radd(await self.builtin_funcs.llList2String(self.gStack, (typecast(-1, int))), "Yielded "))
                await self.popStack((typecast(-1, int)), (typecast(-1, int)))
                _i += 1
        else:
            self.gYielded = neg(bitnot(_stack_to_yield))
            return

    async def lslAssert(self, _val: int) -> None:
        if cond(boolnot(_val)):
            print(radd(typecast(bitnot(neg((radd(self.gIP, self.gIPB)))), str), "I messed up at "))
            await self.builtin_funcs.llOwnerSay(typecast(rdiv((0.0), (0.0)), str))

    async def binOp(self, _op: int, _l_type: int, _r_type: int) -> None:
        if cond(boolnot((rbitor(_r_type, _l_type)))):
            await self.integerIntegerOperation(_op)
            return
        elif cond(boolnot((rbitor(rbitxor(1, _r_type), rbitxor(1, _l_type))))):
            await self.floatFloatOperation(_op)
            return
        elif cond(req(6, _l_type)):
            await self.listAnyOperation(_op, _r_type)
            return
        elif cond(req(6, _r_type)):
            await self.anyListOperation(_op, _l_type)
            return
        elif cond(rbitor(req(3, _l_type), req(2, _l_type))):
            await self.lslAssert(boolnot(boolnot((rbitor(req(3, _r_type), req(2, _r_type))))))
            await self.stringStringOperation(_op)
            return
        elif cond(req(4, _l_type)):
            await self.vectorOperation(_op, _r_type)
            return
        elif cond(req(5, _l_type)):
            await self.lslAssert(req(5, _r_type))
            await self.rotationRotationOperation(_op)
            return
        await self.lslAssert(0)

    async def integerIntegerOperation(self, _op: int) -> None:
        _l: int = await self.builtin_funcs.llList2Integer(self.gStack, (typecast(-1, int)))
        _r: int = await self.builtin_funcs.llList2Integer(self.gStack, (typecast(-2, int)))
        _res: int = 0
        if cond(boolnot(_op)):
            _res = radd(_r, _l)
        elif cond(boolnot(bitnot(neg(_op)))):
            _res = radd(neg(_r), _l)
        elif cond(req(2, _op)):
            _res = rmul(_r, _l)
        elif cond(req(3, _op)):
            _res = rdiv(_r, _l)
        elif cond(req(4, _op)):
            _res = rmod(_r, _l)
        elif cond(req(12, _op)):
            _res = req(_r, _l)
        elif cond(req(13, _op)):
            _res = boolnot((req(_r, _l)))
        elif cond(req(9, _op)):
            _res = rless(_l, _r)
        elif cond(req(8, _op)):
            _res = rless(_r, _l)
        elif cond(req(11, _op)):
            _res = boolnot((rless(_r, _l)))
        elif cond(req(10, _op)):
            _res = boolnot((rless(_l, _r)))
        elif cond(req(6, _op)):
            _res = boolnot((rbitor(boolnot(_r), boolnot(_l))))
        elif cond(req(7, _op)):
            _res = boolnot(boolnot((rbitor(_r, _l))))
        elif cond(req(17, _op)):
            _res = rbitor(_r, _l)
        elif cond(req(16, _op)):
            _res = rbitand(_r, _l)
        elif cond(req(15, _op)):
            _res = rbitxor(_r, _l)
        elif cond(req(18, _op)):
            _res = rshl(_r, _l)
        elif cond(req(19, _op)):
            _res = rshr(_r, _l)
        else:
            await self.lslAssert(0)
        self.gStack = radd(_res, self.gStack)

    async def floatFloatOperation(self, _op: int) -> None:
        _l: float = await self.builtin_funcs.llList2Float(self.gStack, (typecast(-1, int)))
        _r: float = await self.builtin_funcs.llList2Float(self.gStack, (typecast(-2, int)))
        _what: list = []
        if cond(boolnot(_op)):
            _what = typecast(radd(_r, _l), list)
        elif cond(boolnot(bitnot(neg(_op)))):
            _what = typecast(radd(neg(_r), _l), list)
        elif cond(req(2, _op)):
            _what = typecast(rmul(_r, _l), list)
        elif cond(req(3, _op)):
            _what = typecast(rdiv(_r, _l), list)
        elif cond(req(12, _op)):
            _what = typecast(req(_r, _l), list)
        elif cond(req(13, _op)):
            _what = typecast(boolnot((req(_r, _l))), list)
        elif cond(req(9, _op)):
            _what = typecast(rless(_l, _r), list)
        elif cond(req(8, _op)):
            _what = typecast(rless(_r, _l), list)
        elif cond(req(11, _op)):
            _what = typecast(boolnot((rless(_r, _l))), list)
        elif cond(req(10, _op)):
            _what = typecast(boolnot((rless(_l, _r))), list)
        else:
            await self.lslAssert(0)
        self.gStack = radd(_what, self.gStack)

    async def stringStringOperation(self, _op: int) -> None:
        _l: str = await self.builtin_funcs.llList2String(self.gStack, (typecast(-1, int)))
        _r: str = await self.builtin_funcs.llList2String(self.gStack, (typecast(-2, int)))
        if cond(rbitor(req(13, _op), req(12, _op))):
            _eq: int = req(_r, _l)
            if cond(req(13, _op)):
                _eq = boolnot(_eq)
            self.gStack = radd(_eq, self.gStack)
        elif cond(boolnot(_op)):
            self.gStack = radd((radd((radd(_r, ((_r := "")))), radd(_l, ((_l := ""))))), self.gStack)
        else:
            await self.lslAssert(0)

    async def vectorOperation(self, _op: int, _r_type: int) -> None:
        _l: Vector = await self.builtin_funcs.llList2Vector(self.gStack, (typecast(-1, int)))
        if cond(boolnot(bitnot(neg(_r_type)))):
            _r: float = await self.builtin_funcs.llList2Float(self.gStack, (typecast(-2, int)))
            if cond(req(2, _op)):
                self.gStack = radd(rmul(_r, _l), self.gStack)
            elif cond(req(3, _op)):
                self.gStack = radd(rdiv(_r, _l), self.gStack)
            else:
                await self.lslAssert(0)
        elif cond(req(4, _r_type)):
            _r: Vector = await self.builtin_funcs.llList2Vector(self.gStack, (typecast(-2, int)))
            if cond(req(2, _op)):
                self.gStack = radd(rmul(_r, _l), self.gStack)
            elif cond(boolnot(bitnot(neg(_op)))):
                self.gStack = radd((rsub(_r, _l)), self.gStack)
            elif cond(boolnot(_op)):
                self.gStack = radd((radd(_r, _l)), self.gStack)
            elif cond(req(4, _op)):
                self.gStack = radd(rmod(_r, _l), self.gStack)
            elif cond(rbitor(req(13, _op), req(12, _op))):
                _val: int = req(_r, _l)
                if cond(req(13, _op)):
                    _val = boolnot(_val)
                self.gStack = radd(_val, self.gStack)
                return
            else:
                await self.lslAssert(0)
        elif cond(req(5, _r_type)):
            _r: Quaternion = await self.builtin_funcs.llList2Rot(self.gStack, (typecast(-2, int)))
            if cond(req(2, _op)):
                self.gStack = radd(rmul(_r, _l), self.gStack)
            elif cond(req(3, _op)):
                self.gStack = radd(rdiv(_r, _l), self.gStack)
            else:
                await self.lslAssert(0)
        else:
            await self.lslAssert(0)

    async def rotationRotationOperation(self, _op: int) -> None:
        _l: Quaternion = await self.builtin_funcs.llList2Rot(self.gStack, (typecast(-1, int)))
        _r: Quaternion = await self.builtin_funcs.llList2Rot(self.gStack, (typecast(-2, int)))
        _ret: Quaternion = Quaternion(((0.0), (0.0), (0.0), (1.0)))
        if cond(req(2, _op)):
            _ret = rmul(_r, _l)
        elif cond(req(3, _op)):
            _ret = rdiv(_r, _l)
        elif cond(boolnot(bitnot(neg(_op)))):
            _ret = rsub(_r, _l)
        elif cond(boolnot(_op)):
            _ret = radd(_r, _l)
        elif cond(rbitor(req(13, _op), req(12, _op))):
            _val: int = req(_r, _l)
            if cond(req(13, _op)):
                _val = boolnot(_val)
            self.gStack = radd(_val, self.gStack)
            return
        else:
            await self.lslAssert(0)
        self.gStack = radd(_ret, self.gStack)

    async def listAnyOperation(self, _op: int, _r_type: int) -> None:
        _l_str: str = await self.builtin_funcs.llList2String(self.gStack, (typecast(-1, int)))
        await self.tombstoneStack((typecast(-1, int)))
        _l: list = await self.JSONTypeParse(radd(_l_str, ((_l_str := ""))))
        _r: list = []
        if cond(req(6, _r_type)):
            _r_str: str = await self.builtin_funcs.llList2String(self.gStack, (typecast(-2, int)))
            await self.tombstoneStack((typecast(-2, int)))
            _r = await self.JSONTypeParse(radd(_r_str, ((_r_str := ""))))
        else:
            _r = await self.builtin_funcs.llList2List(self.gStack, (typecast(-2, int)), (typecast(-2, int)))
            await self.tombstoneStack((typecast(-2, int)))
        if cond(boolnot(_op)):
            self.gStack = radd(await self.JSONTypeDump(radd((radd(_r, ((_r := [])))), radd(_l, ((_l := []))))), self.gStack)
            return
        await self.lslAssert(req(6, _r_type))
        if cond(rbitor(req(13, _op), req(12, _op))):
            _val: int = rneq(radd(_r, ((_r := []))), radd(_l, ((_l := []))))
            if cond(req(12, _op)):
                _val = boolnot(_val)
            self.gStack = radd(_val, self.gStack)
            return
        await self.lslAssert(0)

    async def anyListOperation(self, _op: int, _l_type: int) -> None:
        await self.lslAssert(boolnot(_op))
        _r_str: str = await self.builtin_funcs.llList2String(self.gStack, (typecast(-2, int)))
        await self.tombstoneStack((typecast(-2, int)))
        _r: list = await self.JSONTypeParse(radd(_r_str, ((_r_str := ""))))
        _l: list = await self.builtin_funcs.llList2List(self.gStack, (typecast(-1, int)), (typecast(-1, int)))
        await self.tombstoneStack((typecast(-1, int)))
        self.gStack = radd(await self.JSONTypeDump(radd((radd(_r, ((_r := [])))), radd(_l, ((_l := []))))), self.gStack)

    async def unOp(self, _op: int, _un_type: int) -> None:
        if cond(boolnot(_un_type)):
            _l: int = await self.builtin_funcs.llList2Integer(self.gStack, (typecast(-1, int)))
            _res: int = 0
            if cond(boolnot(bitnot(neg(_op)))):
                _res = neg(_l)
            elif cond(req(14, _op)):
                _res = bitnot(_l)
            elif cond(req(5, _op)):
                _res = boolnot(_l)
            else:
                await self.lslAssert(0)
            self.gStack = radd(_res, self.gStack)
            return
        elif cond(boolnot(bitnot(neg(_un_type)))):
            if cond(boolnot(bitnot(neg(_op)))):
                self.gStack = radd(neg(await self.builtin_funcs.llList2Float(self.gStack, (typecast(-1, int)))), self.gStack)
                return
        elif cond(req(4, _un_type)):
            if cond(boolnot(bitnot(neg(_op)))):
                self.gStack = radd(neg(await self.builtin_funcs.llList2Vector(self.gStack, (typecast(-1, int)))), self.gStack)
                return
        elif cond(req(5, _un_type)):
            if cond(boolnot(bitnot(neg(_op)))):
                self.gStack = radd(neg(await self.builtin_funcs.llList2Rot(self.gStack, (typecast(-1, int)))), self.gStack)
                return
        await self.lslAssert(0)

    async def castOp(self, _from_type: int, _to_type: int) -> None:
        if cond(req(6, _to_type)):
            await self.buildListOp(1)
            return
        if cond(req(4, _from_type)):
            await self.lslAssert(req(2, _to_type))
            self.gStack = radd(typecast(await self.builtin_funcs.llList2Vector(self.gStack, (typecast(-1, int))), str), self.gStack)
            await self.popStack((typecast(-2, int)), (typecast(-2, int)))
            return
        elif cond(req(5, _from_type)):
            await self.lslAssert(req(2, _to_type))
            self.gStack = radd(typecast(await self.builtin_funcs.llList2Rot(self.gStack, (typecast(-1, int))), str), self.gStack)
            await self.popStack((typecast(-2, int)), (typecast(-2, int)))
            return
        _val: str = await self.builtin_funcs.llList2String(self.gStack, (typecast(-1, int)))
        await self.popStack((typecast(-1, int)), (typecast(-1, int)))
        if cond(req(6, _from_type)):
            await self.lslAssert(req(2, _to_type))
            self.gStack = radd(typecast(await self.JSONTypeParse(radd(_val, ((_val := "")))), str), self.gStack)
            return
        _what: list = []
        if cond(boolnot(_to_type)):
            _what = typecast(typecast(_val, int), list)
        elif cond(boolnot(bitnot(neg(_to_type)))):
            _what = typecast(typecast(_val, float), list)
        elif cond(req(2, _to_type)):
            _what = typecast(_val, list)
        elif cond(req(3, _to_type)):
            _what = typecast(typecast(_val, Key), list)
        elif cond(req(4, _to_type)):
            _what = typecast(typecast(_val, Vector), list)
        elif cond(req(5, _to_type)):
            _what = typecast(typecast(_val, Quaternion), list)
        else:
            await self.lslAssert(0)
        self.gStack = radd((radd(_what, ((_what := [])))), self.gStack)

    async def getDefault(self, _lsl_type: int, _for_initialize: int) -> list:
        if cond(boolnot(_lsl_type)):
            return typecast(0, list)
        if cond(req(2, _lsl_type)):
            return typecast("", list)
        elif cond(boolnot(bitnot(neg(_lsl_type)))):
            return typecast(0.0, list)
        elif cond(req(3, _lsl_type)):
            return typecast(typecast("", Key), list)
        elif cond(req(4, _lsl_type)):
            return typecast(Vector(((0.0), (0.0), (0.0))), list)
        elif cond(req(5, _lsl_type)):
            if cond(_for_initialize):
                return typecast(Quaternion(((0.0), (0.0), (0.0), (1.0))), list)
            else:
                return typecast(Quaternion(((0.0), (0.0), (0.0), (0.0))), list)
        elif cond(req(6, _lsl_type)):
            return typecast("[]", list)
        await self.lslAssert(0)
        return []

    async def allocSlotsOp(self, _whence: int) -> None:
        _types_str: str = await self.builtin_funcs.llList2String(self.gCode, self.gIP)
        self.gIP += 1
        _types_len: int = await self.builtin_funcs.llStringLength(_types_str)
        _i: int = 0
        _defaults: list = []
        _i = 0
        while True == True:
            if not cond(rless(_types_len, _i)):
                break
            _char: str = await self.builtin_funcs.llGetSubString(_types_str, _i, _i)
            _defaults = radd(await self.getDefault(typecast(_char, int), req(2, _whence)), _defaults)
            _i += 1
        if cond(boolnot(bitnot(neg(_whence)))):
            self.gStack = radd((radd(_defaults, ((_defaults := [])))), self.gStack)
            self.gSP = radd(_types_len, self.gSP)
        elif cond(req(2, _whence)):
            self.gGlobals = radd((radd(_defaults, ((_defaults := [])))), self.gGlobals)
        else:
            await self.lslAssert(0)

    async def swapOp(self) -> None:
        _top: list = await self.builtin_funcs.llList2List(self.gStack, (typecast(-1, int)), (typecast(-1, int)))
        _under: list = await self.builtin_funcs.llList2List(self.gStack, (typecast(-2, int)), (typecast(-2, int)))
        await self.popStack((typecast(-2, int)), (typecast(-1, int)))
        self.gStack = radd((radd(_under, _top)), self.gStack)

    async def boolOp(self, _type: int) -> None:
        _bool_res: int = 0
        _stack_val: str = await self.builtin_funcs.llList2String(self.gStack, (typecast(-1, int)))
        await self.popStack((typecast(-1, int)), (typecast(-1, int)))
        if cond(rbitor(boolnot(bitnot(neg(_type))), boolnot(_type))):
            if cond(boolnot((req((0.0), typecast(_stack_val, float))))):
                _bool_res = 1
        elif cond(req(4, _type)):
            if cond(boolnot((req(Vector(((0.0), (0.0), (0.0))), typecast(_stack_val, Vector))))):
                _bool_res = 1
        elif cond(req(5, _type)):
            if cond(boolnot((req(Quaternion(((0.0), (0.0), (0.0), (1.0))), typecast(_stack_val, Quaternion))))):
                _bool_res = 1
        elif cond(req(3, _type)):
            if cond(typecast(_stack_val, Key)):
                _bool_res = 1
        elif cond(req(2, _type)):
            _bool_res = boolnot((req("", radd(_stack_val, ((_stack_val := ""))))))
        elif cond(req(6, _type)):
            _bool_res = boolnot((req("[]", _stack_val)))
        self.gStack = radd(_bool_res, self.gStack)

    async def takeMemberOp(self, _type: int, _idx: int) -> None:
        _val: float = (0.0)
        if cond(req(4, _type)):
            _v: Vector = await self.builtin_funcs.llList2Vector(self.gStack, (typecast(-1, int)))
            if cond(boolnot(_idx)):
                _val = _v[0]
            elif cond(boolnot(bitnot(neg(_idx)))):
                _val = _v[1]
            else:
                _val = _v[2]
        else:
            _r: Quaternion = await self.builtin_funcs.llList2Rot(self.gStack, (typecast(-1, int)))
            if cond(boolnot(_idx)):
                _val = _r[0]
            elif cond(boolnot(bitnot(neg(_idx)))):
                _val = _r[1]
            elif cond(req(2, _idx)):
                _val = _r[2]
            else:
                _val = _r[3]
        await self.popStack((typecast(-1, int)), (typecast(-1, int)))
        self.gStack = radd(_val, self.gStack)

    async def replaceMemberOp(self, _type: int, _idx: int) -> None:
        _val: float = await self.builtin_funcs.llList2Float(self.gStack, (typecast(-2, int)))
        if cond(req(4, _type)):
            _v: Vector = await self.builtin_funcs.llList2Vector(self.gStack, (typecast(-1, int)))
            if cond(boolnot(_idx)):
                _v = replace_coord_axis(_v, 0, _val)
            elif cond(boolnot(bitnot(neg(_idx)))):
                _v = replace_coord_axis(_v, 1, _val)
            else:
                _v = replace_coord_axis(_v, 2, _val)
            self.gStack = radd(_v, self.gStack)
        else:
            _r: Quaternion = await self.builtin_funcs.llList2Rot(self.gStack, (typecast(-1, int)))
            if cond(boolnot(_idx)):
                _r = replace_coord_axis(_r, 0, _val)
            elif cond(boolnot(bitnot(neg(_idx)))):
                _r = replace_coord_axis(_r, 1, _val)
            elif cond(req(2, _idx)):
                _r = replace_coord_axis(_r, 2, _val)
            else:
                _r = replace_coord_axis(_r, 3, _val)
            self.gStack = radd(_r, self.gStack)
        await self.popStack((typecast(-3, int)), (typecast(-2, int)))

    async def buildCoordOp(self, _type: int) -> None:
        _what: list = []
        _to_pop: int = 3
        if cond(req(4, _type)):
            _what = typecast(Vector((await self.builtin_funcs.llList2Float(self.gStack, (typecast(-3, int))), await self.builtin_funcs.llList2Float(self.gStack, (typecast(-2, int))), await self.builtin_funcs.llList2Float(self.gStack, (typecast(-1, int))))), list)
        elif cond(req(5, _type)):
            _to_pop = 4
            _what = typecast(Quaternion((await self.builtin_funcs.llList2Float(self.gStack, (typecast(-4, int))), await self.builtin_funcs.llList2Float(self.gStack, (typecast(-3, int))), await self.builtin_funcs.llList2Float(self.gStack, (typecast(-2, int))), await self.builtin_funcs.llList2Float(self.gStack, (typecast(-1, int))))), list)
        await self.popStack(neg(_to_pop), (typecast(-1, int)))
        self.gStack = radd(_what, self.gStack)

    async def buildListOp(self, _num_elems: int) -> None:
        _val: list = []
        while cond(postdecr(locals(), "_num_elems")):
            _val = radd((radd(_val, ((_val := [])))), await self.builtin_funcs.llList2List(self.gStack, (typecast(-1, int)), (typecast(-1, int))))
            await self.popStack((typecast(-1, int)), (typecast(-1, int)))
        self.gStack = radd(await self.JSONTypeDump(radd(_val, ((_val := [])))), self.gStack)

    async def changeStateOp(self, _state_num: int) -> None:
        self.gStack = []
        self.gBP = 0
        self.gIP = 0
        self.gSP = 0
        self.gYielded = 1
        self.gInvokingHandler = 0
        await self.builtin_funcs.llMessageLinked((typecast(-4, int)), 61959, "", typecast(typecast(_state_num, str), Key))

    async def interpreterLoop(self) -> None:
        self.gYielded = 0
        while cond(boolnot((rbitor(self.gYielded, rbitor(self.gFault, self.gCodeFetchNeeded))))):
            _read: int = await self.builtin_funcs.llList2Integer(self.gCode, self.gIP)
            _op: int = rbitand(31, _read)
            _args: int = rshr(5, _read)
            self.gIP += 1
            if cond(_op):
                if cond(boolnot(bitnot(neg(_op)))):
                    await self.binOp(rbitand(255, _args), rbitand(255, rshr(8, _args)), rbitand(255, rshr(16, _args)))
                    await self.popStack((typecast(-3, int)), (typecast(-2, int)))
                elif cond(req(2, _op)):
                    await self.unOp(rbitand(255, _args), rbitand(255, rshr(8, _args)))
                    await self.popStack((typecast(-2, int)), (typecast(-2, int)))
                elif cond(req(6, _op)):
                    await self.pushOp(rbitand(15, _args), rbitand(3, rshr(5, _args)), rshr(8, _args))
                elif cond(rbitor(req(9, _op), req(8, _op))):
                    await self.storeOp(_op, rbitand(15, _args), rbitand(3, rshr(5, _args)), rshr(8, _args))
                elif cond(req(22, _op)):
                    print(await self.builtin_funcs.llList2String(self.gStack, (typecast(-1, int))))
                    await self.popStack((typecast(-1, int)), (typecast(-1, int)))
                elif cond(req(10, _op)):
                    self.gStack = radd(await self.builtin_funcs.llList2List(self.gStack, (typecast(-1, int)), (typecast(-1, int))), self.gStack)
                elif cond(req(7, _op)):
                    await self.popStack(neg(_args), (typecast(-1, int)))
                elif cond(req(3, _op)):
                    await self.castOp(rbitand(255, _args), rbitand(255, rshr(8, _args)))
                elif cond(req(4, _op)):
                    await self.boolOp(_args)
                elif cond(req(5, _op)):
                    await self.allocSlotsOp(rbitand(255, _args))
                elif cond(req(12, _op)):
                    await self.jumpOp(rbitand(3, _args), rshr(3, _args))
                elif cond(req(13, _op)):
                    await self.callOp(rbitand(3, _args), rshr(3, _args))
                elif cond(req(15, _op)):
                    await self.callLibOp(rbitand(15, _args), rbitand(4095, rshr(4, _args)), rshr(16, _args))
                elif cond(req(14, _op)):
                    await self.retOp(_args)
                elif cond(req(11, _op)):
                    await self.swapOp()
                elif cond(req(16, _op)):
                    await self.buildListOp(_args)
                elif cond(req(17, _op)):
                    await self.buildCoordOp(rbitand(255, _args))
                elif cond(req(20, _op)):
                    await self.yieldOp(_args)
                elif cond(req(18, _op)):
                    await self.takeMemberOp(rbitand(255, _args), rbitand(255, rshr(8, _args)))
                elif cond(req(19, _op)):
                    await self.replaceMemberOp(rbitand(255, _args), rbitand(255, rshr(8, _args)))
                elif cond(req(21, _op)):
                    await self.changeStateOp(rbitand(255, _args))
                else:
                    await self.lslAssert(0)
            await self.checkCodeFetchNeeded()
        if cond(self.gCodeFetchNeeded):
            await self.builtin_funcs.llMessageLinked((typecast(-4, int)), 61955, "", typecast(typecast(radd(self.gIP, self.gIPB), str), Key))

    async def handleCodeReload(self, _new_ipb: int) -> None:
        self.gCodeSize = rneq([], self.gCode)
        self.gIP = radd((radd(self.gIPB, neg(_new_ipb))), self.gIP)
        self.gIPB = _new_ipb
        await self.checkCodeFetchNeeded()
        await self.lslAssert(boolnot(self.gCodeFetchNeeded))

    async def edefaultstate_entry(self) -> None:
        self.gIgnoreYields = 1
        await self.resetVMState()

    async def edefaultlink_message(self, _link_num: int, _num: int, _str: str, _id: Key) -> None:
        if cond(boolnot((rbitand(rless(_num, 61950), rless(61960, _num))))):
            return
        if cond(req(61956, _num)):
            self.gCode = []
            self.gCode = await self.builtin_funcs.llJson2List(radd(_str, ((_str := ""))))
            await self.handleCodeReload(typecast(typecast(_id, str), int))
            if cond(boolnot(self.gExpectingCallLibReply)):
                await self.interpreterLoop()
        elif cond(req(61952, _num)):
            if cond(boolnot(self.gExpectingCallLibReply)):
                await self.builtin_funcs.llOwnerSay("Received unsolicited call lib response?")
                return
            self.gExpectingCallLibReply = 0
            await self.retOp(0)
            _retval_type: int = typecast(typecast(_id, str), int)
            if cond(boolnot(_retval_type)):
                await self.lslAssert(req("", _str))
            elif cond(boolnot(bitnot(neg(_retval_type)))):
                self.gStack = radd(await self.JSONTypeParse(radd(_str, ((_str := "")))), self.gStack)
            elif cond(req(2, _retval_type)):
                self.gStack = radd((radd(_str, ((_str := "")))), self.gStack)
            else:
                await self.lslAssert(0)
            if cond(boolnot(self.gCodeFetchNeeded)):
                await self.interpreterLoop()
        elif cond(req(61957, _num)):
            await self.builtin_funcs.llResetScript()
        elif cond(req(61958, _num)):
            await self.resetVMState()
        elif cond(req(61953, _num)):
            await self.lslAssert(boolnot(self.gInvokingHandler))
            self.gInvokingHandler = 1
            self.gStack = radd(await self.JSONTypeParse(radd(_str, ((_str := "")))), self.gStack)
            self.gIP = bitnot(self.gIPB)
            await self.callOp(1, typecast(typecast(_id, str), int))
            await self.checkCodeFetchNeeded()
            await self.interpreterLoop()

