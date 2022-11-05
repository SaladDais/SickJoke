"""
Run the library, manager and interpreter scripts together.

These tests are somewhat slow due to the state fixups lslopt
needs to constantly do to ensure that results of operations match
what LSL would do.
"""

import asyncio
import pathlib
import unittest
from typing import Sequence, Callable, Union
from unittest.mock import Mock

from lummao import BaseLSLScript, convert_script_to_ir

from assembler import Assembler
from constants import *
from ir2asm import IRConverter
from pythonized import interpreter, library, manager

from . import MockNotecardHandler


BASE_PATH = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))
RESOURCES_PATH = BASE_PATH / "test_resources"


class LinkMessagePropagator:
    """Passes outbound link messages to all other scripts in the set"""
    def __init__(self, scripts: Sequence[BaseLSLScript]):
        self.scripts = scripts

    def patch_scripts(self):
        for script in self.scripts:
            script.builtin_funcs['llMessageLinked'] = self._make_message_sender(script)

    def _make_message_sender(self, script: BaseLSLScript) -> Callable:
        """Make a version of llMessageLinked that will queue link_messages on other scripts"""
        def _send_message(link_num, num, string, key):
            for other_script in self.scripts:
                if other_script is script:
                    # Don't send messages to ourselves
                    continue
                other_script.queue_event("link_message", (link_num, num, string, key))
        return _send_message


class IntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.interp_script = interpreter.Script()
        self.manager_script = manager.Script()
        self.library_script = library.Script()
        self.scripts = [self.interp_script, self.manager_script, self.library_script]

        for script in self.scripts:
            self._patch_builtins(script)

        self.message_propagator = LinkMessagePropagator(self.scripts)
        self.message_propagator.patch_scripts()
        self.mock_notecard = MockNotecardHandler(self.manager_script, "script", "")
        self.mock_notecard.patch_script()

    def _patch_builtins(self, script: BaseLSLScript):
        base_builtins = script.builtin_funcs
        base_builtins['llOwnerSay'] = print
        base_builtins['llSay'] = lambda _chan, msg: print(msg)
        # Our state is already clean, we don't need to restart.
        base_builtins['llResetScript'] = lambda: None
        base_builtins['llSetText'] = lambda *args: None
        base_builtins['llResetTime'] = lambda: None
        base_builtins['llGetTime'] = lambda: 0.0

    def _script_to_asm(self, contents: Union[str, bytes]):
        converter = IRConverter(convert_script_to_ir(contents))
        assembler = Assembler()
        assembler.assemble(converter.convert())
        return assembler

    async def execute_scripts(self) -> bool:
        """
        Run all scripts in a sequence until all their event queues have drained

        This ensures that all communication between the scripts themselves has fully
        completed, and that nothing further could happen without another event coming
        in from outside the system.
        """
        handled = False
        while any(await asyncio.gather(*[s.execute() for s in self.scripts])):
            handled = True
        return handled

    async def test_simple(self):
        assembler = self._script_to_asm("""
default {
    state_entry() {
        llStopMoveToTarget();
    }
}
""")
        self.mock_notecard.text = assembler.pack()
        target_mock = Mock()
        self.manager_script.builtin_funcs['llStopMoveToTarget'] = target_mock
        await self.execute_scripts()
        target_mock.assert_called_once()

    async def test_lsl_conformance(self):
        with open(RESOURCES_PATH / "lsl_conformance.lsl", "rb") as f:
            assembler = self._script_to_asm(f.read())
        self.mock_notecard.text = assembler.pack()
        await self.execute_scripts()
        # Check test failed / passed numbers
        self.assertEqual(188, self.interp_script.gGlobals[0])
        self.assertEqual(0, self.interp_script.gGlobals[1])

    async def test_lsl_conformance2(self):
        with open(RESOURCES_PATH / "lsl_conformance2.lsl", "rb") as f:
            assembler = self._script_to_asm(f.read())
        self.mock_notecard.text = assembler.pack()
        await self.execute_scripts()
        # Check test failed / passed numbers
        self.assertEqual(69, self.interp_script.gGlobals[0])
        self.assertEqual(0, self.interp_script.gGlobals[1])