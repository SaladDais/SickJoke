#!/usr/bin/env python
import math
import unittest

from . import serialize_list, deserialize_list

from lummao.vendor.lslopt.lslcommon import Vector, Quaternion, Key


class UtilsTests(unittest.IsolatedAsyncioTestCase):
    async def test_serialize(self):
        orig = [
            1, 1.0, " ", Key(""), Vector((1.0, math.inf, 1.0)), Quaternion((1.0, -math.inf, 1.0, 1.0))
        ]
        serialized = await serialize_list(orig)
        expected = '["111","21.0000002","3 3","44","5<1.000000, Infinity, 1.000000>5",' \
                   '"6<1.000000, -Infinity, 1.000000, 1.000000>6"]'
        self.assertEqual(expected, serialized)
        self.assertSequenceEqual(orig, await deserialize_list(serialized))


if __name__ == "__main__":
    unittest.main()
