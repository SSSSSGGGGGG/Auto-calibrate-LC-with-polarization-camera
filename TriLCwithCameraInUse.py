# -*- coding: utf-8 -*-
"""
Created on Wed Feb 14 11:28:11 2024

@author: SG
"""

import initialKLCfor3
import closeKLCfor3
import numpy as np
from KLCCommandLib import *
from openpyxl import Workbook
import time
import asyncio
import nest_asyncio
nest_asyncio.apply()
try:
    # if on Windows, use the provided setup script to add the DLLs folder to the PATH
    from windows_setup import configure_path
    configure_path()
except ImportError:
    configure_path = None
    
from PIL import Image, ImageDraw, ImageFont

from thorlabs_tsi_sdk.tl_camera import TLCameraSDK
from thorlabs_tsi_sdk.tl_camera_enums import SENSOR_TYPE
from thorlabs_tsi_sdk.tl_polarization_processor import PolarizationProcessorSDK

start_time = time.time()
handle1,handle2,handle3=initialKLCfor3.initialKLC(1)
print("KLC´s handles:",handle1,handle2,handle3)

vol1=[1.3,2.15,1.1,1.1,1.1,1.55]
vol2=[1.4,1.4,1.15,1.7,1.4,1.4]
vol3=[3.65,3.65,3.65,3.65,3.65,3.65]
vol4=[3.95,3.95,3.95,3.95,3.95,3.95]
# config value will be vavriable for judging the type of configuration.
f=1000  # set the frequency to the enabled channel
mode=2 # 1 continuous; 2 cycle.
cyclenumber=1 #number of cycles 1~ 2147483648.s
delay=1000  #  the sample intervals[ms] 1~ 2147483648
precycle_rest=0  # the delay time before the cycle start[ms] 0~ 2147483648.
 
async def sendVoltage(v1,v2,v3):
    l1=len(v1)
    volarr1 =  (c_float * len(v1))(*v1)
    l2=len(v2)
    volarr2 =  (c_float * len(v2))(*v2)
    l3=len(v3)
    volarr3 =  (c_float * len(v3))(*v3)
    if(klcSetOutputLUT(handle1, volarr1, l1)<0):
        print("klc1SetOutputLUT failed")
    if(klcSetOutputLUT(handle2, volarr2, l2)<0):
        print("klc2SetOutputLUT failed") 
    if(klcSetOutputLUT(handle3, volarr3, l3)<0):
        print("klc3SetOutputLUT failed")
    if(klcSetOutputLUTParams(handle1, mode, cyclenumber, delay, precycle_rest)<0):
        print("klc1SetOutputLUTParams failed")                
    if(klcSetOutputLUTParams(handle2, mode, cyclenumber, delay, precycle_rest)<0):
        print("klc2SetOutputLUTParams failed")
    if(klcSetOutputLUTParams(handle3, mode, cyclenumber, delay, precycle_rest)<0):
        print("klc3SetOutputLUTParams failed")
    task=asyncio.create_task(camera(v3))
    print(f"The current voltage:LC1{v1},LC2{v2},LC3{v3}")  
        
    if(klcStartLUTOutput(handle1)<0):
        print("klc1StartLUTOutput failed")
    if(klcStartLUTOutput(handle2)<0):
        print("klc2StartLUTOutput failed")
    if(klcStartLUTOutput(handle3)<0):
        print("klc3StartLUTOutput failed") 
    # await asyncio.sleep(1)
    await task

def my_count(s, i=[0]):
    #print(s)
    i[0] += 1
    return i[0]

