import os.path
import sys
import unittest
import uuid
from typing import *

from lummao import Key


# Pythonized directory needs to be in the python path, and it's not packaged.
upper_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if upper_path not in sys.path:
    sys.path.append(upper_path)


from pythonized import interpreter


async def deserialize_list(val: str) -> List[Any]:
    script = interpreter.Script()
    return await script.JSONTypeParse(val)


async def serialize_list(val: Sequence[Any]) -> str:
    script = interpreter.Script()
    return await script.JSONTypeDump(list(val))


class LinkMessage(Sequence):
    def __init__(self, num: int, string: str, key: Key):
        self.num = num
        self.string = string
        self.key = key
        self.tup = (-4, int(self.num), self.string, self.key)

    def __eq__(self, other):
        if isinstance(other, LinkMessage):
            other = other.tup
        return self.tup == other

    def __getitem__(self, index: int):
        return self.tup[index]

    def __len__(self) -> int:
        return len(self.tup)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.num!r}, {self.string!r}, {self.key!r})"


class MockNotecard:
    def __init__(self, name: str, text: str):
        self.name = name
        self.text = text

    def get_line(self, line_no: int):
        try:
            return self.text.split("\n")[line_no]
        except IndexError:
            # Bad line number returns EOF (three newlines)
            return "\n\n\n"


class MockNotecardHandler:
    def __init__(self, script, notecards: List[MockNotecard]):
        self.script = script
        self.notecards = notecards
        self._req_num = 0

    def get_key(self, name: str):
        if name == name:
            return Key(uuid.UUID(int=0xF00F))
        return Key(uuid.UUID(int=0))

    def get_line(self, name: str, line: int):
        assert (line >= 0)
        for nc in self.notecards:
            if nc.name == name:
                line_text = nc.get_line(line)
                break
        else:
            raise KeyError(f"Unknown notecard {name}")

        self._req_num += 1
        req_id = Key(uuid.UUID(int=self._req_num))
        self.script.queue_event("dataserver", (req_id, line_text))
        return req_id

    def patch_script(self):
        self.script.builtin_funcs['llGetInventoryKey'] = self.get_key
        self.script.builtin_funcs['llGetNotecardLine'] = self.get_line


class BaseMessagingTestCase(unittest.IsolatedAsyncioTestCase):
    script: Any
    sent_messages: List[Tuple[Any, ...]]

    async def asyncSetUp(self) -> None:
        self.sent_messages = []
        self.script.builtin_funcs['llMessageLinked'] = lambda *args: self.sent_messages.append(args)
