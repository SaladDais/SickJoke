from lummao import *


class Script(BaseLSLScript):

    def __init__(self):
        super().__init__()

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

    async def edefaultlink_message(self, _sender_num: int, _num: int, _str: str, _id: Key) -> None:
        if cond(boolnot((rbitand(rless(_num, 61950), rless(61960, _num))))):
            return
        if cond(req(61951, _num)):
            _lib_num: int = typecast(typecast(_id, str), int)
            _no_wait: int = rbitand((typecast(-65536, int)), _lib_num)
            _lib_num = rbitand(65535, _lib_num)
            _args: list = await self.JSONTypeParse(radd(_str, ((_str := ""))))
            _ret: list = []
            _ret_type: int = 0
            if cond(boolnot(_lib_num)):
                _ret = typecast(await self.builtin_funcs.llAbs(await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(boolnot(bitnot(neg(_lib_num)))):
                _ret = typecast(await self.builtin_funcs.llAcos(await self.builtin_funcs.llList2Float(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(2, _lib_num)):
                await self.builtin_funcs.llAddToLandBanList(await self.builtin_funcs.llList2Key(_args, 0), await self.builtin_funcs.llList2Float(radd(_args, ((_args := []))), 1))
            elif cond(req(3, _lib_num)):
                await self.builtin_funcs.llAddToLandPassList(await self.builtin_funcs.llList2Key(_args, 0), await self.builtin_funcs.llList2Float(radd(_args, ((_args := []))), 1))
            elif cond(req(4, _lib_num)):
                await self.builtin_funcs.llAdjustSoundVolume(await self.builtin_funcs.llList2Float(radd(_args, ((_args := []))), 0))
            elif cond(req(5, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llAgentInExperience(await self.builtin_funcs.llList2Key(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(6, _lib_num)):
                await self.builtin_funcs.llAllowInventoryDrop(await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 0))
            elif cond(req(7, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llAngleBetween(await self.builtin_funcs.llList2Rot(_args, 0), await self.builtin_funcs.llList2Rot(radd(_args, ((_args := []))), 1)), list)
                _ret_type = 1
            elif cond(req(8, _lib_num)):
                await self.builtin_funcs.llApplyImpulse(await self.builtin_funcs.llList2Vector(_args, 0), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 1))
            elif cond(req(9, _lib_num)):
                await self.builtin_funcs.llApplyRotationalImpulse(await self.builtin_funcs.llList2Vector(_args, 0), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 1))
            elif cond(req(10, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llAsin(await self.builtin_funcs.llList2Float(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(11, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llAtan2(await self.builtin_funcs.llList2Float(_args, 0), await self.builtin_funcs.llList2Float(radd(_args, ((_args := []))), 1)), list)
                _ret_type = 1
            elif cond(req(14, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llAvatarOnLinkSitTarget(await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(15, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llAvatarOnSitTarget(), list)
                _ret_type = 1
            elif cond(req(16, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llAxes2Rot(await self.builtin_funcs.llList2Vector(_args, 0), await self.builtin_funcs.llList2Vector(_args, 1), await self.builtin_funcs.llList2Vector(radd(_args, ((_args := []))), 2)), list)
                _ret_type = 1
            elif cond(req(17, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llAxisAngle2Rot(await self.builtin_funcs.llList2Vector(_args, 0), await self.builtin_funcs.llList2Float(radd(_args, ((_args := []))), 1)), list)
                _ret_type = 1
            elif cond(req(18, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llBase64ToInteger(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(19, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llBase64ToString(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(22, _lib_num)):
                _ret = await self.builtin_funcs.llCSV2List(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0))
                _ret_type = 2
            elif cond(req(23, _lib_num)):
                _ret = await self.builtin_funcs.llCastRay(await self.builtin_funcs.llList2Vector(_args, 0), await self.builtin_funcs.llList2Vector(_args, 1), await self.JSONTypeParse(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 2)))
                _ret_type = 2
            elif cond(req(24, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llCeil(await self.builtin_funcs.llList2Float(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(25, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llChar(await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(27, _lib_num)):
                await self.builtin_funcs.llClearExperiencePermissions(await self.builtin_funcs.llList2Key(radd(_args, ((_args := []))), 0))
            elif cond(req(28, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llClearLinkMedia(await self.builtin_funcs.llList2Integer(_args, 0), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 1)), list)
                _ret_type = 1
            elif cond(req(29, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llClearPrimMedia(await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(30, _lib_num)):
                await self.builtin_funcs.llCloseRemoteDataChannel(await self.builtin_funcs.llList2Key(radd(_args, ((_args := []))), 0))
            elif cond(req(31, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llCloud(await self.builtin_funcs.llList2Vector(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(32, _lib_num)):
                await self.builtin_funcs.llCollisionFilter(await self.builtin_funcs.llList2String(_args, 0), await self.builtin_funcs.llList2Key(_args, 1), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 2))
            elif cond(req(33, _lib_num)):
                await self.builtin_funcs.llCollisionSound(await self.builtin_funcs.llList2String(_args, 0), await self.builtin_funcs.llList2Float(radd(_args, ((_args := []))), 1))
            elif cond(req(34, _lib_num)):
                await self.builtin_funcs.llCollisionSprite(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0))
            elif cond(req(35, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llCos(await self.builtin_funcs.llList2Float(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(36, _lib_num)):
                await self.builtin_funcs.llCreateCharacter(await self.JSONTypeParse(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0)))
            elif cond(req(37, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llCreateKeyValue(await self.builtin_funcs.llList2String(_args, 0), await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 1)), list)
                _ret_type = 1
            elif cond(req(39, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llDataSizeKeyValue(), list)
                _ret_type = 1
            elif cond(req(40, _lib_num)):
                await self.builtin_funcs.llDeleteCharacter()
            elif cond(req(41, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llDeleteKeyValue(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(42, _lib_num)):
                _ret = await self.builtin_funcs.llDeleteSubList(await self.JSONTypeParse(await self.builtin_funcs.llList2String(_args, 0)), await self.builtin_funcs.llList2Integer(_args, 1), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 2))
                _ret_type = 2
            elif cond(req(43, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llDeleteSubString(await self.builtin_funcs.llList2String(_args, 0), await self.builtin_funcs.llList2Integer(_args, 1), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 2)), list)
                _ret_type = 1
            elif cond(req(45, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llDetectedGrab(await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(46, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llDetectedGroup(await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(48, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llDetectedLinkNumber(await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(49, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llDetectedName(await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(51, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llDetectedPos(await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(52, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llDetectedRot(await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(53, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llDetectedTouchBinormal(await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(54, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llDetectedTouchFace(await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(55, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llDetectedTouchNormal(await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(56, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llDetectedTouchPos(await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(57, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llDetectedTouchST(await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(58, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llDetectedTouchUV(await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(59, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llDetectedType(await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(60, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llDetectedVel(await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(61, _lib_num)):
                await self.builtin_funcs.llDialog(await self.builtin_funcs.llList2Key(_args, 0), await self.builtin_funcs.llList2String(_args, 1), await self.JSONTypeParse(await self.builtin_funcs.llList2String(_args, 2)), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 3))
            elif cond(req(63, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llDumpList2String(await self.JSONTypeParse(await self.builtin_funcs.llList2String(_args, 0)), await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 1)), list)
                _ret_type = 1
            elif cond(req(64, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llEdgeOfWorld(await self.builtin_funcs.llList2Vector(_args, 0), await self.builtin_funcs.llList2Vector(radd(_args, ((_args := []))), 1)), list)
                _ret_type = 1
            elif cond(req(65, _lib_num)):
                await self.builtin_funcs.llEjectFromLand(await self.builtin_funcs.llList2Key(radd(_args, ((_args := []))), 0))
            elif cond(req(66, _lib_num)):
                await self.builtin_funcs.llEmail(await self.builtin_funcs.llList2String(_args, 0), await self.builtin_funcs.llList2String(_args, 1), await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 2))
            elif cond(req(67, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llEscapeURL(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(68, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llEuler2Rot(await self.builtin_funcs.llList2Vector(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(69, _lib_num)):
                await self.builtin_funcs.llEvade(await self.builtin_funcs.llList2Key(_args, 0), await self.JSONTypeParse(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 1)))
            elif cond(req(70, _lib_num)):
                await self.builtin_funcs.llExecCharacterCmd(await self.builtin_funcs.llList2Integer(_args, 0), await self.JSONTypeParse(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 1)))
            elif cond(req(71, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llFabs(await self.builtin_funcs.llList2Float(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(72, _lib_num)):
                await self.builtin_funcs.llFleeFrom(await self.builtin_funcs.llList2Vector(_args, 0), await self.builtin_funcs.llList2Float(_args, 1), await self.JSONTypeParse(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 2)))
            elif cond(req(73, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llFloor(await self.builtin_funcs.llList2Float(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(74, _lib_num)):
                await self.builtin_funcs.llForceMouselook(await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 0))
            elif cond(req(75, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llFrand(await self.builtin_funcs.llList2Float(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(76, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGenerateKey(), list)
                _ret_type = 1
            elif cond(req(77, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetAccel(), list)
                _ret_type = 1
            elif cond(req(78, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetAgentInfo(await self.builtin_funcs.llList2Key(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(79, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetAgentLanguage(await self.builtin_funcs.llList2Key(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(80, _lib_num)):
                _ret = await self.builtin_funcs.llGetAgentList(await self.builtin_funcs.llList2Integer(_args, 0), await self.JSONTypeParse(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 1)))
                _ret_type = 2
            elif cond(req(81, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetAgentSize(await self.builtin_funcs.llList2Key(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(82, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetAlpha(await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(84, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetAnimation(await self.builtin_funcs.llList2Key(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(85, _lib_num)):
                _ret = await self.builtin_funcs.llGetAnimationList(await self.builtin_funcs.llList2Key(radd(_args, ((_args := []))), 0))
                _ret_type = 2
            elif cond(req(87, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetAttached(), list)
                _ret_type = 1
            elif cond(req(88, _lib_num)):
                _ret = await self.builtin_funcs.llGetAttachedList(await self.builtin_funcs.llList2Key(radd(_args, ((_args := []))), 0))
                _ret_type = 2
            elif cond(req(89, _lib_num)):
                _ret = await self.builtin_funcs.llGetBoundingBox(await self.builtin_funcs.llList2Key(radd(_args, ((_args := []))), 0))
                _ret_type = 2
            elif cond(req(92, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetCenterOfMass(), list)
                _ret_type = 1
            elif cond(req(93, _lib_num)):
                _ret = await self.builtin_funcs.llGetClosestNavPoint(await self.builtin_funcs.llList2Vector(_args, 0), await self.JSONTypeParse(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 1)))
                _ret_type = 2
            elif cond(req(94, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetColor(await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(95, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetCreator(), list)
                _ret_type = 1
            elif cond(req(96, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetDate(), list)
                _ret_type = 1
            elif cond(req(97, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetDayLength(), list)
                _ret_type = 1
            elif cond(req(98, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetDayOffset(), list)
                _ret_type = 1
            elif cond(req(99, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetDisplayName(await self.builtin_funcs.llList2Key(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(100, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetEnergy(), list)
                _ret_type = 1
            elif cond(req(101, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetEnv(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(102, _lib_num)):
                _ret = await self.builtin_funcs.llGetEnvironment(await self.builtin_funcs.llList2Vector(_args, 0), await self.JSONTypeParse(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 1)))
                _ret_type = 2
            elif cond(req(103, _lib_num)):
                _ret = await self.builtin_funcs.llGetExperienceDetails(await self.builtin_funcs.llList2Key(radd(_args, ((_args := []))), 0))
                _ret_type = 2
            elif cond(req(104, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetExperienceErrorMessage(await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(105, _lib_num)):
                _ret = await self.builtin_funcs.llGetExperienceList(await self.builtin_funcs.llList2Key(radd(_args, ((_args := []))), 0))
                _ret_type = 2
            elif cond(req(106, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetForce(), list)
                _ret_type = 1
            elif cond(req(107, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetFreeMemory(), list)
                _ret_type = 1
            elif cond(req(108, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetFreeURLs(), list)
                _ret_type = 1
            elif cond(req(109, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetGMTclock(), list)
                _ret_type = 1
            elif cond(req(110, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetGeometricCenter(), list)
                _ret_type = 1
            elif cond(req(111, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetHTTPHeader(await self.builtin_funcs.llList2Key(_args, 0), await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 1)), list)
                _ret_type = 1
            elif cond(req(112, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetInventoryAcquireTime(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(113, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetInventoryCreator(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(114, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetInventoryKey(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(115, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetInventoryName(await self.builtin_funcs.llList2Integer(_args, 0), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 1)), list)
                _ret_type = 1
            elif cond(req(116, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetInventoryNumber(await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(117, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetInventoryPermMask(await self.builtin_funcs.llList2String(_args, 0), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 1)), list)
                _ret_type = 1
            elif cond(req(118, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetInventoryType(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(119, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetKey(), list)
                _ret_type = 1
            elif cond(req(120, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetLandOwnerAt(await self.builtin_funcs.llList2Vector(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(121, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetLinkKey(await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(122, _lib_num)):
                _ret = await self.builtin_funcs.llGetLinkMedia(await self.builtin_funcs.llList2Integer(_args, 0), await self.builtin_funcs.llList2Integer(_args, 1), await self.JSONTypeParse(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 2)))
                _ret_type = 2
            elif cond(req(123, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetLinkName(await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(124, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetLinkNumber(), list)
                _ret_type = 1
            elif cond(req(125, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetLinkNumberOfSides(await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(126, _lib_num)):
                _ret = await self.builtin_funcs.llGetLinkPrimitiveParams(await self.builtin_funcs.llList2Integer(_args, 0), await self.JSONTypeParse(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 1)))
                _ret_type = 2
            elif cond(req(127, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetListEntryType(await self.JSONTypeParse(await self.builtin_funcs.llList2String(_args, 0)), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 1)), list)
                _ret_type = 1
            elif cond(req(128, _lib_num)):
                _ret = typecast(rneq([], await self.JSONTypeParse(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0))), list)
                _ret_type = 1
            elif cond(req(129, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetLocalPos(), list)
                _ret_type = 1
            elif cond(req(130, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetLocalRot(), list)
                _ret_type = 1
            elif cond(req(131, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetMass(), list)
                _ret_type = 1
            elif cond(req(132, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetMassMKS(), list)
                _ret_type = 1
            elif cond(req(133, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetMaxScaleFactor(), list)
                _ret_type = 1
            elif cond(req(134, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetMemoryLimit(), list)
                _ret_type = 1
            elif cond(req(135, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetMinScaleFactor(), list)
                _ret_type = 1
            elif cond(req(136, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetMoonDirection(), list)
                _ret_type = 1
            elif cond(req(137, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetMoonRotation(), list)
                _ret_type = 1
            elif cond(req(138, _lib_num)):
                await self.builtin_funcs.llGetNextEmail(await self.builtin_funcs.llList2String(_args, 0), await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 1))
            elif cond(req(139, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetNotecardLine(await self.builtin_funcs.llList2String(_args, 0), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 1)), list)
                _ret_type = 1
            elif cond(req(140, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetNumberOfNotecardLines(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(141, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetNumberOfPrims(), list)
                _ret_type = 1
            elif cond(req(142, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetNumberOfSides(), list)
                _ret_type = 1
            elif cond(req(143, _lib_num)):
                _ret = await self.builtin_funcs.llGetObjectAnimationNames()
                _ret_type = 2
            elif cond(req(144, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetObjectDesc(), list)
                _ret_type = 1
            elif cond(req(145, _lib_num)):
                _ret = await self.builtin_funcs.llGetObjectDetails(await self.builtin_funcs.llList2Key(_args, 0), await self.JSONTypeParse(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 1)))
                _ret_type = 2
            elif cond(req(146, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetObjectLinkKey(await self.builtin_funcs.llList2Key(_args, 0), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 1)), list)
                _ret_type = 1
            elif cond(req(147, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetObjectMass(await self.builtin_funcs.llList2Key(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(148, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetObjectName(), list)
                _ret_type = 1
            elif cond(req(149, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetObjectPermMask(await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(150, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetObjectPrimCount(await self.builtin_funcs.llList2Key(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(151, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetOmega(), list)
                _ret_type = 1
            elif cond(req(152, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetOwner(), list)
                _ret_type = 1
            elif cond(req(153, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetOwnerKey(await self.builtin_funcs.llList2Key(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(154, _lib_num)):
                _ret = await self.builtin_funcs.llGetParcelDetails(await self.builtin_funcs.llList2Vector(_args, 0), await self.JSONTypeParse(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 1)))
                _ret_type = 2
            elif cond(req(155, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetParcelFlags(await self.builtin_funcs.llList2Vector(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(156, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetParcelMaxPrims(await self.builtin_funcs.llList2Vector(_args, 0), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 1)), list)
                _ret_type = 1
            elif cond(req(157, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetParcelMusicURL(), list)
                _ret_type = 1
            elif cond(req(158, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetParcelPrimCount(await self.builtin_funcs.llList2Vector(_args, 0), await self.builtin_funcs.llList2Integer(_args, 1), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 2)), list)
                _ret_type = 1
            elif cond(req(159, _lib_num)):
                _ret = await self.builtin_funcs.llGetParcelPrimOwners(await self.builtin_funcs.llList2Vector(radd(_args, ((_args := []))), 0))
                _ret_type = 2
            elif cond(req(162, _lib_num)):
                _ret = await self.builtin_funcs.llGetPhysicsMaterial()
                _ret_type = 2
            elif cond(req(163, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetPos(), list)
                _ret_type = 1
            elif cond(req(164, _lib_num)):
                _ret = await self.builtin_funcs.llGetPrimMediaParams(await self.builtin_funcs.llList2Integer(_args, 0), await self.JSONTypeParse(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 1)))
                _ret_type = 2
            elif cond(req(165, _lib_num)):
                _ret = await self.builtin_funcs.llGetPrimitiveParams(await self.JSONTypeParse(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0)))
                _ret_type = 2
            elif cond(req(166, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetRegionAgentCount(), list)
                _ret_type = 1
            elif cond(req(167, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetRegionCorner(), list)
                _ret_type = 1
            elif cond(req(168, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetRegionDayLength(), list)
                _ret_type = 1
            elif cond(req(169, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetRegionDayOffset(), list)
                _ret_type = 1
            elif cond(req(170, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetRegionFPS(), list)
                _ret_type = 1
            elif cond(req(171, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetRegionFlags(), list)
                _ret_type = 1
            elif cond(req(172, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetRegionMoonDirection(), list)
                _ret_type = 1
            elif cond(req(173, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetRegionMoonRotation(), list)
                _ret_type = 1
            elif cond(req(174, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetRegionName(), list)
                _ret_type = 1
            elif cond(req(175, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetRegionSunDirection(), list)
                _ret_type = 1
            elif cond(req(176, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetRegionSunRotation(), list)
                _ret_type = 1
            elif cond(req(177, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetRegionTimeDilation(), list)
                _ret_type = 1
            elif cond(req(178, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetRegionTimeOfDay(), list)
                _ret_type = 1
            elif cond(req(179, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetRootPosition(), list)
                _ret_type = 1
            elif cond(req(180, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetRootRotation(), list)
                _ret_type = 1
            elif cond(req(181, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetRot(), list)
                _ret_type = 1
            elif cond(req(182, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetSPMaxMemory(), list)
                _ret_type = 1
            elif cond(req(183, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetScale(), list)
                _ret_type = 1
            elif cond(req(184, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetScriptName(), list)
                _ret_type = 1
            elif cond(req(185, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetScriptState(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(186, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetSimStats(await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(187, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetSimulatorHostname(), list)
                _ret_type = 1
            elif cond(req(188, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetStartParameter(), list)
                _ret_type = 1
            elif cond(req(189, _lib_num)):
                _ret = await self.builtin_funcs.llGetStaticPath(await self.builtin_funcs.llList2Vector(_args, 0), await self.builtin_funcs.llList2Vector(_args, 1), await self.builtin_funcs.llList2Float(_args, 2), await self.JSONTypeParse(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 3)))
                _ret_type = 2
            elif cond(req(190, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetStatus(await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(191, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetSubString(await self.builtin_funcs.llList2String(_args, 0), await self.builtin_funcs.llList2Integer(_args, 1), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 2)), list)
                _ret_type = 1
            elif cond(req(192, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetSunDirection(), list)
                _ret_type = 1
            elif cond(req(193, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetSunRotation(), list)
                _ret_type = 1
            elif cond(req(194, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetTexture(await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(195, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetTextureOffset(await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(196, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetTextureRot(await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(197, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetTextureScale(await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(199, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetTimeOfDay(), list)
                _ret_type = 1
            elif cond(req(200, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetTimestamp(), list)
                _ret_type = 1
            elif cond(req(201, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetTorque(), list)
                _ret_type = 1
            elif cond(req(202, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetUnixTime(), list)
                _ret_type = 1
            elif cond(req(203, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetUsedMemory(), list)
                _ret_type = 1
            elif cond(req(204, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetUsername(await self.builtin_funcs.llList2Key(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(205, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetVel(), list)
                _ret_type = 1
            elif cond(req(206, _lib_num)):
                _ret = await self.builtin_funcs.llGetVisualParams(await self.builtin_funcs.llList2Key(_args, 0), await self.JSONTypeParse(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 1)))
                _ret_type = 2
            elif cond(req(207, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGetWallclock(), list)
                _ret_type = 1
            elif cond(req(208, _lib_num)):
                await self.builtin_funcs.llGiveInventory(await self.builtin_funcs.llList2Key(_args, 0), await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 1))
            elif cond(req(209, _lib_num)):
                await self.builtin_funcs.llGiveInventoryList(await self.builtin_funcs.llList2Key(_args, 0), await self.builtin_funcs.llList2String(_args, 1), await self.JSONTypeParse(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 2)))
            elif cond(req(211, _lib_num)):
                await self.builtin_funcs.llGodLikeRezObject(await self.builtin_funcs.llList2Key(_args, 0), await self.builtin_funcs.llList2Vector(radd(_args, ((_args := []))), 1))
            elif cond(req(212, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGround(await self.builtin_funcs.llList2Vector(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(213, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGroundContour(await self.builtin_funcs.llList2Vector(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(214, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGroundNormal(await self.builtin_funcs.llList2Vector(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(215, _lib_num)):
                await self.builtin_funcs.llGroundRepel(await self.builtin_funcs.llList2Float(_args, 0), await self.builtin_funcs.llList2Integer(_args, 1), await self.builtin_funcs.llList2Float(radd(_args, ((_args := []))), 2))
            elif cond(req(216, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llGroundSlope(await self.builtin_funcs.llList2Vector(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(217, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llHTTPRequest(await self.builtin_funcs.llList2String(_args, 0), await self.JSONTypeParse(await self.builtin_funcs.llList2String(_args, 1)), await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 2)), list)
                _ret_type = 1
            elif cond(req(218, _lib_num)):
                await self.builtin_funcs.llHTTPResponse(await self.builtin_funcs.llList2Key(_args, 0), await self.builtin_funcs.llList2Integer(_args, 1), await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 2))
            elif cond(req(219, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llHash(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(220, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llInsertString(await self.builtin_funcs.llList2String(_args, 0), await self.builtin_funcs.llList2Integer(_args, 1), await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 2)), list)
                _ret_type = 1
            elif cond(req(221, _lib_num)):
                await self.builtin_funcs.llInstantMessage(await self.builtin_funcs.llList2Key(_args, 0), await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 1))
            elif cond(req(222, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llIntegerToBase64(await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(223, _lib_num)):
                _ret = await self.builtin_funcs.llJson2List(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0))
                _ret_type = 2
            elif cond(req(224, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llJsonGetValue(await self.builtin_funcs.llList2String(_args, 0), await self.JSONTypeParse(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 1))), list)
                _ret_type = 1
            elif cond(req(225, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llJsonSetValue(await self.builtin_funcs.llList2String(_args, 0), await self.JSONTypeParse(await self.builtin_funcs.llList2String(_args, 1)), await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 2)), list)
                _ret_type = 1
            elif cond(req(226, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llJsonValueType(await self.builtin_funcs.llList2String(_args, 0), await self.JSONTypeParse(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 1))), list)
                _ret_type = 1
            elif cond(req(227, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llKey2Name(await self.builtin_funcs.llList2Key(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(228, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llKeyCountKeyValue(), list)
                _ret_type = 1
            elif cond(req(229, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llKeysKeyValue(await self.builtin_funcs.llList2Integer(_args, 0), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 1)), list)
                _ret_type = 1
            elif cond(req(230, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llLinear2sRGB(await self.builtin_funcs.llList2Vector(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(231, _lib_num)):
                await self.builtin_funcs.llLinkParticleSystem(await self.builtin_funcs.llList2Integer(_args, 0), await self.JSONTypeParse(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 1)))
            elif cond(req(232, _lib_num)):
                await self.builtin_funcs.llLinkSitTarget(await self.builtin_funcs.llList2Integer(_args, 0), await self.builtin_funcs.llList2Vector(_args, 1), await self.builtin_funcs.llList2Rot(radd(_args, ((_args := []))), 2))
            elif cond(req(233, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llLinksetDataAvailable(), list)
                _ret_type = 1
            elif cond(req(234, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llLinksetDataCountKeys(), list)
                _ret_type = 1
            elif cond(req(235, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llLinksetDataDelete(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(236, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llLinksetDataDeleteProtected(await self.builtin_funcs.llList2String(_args, 0), await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 1)), list)
                _ret_type = 1
            elif cond(req(237, _lib_num)):
                _ret = await self.builtin_funcs.llLinksetDataFindKeys(await self.builtin_funcs.llList2String(_args, 0), await self.builtin_funcs.llList2Integer(_args, 1), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 2))
                _ret_type = 2
            elif cond(req(238, _lib_num)):
                _ret = await self.builtin_funcs.llLinksetDataListKeys(await self.builtin_funcs.llList2Integer(_args, 0), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 1))
                _ret_type = 2
            elif cond(req(239, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llLinksetDataRead(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(240, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llLinksetDataReadProtected(await self.builtin_funcs.llList2String(_args, 0), await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 1)), list)
                _ret_type = 1
            elif cond(req(241, _lib_num)):
                await self.builtin_funcs.llLinksetDataReset()
            elif cond(req(242, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llLinksetDataWrite(await self.builtin_funcs.llList2String(_args, 0), await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 1)), list)
                _ret_type = 1
            elif cond(req(243, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llLinksetDataWriteProtected(await self.builtin_funcs.llList2String(_args, 0), await self.builtin_funcs.llList2String(_args, 1), await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 2)), list)
                _ret_type = 1
            elif cond(req(244, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llList2CSV(await self.JSONTypeParse(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0))), list)
                _ret_type = 1
            elif cond(req(245, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llList2Float(await self.JSONTypeParse(await self.builtin_funcs.llList2String(_args, 0)), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 1)), list)
                _ret_type = 1
            elif cond(req(246, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llList2Integer(await self.JSONTypeParse(await self.builtin_funcs.llList2String(_args, 0)), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 1)), list)
                _ret_type = 1
            elif cond(req(247, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llList2Json(await self.builtin_funcs.llList2String(_args, 0), await self.JSONTypeParse(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 1))), list)
                _ret_type = 1
            elif cond(req(248, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llList2Key(await self.JSONTypeParse(await self.builtin_funcs.llList2String(_args, 0)), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 1)), list)
                _ret_type = 1
            elif cond(req(249, _lib_num)):
                _ret = await self.builtin_funcs.llList2List(await self.JSONTypeParse(await self.builtin_funcs.llList2String(_args, 0)), await self.builtin_funcs.llList2Integer(_args, 1), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 2))
                _ret_type = 2
            elif cond(req(250, _lib_num)):
                _ret = await self.builtin_funcs.llList2ListStrided(await self.JSONTypeParse(await self.builtin_funcs.llList2String(_args, 0)), await self.builtin_funcs.llList2Integer(_args, 1), await self.builtin_funcs.llList2Integer(_args, 2), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 3))
                _ret_type = 2
            elif cond(req(251, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llList2Rot(await self.JSONTypeParse(await self.builtin_funcs.llList2String(_args, 0)), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 1)), list)
                _ret_type = 1
            elif cond(req(252, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llList2String(await self.JSONTypeParse(await self.builtin_funcs.llList2String(_args, 0)), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 1)), list)
                _ret_type = 1
            elif cond(req(253, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llList2Vector(await self.JSONTypeParse(await self.builtin_funcs.llList2String(_args, 0)), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 1)), list)
                _ret_type = 1
            elif cond(req(254, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llListFindList(await self.JSONTypeParse(await self.builtin_funcs.llList2String(_args, 0)), await self.JSONTypeParse(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 1))), list)
                _ret_type = 1
            elif cond(req(255, _lib_num)):
                _ret = await self.builtin_funcs.llListInsertList(await self.JSONTypeParse(await self.builtin_funcs.llList2String(_args, 0)), await self.JSONTypeParse(await self.builtin_funcs.llList2String(_args, 1)), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 2))
                _ret_type = 2
            elif cond(req(256, _lib_num)):
                _ret = await self.builtin_funcs.llListRandomize(await self.JSONTypeParse(await self.builtin_funcs.llList2String(_args, 0)), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 1))
                _ret_type = 2
            elif cond(req(257, _lib_num)):
                _ret = await self.builtin_funcs.llListReplaceList(await self.JSONTypeParse(await self.builtin_funcs.llList2String(_args, 0)), await self.JSONTypeParse(await self.builtin_funcs.llList2String(_args, 1)), await self.builtin_funcs.llList2Integer(_args, 2), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 3))
                _ret_type = 2
            elif cond(req(258, _lib_num)):
                _ret = await self.builtin_funcs.llListSort(await self.JSONTypeParse(await self.builtin_funcs.llList2String(_args, 0)), await self.builtin_funcs.llList2Integer(_args, 1), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 2))
                _ret_type = 2
            elif cond(req(259, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llListStatistics(await self.builtin_funcs.llList2Integer(_args, 0), await self.JSONTypeParse(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 1))), list)
                _ret_type = 1
            elif cond(req(263, _lib_num)):
                await self.builtin_funcs.llLoadURL(await self.builtin_funcs.llList2Key(_args, 0), await self.builtin_funcs.llList2String(_args, 1), await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 2))
            elif cond(req(264, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llLog(await self.builtin_funcs.llList2Float(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(265, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llLog10(await self.builtin_funcs.llList2Float(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(267, _lib_num)):
                await self.builtin_funcs.llLoopSound(await self.builtin_funcs.llList2String(_args, 0), await self.builtin_funcs.llList2Float(radd(_args, ((_args := []))), 1))
            elif cond(req(268, _lib_num)):
                await self.builtin_funcs.llLoopSoundMaster(await self.builtin_funcs.llList2String(_args, 0), await self.builtin_funcs.llList2Float(radd(_args, ((_args := []))), 1))
            elif cond(req(269, _lib_num)):
                await self.builtin_funcs.llLoopSoundSlave(await self.builtin_funcs.llList2String(_args, 0), await self.builtin_funcs.llList2Float(radd(_args, ((_args := []))), 1))
            elif cond(req(270, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llMD5String(await self.builtin_funcs.llList2String(_args, 0), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 1)), list)
                _ret_type = 1
            elif cond(req(271, _lib_num)):
                await self.builtin_funcs.llMakeExplosion(await self.builtin_funcs.llList2Integer(_args, 0), await self.builtin_funcs.llList2Float(_args, 1), await self.builtin_funcs.llList2Float(_args, 2), await self.builtin_funcs.llList2Float(_args, 3), await self.builtin_funcs.llList2Float(_args, 4), await self.builtin_funcs.llList2String(_args, 5), await self.builtin_funcs.llList2Vector(radd(_args, ((_args := []))), 6))
            elif cond(req(272, _lib_num)):
                await self.builtin_funcs.llMakeFire(await self.builtin_funcs.llList2Integer(_args, 0), await self.builtin_funcs.llList2Float(_args, 1), await self.builtin_funcs.llList2Float(_args, 2), await self.builtin_funcs.llList2Float(_args, 3), await self.builtin_funcs.llList2Float(_args, 4), await self.builtin_funcs.llList2String(_args, 5), await self.builtin_funcs.llList2Vector(radd(_args, ((_args := []))), 6))
            elif cond(req(273, _lib_num)):
                await self.builtin_funcs.llMakeFountain(await self.builtin_funcs.llList2Integer(_args, 0), await self.builtin_funcs.llList2Float(_args, 1), await self.builtin_funcs.llList2Float(_args, 2), await self.builtin_funcs.llList2Float(_args, 3), await self.builtin_funcs.llList2Float(_args, 4), await self.builtin_funcs.llList2Integer(_args, 5), await self.builtin_funcs.llList2String(_args, 6), await self.builtin_funcs.llList2Vector(_args, 7), await self.builtin_funcs.llList2Float(radd(_args, ((_args := []))), 8))
            elif cond(req(274, _lib_num)):
                await self.builtin_funcs.llMakeSmoke(await self.builtin_funcs.llList2Integer(_args, 0), await self.builtin_funcs.llList2Float(_args, 1), await self.builtin_funcs.llList2Float(_args, 2), await self.builtin_funcs.llList2Float(_args, 3), await self.builtin_funcs.llList2Float(_args, 4), await self.builtin_funcs.llList2String(_args, 5), await self.builtin_funcs.llList2Vector(radd(_args, ((_args := []))), 6))
            elif cond(req(276, _lib_num)):
                await self.builtin_funcs.llMapDestination(await self.builtin_funcs.llList2String(_args, 0), await self.builtin_funcs.llList2Vector(_args, 1), await self.builtin_funcs.llList2Vector(radd(_args, ((_args := []))), 2))
            elif cond(req(278, _lib_num)):
                await self.builtin_funcs.llMinEventDelay(await self.builtin_funcs.llList2Float(radd(_args, ((_args := []))), 0))
            elif cond(req(279, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llModPow(await self.builtin_funcs.llList2Integer(_args, 0), await self.builtin_funcs.llList2Integer(_args, 1), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 2)), list)
                _ret_type = 1
            elif cond(req(280, _lib_num)):
                await self.builtin_funcs.llModifyLand(await self.builtin_funcs.llList2Integer(_args, 0), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 1))
            elif cond(req(282, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llName2Key(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(283, _lib_num)):
                await self.builtin_funcs.llNavigateTo(await self.builtin_funcs.llList2Vector(_args, 0), await self.JSONTypeParse(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 1)))
            elif cond(req(284, _lib_num)):
                await self.builtin_funcs.llOffsetTexture(await self.builtin_funcs.llList2Float(_args, 0), await self.builtin_funcs.llList2Float(_args, 1), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 2))
            elif cond(req(285, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llOpenFloater(await self.builtin_funcs.llList2String(_args, 0), await self.builtin_funcs.llList2String(_args, 1), await self.JSONTypeParse(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 2))), list)
                _ret_type = 1
            elif cond(req(286, _lib_num)):
                await self.builtin_funcs.llOpenRemoteDataChannel()
            elif cond(req(287, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llOrd(await self.builtin_funcs.llList2String(_args, 0), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 1)), list)
                _ret_type = 1
            elif cond(req(288, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llOverMyLand(await self.builtin_funcs.llList2Key(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(289, _lib_num)):
                await self.builtin_funcs.llOwnerSay(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0))
            elif cond(req(290, _lib_num)):
                await self.builtin_funcs.llParcelMediaCommandList(await self.JSONTypeParse(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0)))
            elif cond(req(291, _lib_num)):
                _ret = await self.builtin_funcs.llParcelMediaQuery(await self.JSONTypeParse(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0)))
                _ret_type = 2
            elif cond(req(292, _lib_num)):
                _ret = await self.builtin_funcs.llParseString2List(await self.builtin_funcs.llList2String(_args, 0), await self.JSONTypeParse(await self.builtin_funcs.llList2String(_args, 1)), await self.JSONTypeParse(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 2)))
                _ret_type = 2
            elif cond(req(293, _lib_num)):
                _ret = await self.builtin_funcs.llParseStringKeepNulls(await self.builtin_funcs.llList2String(_args, 0), await self.JSONTypeParse(await self.builtin_funcs.llList2String(_args, 1)), await self.JSONTypeParse(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 2)))
                _ret_type = 2
            elif cond(req(294, _lib_num)):
                await self.builtin_funcs.llParticleSystem(await self.JSONTypeParse(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0)))
            elif cond(req(295, _lib_num)):
                await self.builtin_funcs.llPassCollisions(await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 0))
            elif cond(req(296, _lib_num)):
                await self.builtin_funcs.llPassTouches(await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 0))
            elif cond(req(297, _lib_num)):
                await self.builtin_funcs.llPatrolPoints(await self.JSONTypeParse(await self.builtin_funcs.llList2String(_args, 0)), await self.JSONTypeParse(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 1)))
            elif cond(req(298, _lib_num)):
                await self.builtin_funcs.llPlaySound(await self.builtin_funcs.llList2String(_args, 0), await self.builtin_funcs.llList2Float(radd(_args, ((_args := []))), 1))
            elif cond(req(299, _lib_num)):
                await self.builtin_funcs.llPlaySoundSlave(await self.builtin_funcs.llList2String(_args, 0), await self.builtin_funcs.llList2Float(radd(_args, ((_args := []))), 1))
            elif cond(req(300, _lib_num)):
                await self.builtin_funcs.llPointAt(await self.builtin_funcs.llList2Vector(radd(_args, ((_args := []))), 0))
            elif cond(req(301, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llPow(await self.builtin_funcs.llList2Float(_args, 0), await self.builtin_funcs.llList2Float(radd(_args, ((_args := []))), 1)), list)
                _ret_type = 1
            elif cond(req(302, _lib_num)):
                await self.builtin_funcs.llPreloadSound(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0))
            elif cond(req(303, _lib_num)):
                await self.builtin_funcs.llPursue(await self.builtin_funcs.llList2Key(_args, 0), await self.JSONTypeParse(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 1)))
            elif cond(req(304, _lib_num)):
                await self.builtin_funcs.llPushObject(await self.builtin_funcs.llList2Key(_args, 0), await self.builtin_funcs.llList2Vector(_args, 1), await self.builtin_funcs.llList2Vector(_args, 2), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 3))
            elif cond(req(305, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llReadKeyValue(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(306, _lib_num)):
                await self.builtin_funcs.llRefreshPrimURL()
            elif cond(req(307, _lib_num)):
                await self.builtin_funcs.llRegionSay(await self.builtin_funcs.llList2Integer(_args, 0), await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 1))
            elif cond(req(308, _lib_num)):
                await self.builtin_funcs.llRegionSayTo(await self.builtin_funcs.llList2Key(_args, 0), await self.builtin_funcs.llList2Integer(_args, 1), await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 2))
            elif cond(req(309, _lib_num)):
                await self.builtin_funcs.llReleaseCamera(await self.builtin_funcs.llList2Key(radd(_args, ((_args := []))), 0))
            elif cond(req(311, _lib_num)):
                await self.builtin_funcs.llReleaseURL(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0))
            elif cond(req(312, _lib_num)):
                await self.builtin_funcs.llRemoteDataReply(await self.builtin_funcs.llList2Key(_args, 0), await self.builtin_funcs.llList2Key(_args, 1), await self.builtin_funcs.llList2String(_args, 2), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 3))
            elif cond(req(313, _lib_num)):
                await self.builtin_funcs.llRemoteDataSetRegion()
            elif cond(req(314, _lib_num)):
                await self.builtin_funcs.llRemoteLoadScript(await self.builtin_funcs.llList2Key(_args, 0), await self.builtin_funcs.llList2String(_args, 1), await self.builtin_funcs.llList2Integer(_args, 2), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 3))
            elif cond(req(315, _lib_num)):
                await self.builtin_funcs.llRemoteLoadScriptPin(await self.builtin_funcs.llList2Key(_args, 0), await self.builtin_funcs.llList2String(_args, 1), await self.builtin_funcs.llList2Integer(_args, 2), await self.builtin_funcs.llList2Integer(_args, 3), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 4))
            elif cond(req(316, _lib_num)):
                await self.builtin_funcs.llRemoveFromLandBanList(await self.builtin_funcs.llList2Key(radd(_args, ((_args := []))), 0))
            elif cond(req(317, _lib_num)):
                await self.builtin_funcs.llRemoveFromLandPassList(await self.builtin_funcs.llList2Key(radd(_args, ((_args := []))), 0))
            elif cond(req(318, _lib_num)):
                await self.builtin_funcs.llRemoveInventory(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0))
            elif cond(req(319, _lib_num)):
                await self.builtin_funcs.llRemoveVehicleFlags(await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 0))
            elif cond(req(320, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llReplaceAgentEnvironment(await self.builtin_funcs.llList2Key(_args, 0), await self.builtin_funcs.llList2Float(_args, 1), await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 2)), list)
                _ret_type = 1
            elif cond(req(321, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llReplaceEnvironment(await self.builtin_funcs.llList2Vector(_args, 0), await self.builtin_funcs.llList2String(_args, 1), await self.builtin_funcs.llList2Integer(_args, 2), await self.builtin_funcs.llList2Integer(_args, 3), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 4)), list)
                _ret_type = 1
            elif cond(req(322, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llRequestAgentData(await self.builtin_funcs.llList2Key(_args, 0), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 1)), list)
                _ret_type = 1
            elif cond(req(323, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llRequestDisplayName(await self.builtin_funcs.llList2Key(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(324, _lib_num)):
                await self.builtin_funcs.llRequestExperiencePermissions(await self.builtin_funcs.llList2Key(_args, 0), await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 1))
            elif cond(req(325, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llRequestInventoryData(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(327, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llRequestSecureURL(), list)
                _ret_type = 1
            elif cond(req(328, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llRequestSimulatorData(await self.builtin_funcs.llList2String(_args, 0), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 1)), list)
                _ret_type = 1
            elif cond(req(329, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llRequestURL(), list)
                _ret_type = 1
            elif cond(req(330, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llRequestUserKey(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(331, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llRequestUsername(await self.builtin_funcs.llList2Key(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(333, _lib_num)):
                await self.builtin_funcs.llResetLandBanList()
            elif cond(req(334, _lib_num)):
                await self.builtin_funcs.llResetLandPassList()
            elif cond(req(335, _lib_num)):
                await self.builtin_funcs.llResetOtherScript(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0))
            elif cond(req(340, _lib_num)):
                await self.builtin_funcs.llRezAtRoot(await self.builtin_funcs.llList2String(_args, 0), await self.builtin_funcs.llList2Vector(_args, 1), await self.builtin_funcs.llList2Vector(_args, 2), await self.builtin_funcs.llList2Rot(_args, 3), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 4))
            elif cond(req(341, _lib_num)):
                await self.builtin_funcs.llRezObject(await self.builtin_funcs.llList2String(_args, 0), await self.builtin_funcs.llList2Vector(_args, 1), await self.builtin_funcs.llList2Vector(_args, 2), await self.builtin_funcs.llList2Rot(_args, 3), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 4))
            elif cond(req(342, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llRot2Angle(await self.builtin_funcs.llList2Rot(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(343, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llRot2Axis(await self.builtin_funcs.llList2Rot(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(344, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llRot2Euler(await self.builtin_funcs.llList2Rot(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(345, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llRot2Fwd(await self.builtin_funcs.llList2Rot(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(346, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llRot2Left(await self.builtin_funcs.llList2Rot(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(347, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llRot2Up(await self.builtin_funcs.llList2Rot(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(348, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llRotBetween(await self.builtin_funcs.llList2Vector(_args, 0), await self.builtin_funcs.llList2Vector(radd(_args, ((_args := []))), 1)), list)
                _ret_type = 1
            elif cond(req(350, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llRotTarget(await self.builtin_funcs.llList2Rot(_args, 0), await self.builtin_funcs.llList2Float(radd(_args, ((_args := []))), 1)), list)
                _ret_type = 1
            elif cond(req(351, _lib_num)):
                await self.builtin_funcs.llRotTargetRemove(await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 0))
            elif cond(req(352, _lib_num)):
                await self.builtin_funcs.llRotateTexture(await self.builtin_funcs.llList2Float(_args, 0), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 1))
            elif cond(req(353, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llRound(await self.builtin_funcs.llList2Float(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(354, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llSHA1String(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(355, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llSHA256String(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(356, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llSameGroup(await self.builtin_funcs.llList2Key(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(357, _lib_num)):
                await self.builtin_funcs.llSay(await self.builtin_funcs.llList2Integer(_args, 0), await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 1))
            elif cond(req(358, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llScaleByFactor(await self.builtin_funcs.llList2Float(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(359, _lib_num)):
                await self.builtin_funcs.llScaleTexture(await self.builtin_funcs.llList2Float(_args, 0), await self.builtin_funcs.llList2Float(_args, 1), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 2))
            elif cond(req(360, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llScriptDanger(await self.builtin_funcs.llList2Vector(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(361, _lib_num)):
                await self.builtin_funcs.llScriptProfiler(await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 0))
            elif cond(req(362, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llSendRemoteData(await self.builtin_funcs.llList2Key(_args, 0), await self.builtin_funcs.llList2String(_args, 1), await self.builtin_funcs.llList2Integer(_args, 2), await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 3)), list)
                _ret_type = 1
            elif cond(req(363, _lib_num)):
                await self.builtin_funcs.llSensor(await self.builtin_funcs.llList2String(_args, 0), await self.builtin_funcs.llList2Key(_args, 1), await self.builtin_funcs.llList2Integer(_args, 2), await self.builtin_funcs.llList2Float(_args, 3), await self.builtin_funcs.llList2Float(radd(_args, ((_args := []))), 4))
            elif cond(req(364, _lib_num)):
                await self.builtin_funcs.llSensorRemove()
            elif cond(req(365, _lib_num)):
                await self.builtin_funcs.llSensorRepeat(await self.builtin_funcs.llList2String(_args, 0), await self.builtin_funcs.llList2Key(_args, 1), await self.builtin_funcs.llList2Integer(_args, 2), await self.builtin_funcs.llList2Float(_args, 3), await self.builtin_funcs.llList2Float(_args, 4), await self.builtin_funcs.llList2Float(radd(_args, ((_args := []))), 5))
            elif cond(req(366, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llSetAgentEnvironment(await self.builtin_funcs.llList2Key(_args, 0), await self.builtin_funcs.llList2Float(_args, 1), await self.JSONTypeParse(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 2))), list)
                _ret_type = 1
            elif cond(req(367, _lib_num)):
                await self.builtin_funcs.llSetAlpha(await self.builtin_funcs.llList2Float(_args, 0), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 1))
            elif cond(req(368, _lib_num)):
                await self.builtin_funcs.llSetAngularVelocity(await self.builtin_funcs.llList2Vector(_args, 0), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 1))
            elif cond(req(370, _lib_num)):
                await self.builtin_funcs.llSetBuoyancy(await self.builtin_funcs.llList2Float(radd(_args, ((_args := []))), 0))
            elif cond(req(371, _lib_num)):
                await self.builtin_funcs.llSetCameraAtOffset(await self.builtin_funcs.llList2Vector(radd(_args, ((_args := []))), 0))
            elif cond(req(372, _lib_num)):
                await self.builtin_funcs.llSetCameraEyeOffset(await self.builtin_funcs.llList2Vector(radd(_args, ((_args := []))), 0))
            elif cond(req(374, _lib_num)):
                await self.builtin_funcs.llSetClickAction(await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 0))
            elif cond(req(375, _lib_num)):
                await self.builtin_funcs.llSetColor(await self.builtin_funcs.llList2Vector(_args, 0), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 1))
            elif cond(req(376, _lib_num)):
                await self.builtin_funcs.llSetContentType(await self.builtin_funcs.llList2Key(_args, 0), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 1))
            elif cond(req(377, _lib_num)):
                await self.builtin_funcs.llSetDamage(await self.builtin_funcs.llList2Float(radd(_args, ((_args := []))), 0))
            elif cond(req(378, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llSetEnvironment(await self.builtin_funcs.llList2Vector(_args, 0), await self.JSONTypeParse(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 1))), list)
                _ret_type = 1
            elif cond(req(379, _lib_num)):
                await self.builtin_funcs.llSetForce(await self.builtin_funcs.llList2Vector(_args, 0), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 1))
            elif cond(req(380, _lib_num)):
                await self.builtin_funcs.llSetForceAndTorque(await self.builtin_funcs.llList2Vector(_args, 0), await self.builtin_funcs.llList2Vector(_args, 1), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 2))
            elif cond(req(381, _lib_num)):
                await self.builtin_funcs.llSetHoverHeight(await self.builtin_funcs.llList2Float(_args, 0), await self.builtin_funcs.llList2Integer(_args, 1), await self.builtin_funcs.llList2Float(radd(_args, ((_args := []))), 2))
            elif cond(req(382, _lib_num)):
                await self.builtin_funcs.llSetInventoryPermMask(await self.builtin_funcs.llList2String(_args, 0), await self.builtin_funcs.llList2Integer(_args, 1), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 2))
            elif cond(req(383, _lib_num)):
                await self.builtin_funcs.llSetKeyframedMotion(await self.JSONTypeParse(await self.builtin_funcs.llList2String(_args, 0)), await self.JSONTypeParse(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 1)))
            elif cond(req(384, _lib_num)):
                await self.builtin_funcs.llSetLinkAlpha(await self.builtin_funcs.llList2Integer(_args, 0), await self.builtin_funcs.llList2Float(_args, 1), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 2))
            elif cond(req(385, _lib_num)):
                await self.builtin_funcs.llSetLinkCamera(await self.builtin_funcs.llList2Integer(_args, 0), await self.builtin_funcs.llList2Vector(_args, 1), await self.builtin_funcs.llList2Vector(radd(_args, ((_args := []))), 2))
            elif cond(req(386, _lib_num)):
                await self.builtin_funcs.llSetLinkColor(await self.builtin_funcs.llList2Integer(_args, 0), await self.builtin_funcs.llList2Vector(_args, 1), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 2))
            elif cond(req(387, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llSetLinkMedia(await self.builtin_funcs.llList2Integer(_args, 0), await self.builtin_funcs.llList2Integer(_args, 1), await self.JSONTypeParse(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 2))), list)
                _ret_type = 1
            elif cond(req(388, _lib_num)):
                await self.builtin_funcs.llSetLinkPrimitiveParams(await self.builtin_funcs.llList2Integer(_args, 0), await self.JSONTypeParse(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 1)))
            elif cond(req(389, _lib_num)):
                await self.builtin_funcs.llSetLinkPrimitiveParamsFast(await self.builtin_funcs.llList2Integer(_args, 0), await self.JSONTypeParse(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 1)))
            elif cond(req(390, _lib_num)):
                await self.builtin_funcs.llSetLinkTexture(await self.builtin_funcs.llList2Integer(_args, 0), await self.builtin_funcs.llList2String(_args, 1), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 2))
            elif cond(req(391, _lib_num)):
                await self.builtin_funcs.llSetLinkTextureAnim(await self.builtin_funcs.llList2Integer(_args, 0), await self.builtin_funcs.llList2Integer(_args, 1), await self.builtin_funcs.llList2Integer(_args, 2), await self.builtin_funcs.llList2Integer(_args, 3), await self.builtin_funcs.llList2Integer(_args, 4), await self.builtin_funcs.llList2Float(_args, 5), await self.builtin_funcs.llList2Float(_args, 6), await self.builtin_funcs.llList2Float(radd(_args, ((_args := []))), 7))
            elif cond(req(392, _lib_num)):
                await self.builtin_funcs.llSetLocalRot(await self.builtin_funcs.llList2Rot(radd(_args, ((_args := []))), 0))
            elif cond(req(393, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llSetMemoryLimit(await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(394, _lib_num)):
                await self.builtin_funcs.llSetObjectDesc(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0))
            elif cond(req(395, _lib_num)):
                await self.builtin_funcs.llSetObjectName(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0))
            elif cond(req(396, _lib_num)):
                await self.builtin_funcs.llSetObjectPermMask(await self.builtin_funcs.llList2Integer(_args, 0), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 1))
            elif cond(req(397, _lib_num)):
                await self.builtin_funcs.llSetParcelMusicURL(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0))
            elif cond(req(398, _lib_num)):
                await self.builtin_funcs.llSetPayPrice(await self.builtin_funcs.llList2Integer(_args, 0), await self.JSONTypeParse(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 1)))
            elif cond(req(399, _lib_num)):
                await self.builtin_funcs.llSetPhysicsMaterial(await self.builtin_funcs.llList2Integer(_args, 0), await self.builtin_funcs.llList2Float(_args, 1), await self.builtin_funcs.llList2Float(_args, 2), await self.builtin_funcs.llList2Float(_args, 3), await self.builtin_funcs.llList2Float(radd(_args, ((_args := []))), 4))
            elif cond(req(400, _lib_num)):
                await self.builtin_funcs.llSetPos(await self.builtin_funcs.llList2Vector(radd(_args, ((_args := []))), 0))
            elif cond(req(401, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llSetPrimMediaParams(await self.builtin_funcs.llList2Integer(_args, 0), await self.JSONTypeParse(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 1))), list)
                _ret_type = 1
            elif cond(req(402, _lib_num)):
                await self.builtin_funcs.llSetPrimURL(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0))
            elif cond(req(403, _lib_num)):
                await self.builtin_funcs.llSetPrimitiveParams(await self.JSONTypeParse(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0)))
            elif cond(req(404, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llSetRegionPos(await self.builtin_funcs.llList2Vector(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(405, _lib_num)):
                await self.builtin_funcs.llSetRemoteScriptAccessPin(await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 0))
            elif cond(req(406, _lib_num)):
                await self.builtin_funcs.llSetRot(await self.builtin_funcs.llList2Rot(radd(_args, ((_args := []))), 0))
            elif cond(req(407, _lib_num)):
                await self.builtin_funcs.llSetScale(await self.builtin_funcs.llList2Vector(radd(_args, ((_args := []))), 0))
            elif cond(req(408, _lib_num)):
                await self.builtin_funcs.llSetScriptState(await self.builtin_funcs.llList2String(_args, 0), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 1))
            elif cond(req(409, _lib_num)):
                await self.builtin_funcs.llSetSitText(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0))
            elif cond(req(410, _lib_num)):
                await self.builtin_funcs.llSetSoundQueueing(await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 0))
            elif cond(req(411, _lib_num)):
                await self.builtin_funcs.llSetSoundRadius(await self.builtin_funcs.llList2Float(radd(_args, ((_args := []))), 0))
            elif cond(req(412, _lib_num)):
                await self.builtin_funcs.llSetStatus(await self.builtin_funcs.llList2Integer(_args, 0), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 1))
            elif cond(req(413, _lib_num)):
                await self.builtin_funcs.llSetText(await self.builtin_funcs.llList2String(_args, 0), await self.builtin_funcs.llList2Vector(_args, 1), await self.builtin_funcs.llList2Float(radd(_args, ((_args := []))), 2))
            elif cond(req(414, _lib_num)):
                await self.builtin_funcs.llSetTexture(await self.builtin_funcs.llList2String(_args, 0), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 1))
            elif cond(req(415, _lib_num)):
                await self.builtin_funcs.llSetTextureAnim(await self.builtin_funcs.llList2Integer(_args, 0), await self.builtin_funcs.llList2Integer(_args, 1), await self.builtin_funcs.llList2Integer(_args, 2), await self.builtin_funcs.llList2Integer(_args, 3), await self.builtin_funcs.llList2Float(_args, 4), await self.builtin_funcs.llList2Float(_args, 5), await self.builtin_funcs.llList2Float(radd(_args, ((_args := []))), 6))
            elif cond(req(417, _lib_num)):
                await self.builtin_funcs.llSetTorque(await self.builtin_funcs.llList2Vector(_args, 0), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 1))
            elif cond(req(418, _lib_num)):
                await self.builtin_funcs.llSetTouchText(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0))
            elif cond(req(419, _lib_num)):
                await self.builtin_funcs.llSetVehicleFlags(await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 0))
            elif cond(req(420, _lib_num)):
                await self.builtin_funcs.llSetVehicleFloatParam(await self.builtin_funcs.llList2Integer(_args, 0), await self.builtin_funcs.llList2Float(radd(_args, ((_args := []))), 1))
            elif cond(req(421, _lib_num)):
                await self.builtin_funcs.llSetVehicleRotationParam(await self.builtin_funcs.llList2Integer(_args, 0), await self.builtin_funcs.llList2Rot(radd(_args, ((_args := []))), 1))
            elif cond(req(422, _lib_num)):
                await self.builtin_funcs.llSetVehicleType(await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 0))
            elif cond(req(423, _lib_num)):
                await self.builtin_funcs.llSetVehicleVectorParam(await self.builtin_funcs.llList2Integer(_args, 0), await self.builtin_funcs.llList2Vector(radd(_args, ((_args := []))), 1))
            elif cond(req(424, _lib_num)):
                await self.builtin_funcs.llSetVelocity(await self.builtin_funcs.llList2Vector(_args, 0), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 1))
            elif cond(req(425, _lib_num)):
                await self.builtin_funcs.llShout(await self.builtin_funcs.llList2Integer(_args, 0), await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 1))
            elif cond(req(426, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llSin(await self.builtin_funcs.llList2Float(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(427, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llSitOnLink(await self.builtin_funcs.llList2Key(_args, 0), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 1)), list)
                _ret_type = 1
            elif cond(req(428, _lib_num)):
                await self.builtin_funcs.llSitTarget(await self.builtin_funcs.llList2Vector(_args, 0), await self.builtin_funcs.llList2Rot(radd(_args, ((_args := []))), 1))
            elif cond(req(430, _lib_num)):
                await self.builtin_funcs.llSound(await self.builtin_funcs.llList2String(_args, 0), await self.builtin_funcs.llList2Float(_args, 1), await self.builtin_funcs.llList2Integer(_args, 2), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 3))
            elif cond(req(431, _lib_num)):
                await self.builtin_funcs.llSoundPreload(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0))
            elif cond(req(432, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llSqrt(await self.builtin_funcs.llList2Float(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(434, _lib_num)):
                await self.builtin_funcs.llStartObjectAnimation(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0))
            elif cond(req(436, _lib_num)):
                await self.builtin_funcs.llStopHover()
            elif cond(req(439, _lib_num)):
                await self.builtin_funcs.llStopObjectAnimation(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0))
            elif cond(req(440, _lib_num)):
                await self.builtin_funcs.llStopPointAt()
            elif cond(req(441, _lib_num)):
                await self.builtin_funcs.llStopSound()
            elif cond(req(442, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llStringLength(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(443, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llStringToBase64(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(444, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llStringTrim(await self.builtin_funcs.llList2String(_args, 0), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 1)), list)
                _ret_type = 1
            elif cond(req(445, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llSubStringIndex(await self.builtin_funcs.llList2String(_args, 0), await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 1)), list)
                _ret_type = 1
            elif cond(req(446, _lib_num)):
                await self.builtin_funcs.llTakeCamera(await self.builtin_funcs.llList2Key(radd(_args, ((_args := []))), 0))
            elif cond(req(448, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llTan(await self.builtin_funcs.llList2Float(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(449, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llTarget(await self.builtin_funcs.llList2Vector(_args, 0), await self.builtin_funcs.llList2Float(radd(_args, ((_args := []))), 1)), list)
                _ret_type = 1
            elif cond(req(450, _lib_num)):
                await self.builtin_funcs.llTargetOmega(await self.builtin_funcs.llList2Vector(_args, 0), await self.builtin_funcs.llList2Float(_args, 1), await self.builtin_funcs.llList2Float(radd(_args, ((_args := []))), 2))
            elif cond(req(451, _lib_num)):
                await self.builtin_funcs.llTargetRemove(await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 0))
            elif cond(req(452, _lib_num)):
                await self.builtin_funcs.llTargetedEmail(await self.builtin_funcs.llList2Integer(_args, 0), await self.builtin_funcs.llList2String(_args, 1), await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 2))
            elif cond(req(454, _lib_num)):
                await self.builtin_funcs.llTeleportAgentGlobalCoords(await self.builtin_funcs.llList2Key(_args, 0), await self.builtin_funcs.llList2Vector(_args, 1), await self.builtin_funcs.llList2Vector(_args, 2), await self.builtin_funcs.llList2Vector(radd(_args, ((_args := []))), 3))
            elif cond(req(455, _lib_num)):
                await self.builtin_funcs.llTeleportAgentHome(await self.builtin_funcs.llList2Key(radd(_args, ((_args := []))), 0))
            elif cond(req(456, _lib_num)):
                await self.builtin_funcs.llTextBox(await self.builtin_funcs.llList2Key(_args, 0), await self.builtin_funcs.llList2String(_args, 1), await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 2))
            elif cond(req(457, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llToLower(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(458, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llToUpper(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(460, _lib_num)):
                await self.builtin_funcs.llTriggerSound(await self.builtin_funcs.llList2String(_args, 0), await self.builtin_funcs.llList2Float(radd(_args, ((_args := []))), 1))
            elif cond(req(461, _lib_num)):
                await self.builtin_funcs.llTriggerSoundLimited(await self.builtin_funcs.llList2String(_args, 0), await self.builtin_funcs.llList2Float(_args, 1), await self.builtin_funcs.llList2Vector(_args, 2), await self.builtin_funcs.llList2Vector(radd(_args, ((_args := []))), 3))
            elif cond(req(462, _lib_num)):
                await self.builtin_funcs.llUnSit(await self.builtin_funcs.llList2Key(radd(_args, ((_args := []))), 0))
            elif cond(req(463, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llUnescapeURL(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(464, _lib_num)):
                await self.builtin_funcs.llUpdateCharacter(await self.JSONTypeParse(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 0)))
            elif cond(req(465, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llUpdateKeyValue(await self.builtin_funcs.llList2String(_args, 0), await self.builtin_funcs.llList2String(_args, 1), await self.builtin_funcs.llList2Integer(_args, 2), await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 3)), list)
                _ret_type = 1
            elif cond(req(466, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llVecDist(await self.builtin_funcs.llList2Vector(_args, 0), await self.builtin_funcs.llList2Vector(radd(_args, ((_args := []))), 1)), list)
                _ret_type = 1
            elif cond(req(467, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llVecMag(await self.builtin_funcs.llList2Vector(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(468, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llVecNorm(await self.builtin_funcs.llList2Vector(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(469, _lib_num)):
                await self.builtin_funcs.llVolumeDetect(await self.builtin_funcs.llList2Integer(radd(_args, ((_args := []))), 0))
            elif cond(req(470, _lib_num)):
                await self.builtin_funcs.llWanderWithin(await self.builtin_funcs.llList2Vector(_args, 0), await self.builtin_funcs.llList2Vector(_args, 1), await self.JSONTypeParse(await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 2)))
            elif cond(req(471, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llWater(await self.builtin_funcs.llList2Vector(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(472, _lib_num)):
                await self.builtin_funcs.llWhisper(await self.builtin_funcs.llList2Integer(_args, 0), await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 1))
            elif cond(req(473, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llWind(await self.builtin_funcs.llList2Vector(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            elif cond(req(474, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llXorBase64(await self.builtin_funcs.llList2String(_args, 0), await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 1)), list)
                _ret_type = 1
            elif cond(req(475, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llXorBase64Strings(await self.builtin_funcs.llList2String(_args, 0), await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 1)), list)
                _ret_type = 1
            elif cond(req(476, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llXorBase64StringsCorrect(await self.builtin_funcs.llList2String(_args, 0), await self.builtin_funcs.llList2String(radd(_args, ((_args := []))), 1)), list)
                _ret_type = 1
            elif cond(req(477, _lib_num)):
                _ret = typecast(await self.builtin_funcs.llsRGB2Linear(await self.builtin_funcs.llList2Vector(radd(_args, ((_args := []))), 0)), list)
                _ret_type = 1
            else:
                return
            _args = []
            _ret_str: str = ""
            if cond(boolnot(_no_wait)):
                if cond(_ret_type):
                    _ret_str = await self.JSONTypeDump(radd(_ret, ((_ret := []))))
                await self.builtin_funcs.llMessageLinked((typecast(-4, int)), 61952, radd(_ret_str, ((_ret_str := ""))), typecast(typecast(_ret_type, str), Key))

