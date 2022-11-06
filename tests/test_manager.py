#!/usr/bin/env python
import unittest
import unittest.mock
import uuid
from typing import *

from lummao import Vector, Quaternion, Key

from pythonized import manager
from constants import *

from . import BaseMessagingTestCase, serialize_list, LinkMessage, MockNotecardHandler

TOUCH_START_NUM = EVENTS['touch_start'].num
STATE_EXIT_NUM = EVENTS['state_exit'].num
TIMER_NUM = EVENTS['timer'].num

DEFAULT_NOTECARD = f"""
[{TOUCH_START_NUM}, 1, {TIMER_NUM}, 2, {STATE_EXIT_NUM}, 3]
[0,0, 5,1, 10,2]
line0
line1
line2
""".lstrip()


class ManagerTests(BaseMessagingTestCase):
    script: manager.Script

    async def asyncSetUp(self):
        self.script = manager.Script()
        await super().asyncSetUp()
        self.notecard = MockNotecardHandler(self.script, "script", DEFAULT_NOTECARD)
        self.notecard.patch_script()

    def _request_ip(self, ip: int):
        self.script.queue_event("link_message", LinkMessage(IPCType.REQUEST_CODE, "", Key(str(ip))))

    def _send_handler_finished(self):
        self.script.queue_event("link_message", LinkMessage(IPCType.HANDLER_FINISHED, "", Key("")))

    async def _execute_until_bootstrapped(self):
        await self.script.execute()
        self._send_handler_finished()
        await self.script.execute()

    async def assertRequestReturns(self, request_ip: int, returns: Tuple[int, str]):
        self.sent_messages.clear()
        self._request_ip(request_ip)
        await self.script.execute()
        expected_messages = [
            LinkMessage(IPCType.REQUEST_CODE_REPLY, returns[1], Key(str(returns[0])))
        ]
        self.assertSequenceEqual(expected_messages, self.sent_messages)
        self.sent_messages.clear()

    async def test_sends_startup_messages(self):
        await self.script.execute()
        expected_messages = [
            LinkMessage(IPCType.MANAGER_RESTARTED, "", Key("")),
            LinkMessage(IPCType.SCRIPT_LOADED, "", Key("")),
            LinkMessage(IPCType.INVOKE_HANDLER, "", Key("0")),
        ]
        self.assertSequenceEqual(expected_messages, self.sent_messages)
        self.sent_messages.clear()

        self.script.queue_event("link_message", LinkMessage(IPCType.HANDLER_FINISHED, "", Key("")))
        # No state_entry invocation because we don't have one registered
        await self.script.execute()
        self.assertSequenceEqual([], self.sent_messages)

    async def test_load_works(self):
        await self.script.execute()

        self.assertSequenceEqual(
            [*CodeIndex(0, 0), *CodeIndex(5, 1), *CodeIndex(10, 2)],
            self.script.gCodeLines
        )
        self.assertSequenceEqual(
            [
                *HandlerIndex(TOUCH_START_NUM, 1),
                *HandlerIndex(TIMER_NUM, 2),
                *HandlerIndex(STATE_EXIT_NUM, 3),
            ],
            self.script.gEventHandlers
        )
        self.assertEqual(2, self.script.gHeaderLines)
        self.assertEqual(0, self.script.gLoadState)
        self.assertEqual(Key(uuid.UUID(int=0)), self.script.gNotecardRequestID)

    async def test_can_request_code(self):
        # Allow the initial notecard loading to finish before we start making requests
        await self.script.execute()

        await self.assertRequestReturns(0, (0, "line0"))
        await self.assertRequestReturns(5, (5, "line1"))
        await self.assertRequestReturns(11, (10, "line2"))

    async def test_invalid_code_request(self):
        # Allow the initial notecard loading to finish before we start making requests
        await self.script.execute()

        ownersay_mock = unittest.mock.Mock()
        self.script.builtin_funcs['llOwnerSay'] = ownersay_mock
        self.sent_messages.clear()
        self._request_ip(-1)
        await self.script.execute()
        # There should be no response
        self.assertSequenceEqual([], self.sent_messages)
        ownersay_mock.assert_called_once()

    async def test_cache_hit(self):
        # Allow the initial notecard loading to finish before we start making requests
        await self.script.execute()

        await self.assertRequestReturns(0, (0, "line0"))
        await self.assertRequestReturns(6, (5, "line1"))
        await self.assertRequestReturns(0, (0, "line0"))
        get_notecard_line_mock = unittest.mock.Mock()
        self.script.builtin_funcs['llGetNotecardLine'] = get_notecard_line_mock
        await self.assertRequestReturns(4, (0, "line0"))
        # The request should have been a cache hit, resulting in not having to
        # read the notecard
        get_notecard_line_mock.assert_not_called()
        expected_cached = [*CachedCode(4, 0, "line0"), *CachedCode(2, 1, "line1")]
        expected_len = NUM_CACHED_CODES * len(CachedCode.indices)
        while len(expected_cached) != expected_len:
            expected_cached.extend(CachedCode(-0x7FffFFff, -0x7FffFFff, -0x7FffFFff))
        self.assertSequenceEqual(expected_cached, self.script.gCachedCode)

        await self.assertRequestReturns(4, (0, "line0"))
        # Cache hit should have updated the LRU tag
        expected_cached[0] = 5
        self.assertSequenceEqual(expected_cached, self.script.gCachedCode)

        # This should still be a cache hit too
        await self.assertRequestReturns(6, (5, "line1"))

    async def test_invoke_handler(self):
        await self._execute_until_bootstrapped()
        self.sent_messages.clear()
        # Touch event should invoke the touch event handler
        await self.script.edefaulttouch_start(0)
        expected_messages = [
            LinkMessage(IPCType.INVOKE_HANDLER, await serialize_list([0]), Key("1")),
        ]
        self.assertSequenceEqual(expected_messages, self.sent_messages)
        self.assertSequenceEqual([], self.script.gQueuedEvents)
        self.assertTrue(self.script.gInvokingHandler)

        # Handler finished message should clear the invoking flag
        self.sent_messages.clear()
        self.script.queue_event("link_message", LinkMessage(IPCType.HANDLER_FINISHED, "", Key("")))
        await self.script.execute()
        self.assertFalse(self.script.gInvokingHandler)
        self.assertSequenceEqual([], self.sent_messages)

        # Nothing should happen in the touch event if we unregister the event handlers
        self.script.gEventHandlers.clear()
        await self.script.edefaulttouch_start(0)
        self.assertSequenceEqual([], self.sent_messages)
        self.assertSequenceEqual([], self.script.gQueuedEvents)
        self.assertFalse(self.script.gInvokingHandler)

    async def test_queue_event(self):
        await self._execute_until_bootstrapped()
        self.sent_messages.clear()
        # Touch event should invoke the touch event handler
        await self.script.edefaulttouch_start(0)
        await self.script.edefaulttouch_start(1)
        # Only the first should have been sent immediately
        expected_messages = [
            LinkMessage(IPCType.INVOKE_HANDLER, await serialize_list([0]), Key("1")),
        ]
        self.assertSequenceEqual(expected_messages, self.sent_messages)
        # The other should be queued
        expected_queued = [
            *QueuedEvent(
                TOUCH_START_NUM,
                1,
                await serialize_list([1]),
                await serialize_list([Key(""), Key("")]),
            ),
        ]
        self.assertSequenceEqual(expected_queued, self.script.gQueuedEvents)
        self.assertTrue(self.script.gInvokingHandler)

        # Handler finished message should clear the invoking flag and send the queued message
        self.sent_messages.clear()
        self.script.queue_event("link_message", LinkMessage(IPCType.HANDLER_FINISHED, "", Key("")))

        await self.script.execute()
        self.assertTrue(self.script.gInvokingHandler)
        expected_messages = [
            LinkMessage(IPCType.INVOKE_HANDLER, await serialize_list([1]), Key("1")),
        ]
        self.assertSequenceEqual(expected_messages, self.sent_messages)
        # The queue should have been cleared out
        self.assertSequenceEqual([], self.script.gQueuedEvents)

    async def test_no_timer_requeue(self):
        await self._execute_until_bootstrapped()
        self.sent_messages.clear()
        await self.script.edefaulttimer()
        await self.script.edefaulttouch_start(1)
        for _ in range(2):
            await self.script.edefaulttimer()
        # Only the first should have been sent immediately
        expected_messages = [
            LinkMessage(IPCType.INVOKE_HANDLER, await serialize_list([]), Key("2")),
        ]
        self.assertSequenceEqual(expected_messages, self.sent_messages)
        # And only the second timer event should have been queued
        expected_queued = [
            # But the touch event should still be at the head of the line
            *QueuedEvent(
                TOUCH_START_NUM,
                1,
                await serialize_list([1]),
                await serialize_list([Key(""), Key("")]),
            ),
            *QueuedEvent(TIMER_NUM, 2, await serialize_list([]), await serialize_list([])),
        ]
        self.assertSequenceEqual(expected_queued, self.script.gQueuedEvents)
        self.assertTrue(self.script.gInvokingHandler)

    async def test_detected_call(self):
        await self.script.execute()
        self.sent_messages.clear()
        detected_key_num = Key(LIBRARY_FUNCS["llDetectedKey"].num)
        # These are compressed "non-key" keys for readability.
        self.script.gDetectedStack = [
            *DetectEntry(Key("-foo"), Key("-bar")),
        ]
        self.script.queue_event(
            "link_message",
            LinkMessage(IPCType.CALL_LIB, await serialize_list([0]), detected_key_num)
        )
        await self.script.execute()
        # No detected stack, should have returned the default value `llDetectedKey(invalid)`
        expected_messages = [
            LinkMessage(IPCType.CALL_LIB_REPLY, await serialize_list([Key("foo")]), Key("1")),
        ]
        self.assertSequenceEqual(expected_messages, self.sent_messages)

    async def test_detected_call_default(self):
        await self.script.execute()
        self.sent_messages.clear()
        detected_key_num = Key(LIBRARY_FUNCS["llDetectedKey"].num)
        self.script.queue_event(
            "link_message",
            LinkMessage(IPCType.CALL_LIB, await serialize_list([0]), detected_key_num)
        )
        await self.script.execute()
        # No detected stack, should have returned the default value `llDetectedKey(invalid)`
        expected_messages = [
            LinkMessage(IPCType.CALL_LIB_REPLY, await serialize_list([Key(uuid.UUID(int=0))]), Key("1")),
        ]
        self.assertSequenceEqual(expected_messages, self.sent_messages)

    async def test_change_state(self):
        await self.script.execute()
        self.sent_messages.clear()
        self.script.gInvokingHandler = 1
        self.script.queue_event(
            "link_message",
            LinkMessage(IPCType.CHANGE_STATE, "", Key("1"))
        )
        await self.script.execute()
        self.assertEqual(1, self.script.gScriptState)
        # Should have invoked the state_exit for the state
        expected_messages = [
            LinkMessage(IPCType.INVOKE_HANDLER, await serialize_list([]), Key("3")),
        ]
        self.assertSequenceEqual(expected_messages, self.sent_messages)

    async def test_compress_key(self):
        expected = Key(uuid.UUID(int=1))
        # Base 4096-encoded UUID
        self.assertEqual(Key(("\ue030" * 10) + "\ue070"), await self.script.compress_key(expected))
        self.assertEqual(
            expected,
            await self.script.uncompress_key(await self.script.compress_key(expected))
        )

        # Null UUID -> Blank string
        expected = Key(uuid.UUID(int=0))
        self.assertEqual(Key(""), await self.script.compress_key(expected))
        self.assertEqual(
            expected,
            await self.script.uncompress_key(await self.script.compress_key(expected))
        )

        expected = Key("foobar")
        self.assertEqual(Key("-foobar"), await self.script.compress_key(expected))
        self.assertEqual(
            expected,
            await self.script.uncompress_key(await self.script.compress_key(expected))
        )

        expected = Key("")
        self.assertEqual(Key("-"), await self.script.compress_key(expected))
        self.assertEqual(
            expected,
            await self.script.uncompress_key(await self.script.compress_key(expected))
        )


if __name__ == "__main__":
    unittest.main()
