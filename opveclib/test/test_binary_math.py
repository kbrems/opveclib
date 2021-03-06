# Copyright 2016 Hewlett Packard Enterprise Development LP
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for
# the specific language governing permissions and limitations under the License.

from __future__ import print_function
import unittest
import numpy as np
from sys import _getframe
from ..operator import Operator
from ..expression import output_like, position_in, minimum, maximum, power, arctan2, logical_and, logical_or
from ..local import cuda_enabled


def gen(input0, input1, ops_func, np_func):
    class BinaryMath(Operator):
        def op(self, input0, input1):

            output = output_like(input0)
            pos = position_in(input0.shape)

            output[pos] = ops_func(input0[pos], input1[pos])

            return output

    op = BinaryMath(input0, input1, clear_cache=True)
    op_c = op.evaluate_c()
    assert np.allclose(op_c, np_func(input0, input1))

    if cuda_enabled:
        op_cuda = op.evaluate_cuda()
        assert np.allclose(op_cuda, np_func(input0, input1))


class TestBinary(unittest.TestCase):
    def test_binary(self):
        print('*** Running Test: ' + self.__class__.__name__ + ' function: ' + _getframe().f_code.co_name)
        self.binary_math(np.float32)
        self.binary_math(np.float64)

        self.binary_math(np.int8)
        self.binary_math(np.int16)
        self.binary_math(np.int32)
        self.binary_math(np.int64)

        self.binary_math(np.uint8)
        self.binary_math(np.uint16)
        self.binary_math(np.uint32)
        self.binary_math(np.uint64)

    def binary_math(self, dtype):
        length = 10
        rng = np.random.RandomState(1)

        def cast(arg):
            uints = [np.uint8, np.uint16, np.uint32, np.uint64]
            if dtype in uints:
                return np.abs(arg).astype(dtype)
            else:
                return arg.astype(dtype)

        x = cast(rng.uniform(-10, 10, length))
        y = cast(rng.uniform(-10, 10, length))
        y_nonzero = y + np.equal(y, 0)

        x_binary = cast(rng.uniform(0, 1, length) > 0.5)
        y_binary = cast(rng.uniform(0, 1, length) > 0.5)

        gen(x, y, lambda a, b: a + b, lambda a, b: a + b)
        gen(x, y, lambda a, b: a - b, lambda a, b: a - b)
        gen(x, y, lambda a, b: a * b, lambda a, b: a * b)

        # use c style integer division (round towards 0) instead of python style (round towards negative infinity)
        def truncated_division(a, b):
            ints = [np.int8, np.int16, np.int32, np.int64]
            if b.dtype in ints:
                return np.trunc(np.true_divide(a, b)).astype(b.dtype)
            else:
                return np.true_divide(a, b).astype(b.dtype)
        gen(x, y_nonzero, lambda a, b: a / b, truncated_division)

        def truncated_mod(a, b):
            return a-b*np.trunc(np.true_divide(a, b)).astype(b.dtype)

        gen(x, y_nonzero, lambda a, b: a % b, truncated_mod)
        gen(x_binary, y_binary, lambda a, b: a == b, lambda a, b: np.equal(a, b))
        gen(x_binary, y_binary, lambda a, b: a != b, lambda a, b: np.not_equal(a, b))
        gen(x_binary, y_binary, lambda a, b: logical_or(a, b), lambda a, b: np.logical_or(a, b))
        gen(x_binary, y_binary, lambda a, b: logical_and(a, b), lambda a, b: np.logical_and(a, b))
        gen(x, y, lambda a, b: a < b, lambda a, b: np.less(a, b))
        gen(x, y, lambda a, b: a <= b, lambda a, b: np.less_equal(a, b))
        gen(x, y, lambda a, b: a > b, lambda a, b: np.greater(a, b))
        gen(x, y, lambda a, b: a >= b, lambda a, b: np.greater_equal(a, b))
        gen(x, y, lambda a, b: minimum(a, b), lambda a, b: np.minimum(a, b))
        gen(x, y, lambda a, b: maximum(a, b), lambda a, b: np.maximum(a, b))

        fp = [np.float32, np.float64]
        if dtype in fp:
            gen(np.abs(x), y, lambda a, b: power(a, b), lambda a, b: np.power(a, b))
            gen(x, y, lambda a, b: arctan2(a, b), lambda a, b: np.arctan2(a, b))


if __name__ == '__main__':
    unittest.main()
