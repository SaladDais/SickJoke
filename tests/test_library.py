#!/usr/bin/env python
import unittest
import unittest.mock
from typing import *

from . import serialize_list, deserialize_list, BaseMessagingTestCase, LinkMessage

from lummao.vendor.lslopt.lslcommon import Vector, Quaternion, Key

from pythonized import library
from constants import *


class LibraryTests(BaseMessagingTestCase):
    script: library.Script

    async def asyncSetUp(self):
        self.script = library.Script()
        await super().asyncSetUp()
        # Execute state_entry()
        await self.script.execute()

    async def _call_library_function(self, lib_num: int, *args, no_wait=False):
        built_args = []
        # Any lists in our arguments must be pre-converted to tight lists.
        for arg in args:
            if isinstance(arg, (tuple, list)):
                arg = await serialize_list(arg)
            built_args.append(arg)

        serialized_args = await serialize_list(built_args)
        call_args = lib_num | (no_wait << 16)
        self.script.queue_event("link_message", LinkMessage(IPCType.CALL_LIB, serialized_args, str(call_args)))
        await self.script.execute()

    async def assertLibraryReplyEquals(self, val: Any):
        self.assertEqual(1, len(self.sent_messages))
        expecting_list = isinstance(val, (tuple, list))
        expecting_none = val is None
        dest, ipc_type, ret_val, ret_type = self.sent_messages[0]
        ret_type = int(ret_type)
        self.assertEqual(IPCType.CALL_LIB_REPLY, ipc_type)
        if expecting_none:
            self.assertEqual(ret_type, LibFuncRet.NONE)
            self.assertEqual("", ret_val)
            return

        unboxed = await deserialize_list(ret_val)
        if expecting_list:
            self.assertEqual(ret_type, LibFuncRet.LIST)
            self.assertSequenceEqual(val, unboxed)
        else:
            self.assertEqual(ret_type, LibFuncRet.SIMPLE)
            self.assertEqual(val, unboxed[0])

    async def test_void_call_works(self):
        say_mock = unittest.mock.MagicMock()
        self.script.builtin_funcs['llSay'] = say_mock
        await self._call_library_function(LIBRARY_FUNCS['llSay'].num, 0, "foo")
        say_mock.assert_called_once()
        self.assertSequenceEqual([LinkMessage(IPCType.CALL_LIB_REPLY, "", Key("0"))], self.sent_messages)
        await self.assertLibraryReplyEquals(None)

    async def test_simple_ret_works(self):
        await self._call_library_function(LIBRARY_FUNCS['llFabs'].num, -1.0)
        await self.assertLibraryReplyEquals(1.0)

    async def test_list_arg_works(self):
        await self._call_library_function(LIBRARY_FUNCS['llList2Float'].num, [1, 2, 4.0], 1)
        await self.assertLibraryReplyEquals(2.0)

    async def test_list_ret_works(self):
        await self._call_library_function(LIBRARY_FUNCS['llList2List'].num, [1, 2, 4.0], 0, 1)
        await self.assertLibraryReplyEquals([1, 2])

    async def test_void_call_no_wait_works(self):
        say_mock = unittest.mock.MagicMock()
        self.script.builtin_funcs['llSay'] = say_mock
        await self._call_library_function(LIBRARY_FUNCS['llSay'].num, 0, "foo", no_wait=True)
        say_mock.assert_called_once()
        # No completion notification sent, we didn't want to wait!
        self.assertSequenceEqual([], self.sent_messages)


if __name__ == "__main__":
    unittest.main()
