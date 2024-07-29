# -*- coding: utf-8 -*-
"""
Created on Wed Feb 14 11:28:11 2024

@author: Laboratorio
"""


import initialKLCfor1
import closeKLCfor1
import numpy as np
from KLCCommandLib import *
from openpyxl import Workbook
import time
import asyncio
import nest_asyncio
nest_asyncio.apply()


# initial KLC 
# here we also use a=1 to call KLC initial function
# If we need to restart KLC, we should restart the kernal (in the python console)
# To check the handle value of KLC, which is necessary for the following KLC functions.
handle=initialKLCfor1.initialKLC(1)
print("KLC´s handle:",handle)
# seriesName=input("input a name for the new series of captures:")
# =============================================================================
# 
# =============================================================================
# vols2=[0,1,2,3,4,5]
# x=np.arange(0,0.8,0.1)
# y=np.arange(0.8,2.1,0.01)
# z=np.arange(2.1,5.1,0.1)
vols2=np.arange(0,2,0.5)
# config value will be vavriable for judging the type of configuration.
f=1000  # !!!!! set the frequency to the enabled channel
mode=2 # 1 continuous; 2 cycle.
cyclenumber=1 #number of cycles 1~ 2147483648.s
delay=1000  # !!! the sample intervals[ms] 1~ 2147483648
precycle_rest=0 # the delay time before the cycle start[ms] 0~ 2147483648.
hdl=handle

async def sendVoltage(vols):
    l=len(vols)
    volarr =  (c_float * len(vols))(*vols)
    print("what is happenning")
    if(klcSetOutputLUT(hdl, volarr, l)<0):
        print("klcSetOutputLUT failed")
    klcSetFrequency1(hdl, f)   
    if(klcSetOutputLUTParams(hdl, mode, cyclenumber, delay, precycle_rest)<0):
        print("klcSetOutputLUTParams failed")
    
    print("----------------Current output voltage is:",vols)
    
    task=asyncio.create_task(camera())

    if(klcStartLUTOutput(hdl)<0):
        print("klcStartLUTOutput failed")
    
    asyncio.sleep(1)
    await task
async def camera():
    with TLCameraSDK() as camera_sdk, PolarizationProcessorSDK() as polarization_sdk:
        available_cameras = camera_sdk.discover_available_cameras()
        if len(available_cameras) < 1:
            raise ValueError("no cameras detected")
            # !!!!
        with camera_sdk.open_camera(available_cameras[0]) as camera:
            camera.frames_per_trigger_zero_for_unlimited = 1  # 0 means start camera in continuous mode
            camera.image_poll_timeout_ms = 1000  # block imgae by this time that is used for retrieving image to frame, unit is ms 2 second timeout
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
            print(f"camera_polar_phase at top left:{camera_polar_phase}, and the bit depth:{camera_bit_depth}")
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
                # | +45 |+ 0  |
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
                
                # draw.text(((0,0)), text2, (0,0,0), font=font)
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
                img.save("pAt-45.tif")
      
   
def main():  
         
    length=len(vols2) #!!!!
    count=1
    while(count<length+1):  
        vols1=[vols2[count-1]]   
         
        asyncio.run(sendVoltage(vols1))
        # with asyncio.Runner() as runner:
        #     runner.run(sendVoltage(vols1))
        count+=1

if __name__=="__main__":
    main()

# =============================================================================
#                    close all the devices
# =============================================================================
# input y will close all device, any other input will keep pd work, but KLC will be closed anyway
print("The measurement is done.")
closeKLCfor1.closeKLC(handle)