async def camera(v3):
    with TLCameraSDK() as camera_sdk, PolarizationProcessorSDK() as polarization_sdk:
        available_cameras = camera_sdk.discover_available_cameras()
        if len(available_cameras) < 1:
            raise ValueError("no cameras detected")
            # !!!!
        with camera_sdk.open_camera(available_cameras[0]) as camera:
            camera.frames_per_trigger_zero_for_unlimited = 1  # start camera in continuous mode
            camera.image_poll_timeout_ms = 2000  # 2 second timeout
            camera.arm(2)

            """
                In a real-world scenario, we want to save the image width and height before color processing so that we 
                do not have to query it from the camera each time it is needed, which would slow down the process. It is 
                safe to save these after arming since the image width and height cannot change while the camera is armed.
            """
            image_width = camera.image_width_pixels
            image_height = camera.image_height_pixels

            camera.issue_software_trigger()

            frame = camera.get_pending_frame_or_null()
            if frame is not None:
                print("frame received!")
            else:
                raise ValueError("No frame arrived within the timeout!")

            camera.disarm()

            if camera.camera_sensor_type is not SENSOR_TYPE.MONOCHROME_POLARIZED:
                raise ValueError("Polarization processing should only be done with polarized cameras")

            camera_polar_phase = camera.polar_phase
            camera_bit_depth = camera.bit_depth
            """
            We're scaling to 8-bits in this example so we can easily convert to PIL Image objects.
            """
            max_output_value = 255

            with polarization_sdk.create_polarization_processor() as polarization_processor:
                
                # Lastly, we'll construct a QuadView image that is useful for visualizing each polar rotation: 0, 45, 90, and 
                # -45 degrees. The sensor on the polarized camera has a filter in front of it that is composed of 2x2 pixel 
                # sections that look like the following pattern: 

                # -------------
                # | +90 | -45 |
                # -------------
                # | +45 | + 0 |
                # -------------

                # It is always 2x2, but the ordering of the rotations may differ depending on your camera model. The top left 
                # rotation (the 'origin' rotation) is always equal to the camera_polar_phase that was queried earlier. We'll 
                # use array splicing to extract each of the rotations and separate them visually. If you are familiar with 
                # manipulating color image arrays, this is similar to pulling out the R, G, and B components of an RGB image.
                # """
                unprocessed_image = frame.image_buffer.reshape(image_height, image_width)  # this is the raw image data
                unprocessed_image = unprocessed_image >> camera_bit_depth - 8  # scale to 8 bits for easier displaying
                output_quadview = np.zeros(shape=(image_height, image_width))  # initialize array for QuadView data
                # Top Left Quadrant =
                output_quadview[0:int(image_height / 2), 0:int(image_width / 2)] = \
                    unprocessed_image[0::2, 0::2]  # (0,0): top left rotation == camera_polar_phase
                # Top Right Quadrant =
                output_quadview[0:int(image_height / 2), int(image_width / 2):image_width] = \
                    unprocessed_image[0::2, 1::2]  # (0,1): top right rotation
                # Bottom Left Quadrant =
                output_quadview[int(image_height / 2):image_height, 0:int(image_width / 2)] = \
                    unprocessed_image[1::2, 0::2]  # (1,0): bottom left rotation
                # Bottom Right Quadrant =
                output_quadview[int(image_height / 2):image_height, int(image_width / 2):image_width] = \
                    unprocessed_image[1::2, 1::2]  # (1,1): bottom right rotation
                # Display QuadView
                quadview_image = Image.fromarray(output_quadview)
                
                # quadview_image.show()
                img = quadview_image.convert('RGB')
                draw=ImageDraw.Draw(img)
                text1="+0"
                text2="+90"
                text3="+45"
                text4="-45"
                font=ImageFont.truetype("arial.ttf",50)
                draw.text((0,0), text2, (255,255,255),font=font)
                draw.text((1224,1024), text1, (255,255,255),font=font)
                draw.text((0,1024), text3, (255,255,255),font=font)
                draw.text((1224,0), text4, (255,255,255),font=font)
                k=my_count(1) 
                if k<7:
                    img.save(f"PSA {v3}=2.5pi_{k}.tif") 
                else:
                    img.save(f"PSA {v3}=2pi_{k}.tif")
      

def main():      
    length1=len(vol1)
    count=1
    while(count<length1+1):  
        vols1=[vol1[count-1]] 
        vols2=[vol2[count-1]]
        volPi=[vol3[count-1]]
        print(f"The input voltages: vols1 ={vols1},vols2 ={vols2},vols3 ={volPi}")
        asyncio.run(sendVoltage(vols1, vols2,volPi))
        count+=1
    count2=1
    while(count2<length1+1):  
        vols1=[vol1[count2-1]] 
        vols2=[vol2[count2-1]]        
        volHlafPi=[vol4[count2-1]]
        print(f"The input voltages: vols1 ={vols1},vols2 ={vols2},vols3 ={volHlafPi}")
        asyncio.run(sendVoltage(vols1, vols2,volHlafPi))
        count2+=1

if __name__=="__main__":
    main()
    
print("The measurement is done.")
closeKLCfor3.closeKLC(handle1,handle2,handle3)
end_time = time.time()
execution_time = end_time - start_time
print("Execution time:", execution_time, "seconds")