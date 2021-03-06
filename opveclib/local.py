# Copyright 2016 Hewlett Packard Enterprise Development LP
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for
# the specific language governing permissions and limitations under the License.


import os
import errno
import tensorflow as tf

#: Version string for current version
version = '0.3.4'

# set directories for cuda and operator cache
cuda_directory = os.getenv('CUDA_HOME', '/usr/local/cuda')
_base_cache_directory = os.getenv('OPVECLIB_HOME', os.path.join(os.path.expanduser('~'), '.opveclib'))

#: Directory where cached operators are stored
cache_directory = os.path.join(_base_cache_directory, version)

# create the cache directory if it does not exist
try:
    os.makedirs(cache_directory)
except OSError as exception:
    if exception.errno != errno.EEXIST:
        raise


#: Flag which indicates whether or not CUDA operators are enabled
cuda_enabled = True

# test whether we have cuda installed and if the tensorflow cuda version is installed
if not os.path.exists(cuda_directory):
    cuda_enabled = False
    tf.logging.log(tf.logging.INFO, '*** CUDA directory not found - Running on CPU Only ***')
elif not tf.test.is_built_with_cuda():
    cuda_enabled = False
    tf.logging.log(tf.logging.INFO, '*** TensorFlow CUDA version not installed - Running on CPU Only ***')
