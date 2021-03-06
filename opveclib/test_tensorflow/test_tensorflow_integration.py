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
from sys import _getframe

import numpy as np

import tensorflow as tf
from opveclib.expression import position_in, output_like
from opveclib.operator import Operator
from opveclib.local import cuda_enabled


class TestIntegration(unittest.TestCase):
    def test_single_output(self):
        print('*** Running Test: ' + self.__class__.__name__ + ' function: ' + _getframe().f_code.co_name)

        class AddOp(Operator):
            def op(self, x, y):
                pos = position_in(x.shape)
                out = output_like(x)
                out[pos] = x[pos] + y[pos]
                return out

        in0 = np.random.random(5).astype(np.float32)
        in1 = np.random.random(5).astype(np.float32)
        reference = 4*(in0 + in1)*(in0 + in1)

        with tf.Session() as sess:
            with tf.device('/cpu:0'):
                a = in0*2
                b = in1*2
                c = AddOp(a, b, clear_cache=True).as_tensorflow()
                squared = tf.square(c)
            if cuda_enabled:
                with tf.device('/gpu:0'):
                    a_gpu = in0*2
                    b_gpu = in1*2
                    c_gpu = AddOp(a_gpu, b_gpu).as_tensorflow()
                    squared_gpu = tf.square(c_gpu)
                result, result_gpu = sess.run([squared, squared_gpu])
                assert np.allclose(reference, result_gpu)
            else:
                result = sess.run([squared])

        assert np.allclose(reference, result)


    def test_multiple_outputs(self):
        print('*** Running Test: ' + self.__class__.__name__ + ' function: ' + _getframe().f_code.co_name)

        class MultiOp(Operator):
            # first output is the sum of first two inputs
            # second output is the sum of the first two multiplied by the third
            # third output is sum of all three inputs
            def op(self, input0, input1, input2):
                pos = position_in(input0.shape)
                output0 = output_like(input0)
                output1 = output_like(input0)
                output2 = output_like(input0)

                a = input0[pos]
                b = input1[pos]
                c = input2[pos]
                d = a + b
                output0[pos] = d
                output1[pos] = d*c
                output2[pos] = d+c

                return output0, output1, output2

        rng = np.random.RandomState()
        in0 = rng.uniform(-1, 1, 5).astype(np.float32)
        in1 = rng.uniform(-1, 1, 5).astype(np.float32)
        in2 = rng.uniform(-1, 1, 5).astype(np.float32)

        np1 = in0*in0 + in1*in1
        np2 = np1*in2
        np3 = np1 + in2

        with tf.Session() as sess:
            sq0 = tf.square(in0)
            sq1 = tf.square(in1)

            with tf.device('/cpu:0'):
                op = MultiOp(sq0, sq1, in2, clear_cache=True)
                out0, out1, out2 = op.as_tensorflow()

            if cuda_enabled:
                with tf.device('/gpu:0'):
                    op_gpu = MultiOp(sq0, sq1, in2, clear_cache=True)
                    out0_gpu, out1_gpu, out2_gpu = op_gpu.as_tensorflow()

                eval1, eval2, eval3, eval1_gpu, eval2_gpu, eval3_gpu = \
                    sess.run([out0, out1, out2, out0_gpu, out1_gpu, out2_gpu])
                assert np.allclose(eval1_gpu, np1)
                assert np.allclose(eval2_gpu, np2)
                assert np.allclose(eval3_gpu, np3)
            else:
                eval1, eval2, eval3 = sess.run([out0, out1, out2])

        assert np.allclose(eval1, np1)
        assert np.allclose(eval2, np2)
        assert np.allclose(eval3, np3)


if __name__ == '__main__':
    unittest.main()
