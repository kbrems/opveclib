# Copyright 2016 Hewlett Packard Enterprise Development LP
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for
# the specific language governing permissions and limitations under the License.

import os.path
from urllib2 import Request, urlopen, URLError
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from diffusion import TensorToFloat64, diffusion2DGPU

def downloadImage(fileURL, fileName, fileTmp):
    # Cache the downloaded file in the /tmp directory and only download it again if not present.
    rValue = 0
    if not os.path.isfile(fileTmp):
        print "Downloading data file %s." % (fileURL + fileName)
        req = Request(fileURL + fileName)
        try:
            response = urlopen(req)
        except URLError as e:
            if hasattr(e, 'reason'):
                print 'Could not reach ', fileURL, ' because of ', e.reason
            elif hasattr(e, 'code'):
                print 'Server ', fileURL, ' returned error code ', e.code
        else:
            print "Downloaded file %s." % (fileURL + fileName)
            with open(fileTmp, 'w') as fHandle:
                fHandle.write(response.read())
                rValue = 1
    else:
        rValue = 1

    return rValue



if __name__ == '__main__':
    """Demo program for the anisotropic image diffusion.

    This program loads an MRI scan used for image diffusion.
    Image diffusion helps to segment parts within the image.

    """
    fileURL     = "https://upload.wikimedia.org/wikipedia/commons/6/68/"
    fileName    = "Head_MRI%2C_enlarged_inferior_sagittal_sinus.png"
    fileTmp     = "/tmp/MRI.png"

    if downloadImage(fileURL, fileName, fileTmp):
        # Load the image and convert it into float64.
        imageIn     = TensorToFloat64(mpimg.imread(fileTmp)).evaluate_c()

        # Apply the image diffusion with the step width dt = 5, lambda parameter 3.5/255, sigma parameter = 3 pixel,
        # and 3 iterations.
        imageOut    = diffusion2DGPU(imageIn, dt=5, l=3.5/255, s=3, nIter=3)

        # Display the original image and diffusion result.
        plt.figure(1)
        plt.subplot(121)
        plt.imshow(imageIn)
        plt.title('Input')
        plt.set_cmap('gray')
        plt.subplot(122)
        plt.imshow(imageOut)
        plt.title('Diffused')
        plt.set_cmap('gray')
        plt.show()