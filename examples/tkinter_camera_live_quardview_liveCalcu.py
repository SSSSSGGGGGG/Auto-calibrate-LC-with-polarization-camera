"""
Camera Live View - TkInter

This example shows how one could create a live image viewer using TkInter.
It also uses the third party library 'pillow', which is a fork of PIL.

This example detects if a camera is a color camera and will process the
images using the tl_mono_to_color_processor module.

This example uses threading to enqueue images coming off the camera in one thread, and
dequeue them in the UI thread for quick displaying.

"""
import numpy as np
try:
    # if on Windows, use the provided setup script to add the DLLs folder to the PATH
    from windows_setup_o import configure_path
    configure_path()
except ImportError:
    configure_path = None

from thorlabs_tsi_sdk.tl_camera import TLCameraSDK, TLCamera, Frame
from thorlabs_tsi_sdk.tl_camera_enums import SENSOR_TYPE
from thorlabs_tsi_sdk.tl_mono_to_color_processor import MonoToColorProcessorSDK
from thorlabs_tsi_sdk.tl_polarization_processor import PolarizationProcessorSDK
try:
    #  For python 2.7 tkinter is named Tkinter
    import Tkinter as tk
except ImportError:
    import tkinter as tk
from PIL import Image, ImageDraw, ImageFont, ImageTk 
import matplotlib.pyplot as plt
import typing
import threading
from tkinter import font
try:
    #  For Python 2.7 queue is named Queue
    import Queue as queue
except ImportError:
    import queue

""" LiveViewCanvas

This is a Tkinter Canvas object that can be reused in custom programs. The Canvas expects a parent Tkinter object and 
an image queue. The image queue is a queue.Queue that it will pull images from, and is expected to hold PIL Image 
objects that will be displayed to the canvas. It automatically adjusts its size based on the incoming image dimensions.

"""


class LiveViewCanvas(tk.Canvas):
    def __init__(self, parent, image_queue, canvas_width, canvas_height):
        self.image_queue = image_queue
        self._canvas_width = canvas_width
        self._canvas_height = canvas_height
        self._image_width = 0
        self._image_height = 0
        
        # Store the image reference
        self._image = None
        
        tk.Canvas.__init__(self, parent, width=self._canvas_width, height=self._canvas_height)
        self.pack(side="top", fill="both", expand=True)
        
        self._get_image()

    def _get_image(self):
        try:
            # Get the next image from the queue
            image = self.image_queue.get_nowait()
            
            # Resize the image to fit the canvas with LANCZOS resampling
            resized_image = image.resize((self._canvas_width, self._canvas_height), Image.Resampling.LANCZOS)
            
            # Convert the resized image to be displayed
            self._image = ImageTk.PhotoImage(master=self, image=resized_image)
            
            if (self._image.width() != self._image_width) or (self._image.height() != self._image_height):
                self._image_width = self._image.width()
                self._image_height = self._image.height()
                self.config(width=self._image_width, height=self._image_height)
                
            # Display the resized image on the canvas
            self.create_image(0, 0, image=self._image, anchor='nw')
        except queue.Empty:
            pass
        
        self.after(10, self._get_image)




# class ColorBarCanvas(tk.Canvas):
#     def __init__(self, parent, width=50, height=300):
#         tk.Canvas.__init__(self, parent, width=width, height=height)
#         self.pack(side="left", fill="both", expand=False)
#         self.create_color_bar(width, height)

#     def create_color_bar(self, width, height):
#         # Create a gradient (from blue to red)
#         color_gradient = np.linspace(0, 1, height).reshape(height, 1) * 255
#         color_image = np.zeros((height, width, 3), dtype=np.uint8)
#         color_image[:, :, 0] = color_gradient  # Red channel
#         color_image[:, :, 2] = 255 - color_gradient  # Blue channel
        
#         img = Image.fromarray(color_image)
#         self._color_bar = ImageTk.PhotoImage(image=img)
#         self.create_image(0, 0, image=self._color_bar, anchor='nw')


""" ImageAcquisitionThread

This class derives from threading.Thread and is given a TLCamera instance during initialization. When started, the 
thread continuously acquires frames from the camera and converts them to PIL Image objects. These are placed in a 
queue.Queue object that can be retrieved using get_output_queue(). The thread doesn't do any arming or triggering, 
so users will still need to setup and control the camera from a different thread. Be sure to call stop() when it is 
time for the thread to stop.

"""


class ImageAcquisitionThread(threading.Thread):

    def __init__(self, camera):
        super(ImageAcquisitionThread, self).__init__()
        self._camera = camera
        self._previous_timestamp = 0

        if self._camera.camera_sensor_type != SENSOR_TYPE.BAYER:
            self._is_color = False
        else:
            self._mono_to_color_sdk = MonoToColorProcessorSDK()
            self._image_width = self._camera.image_width_pixels
            self._image_height = self._camera.image_height_pixels
            self._mono_to_color_processor = self._mono_to_color_sdk.create_mono_to_color_processor(
                SENSOR_TYPE.BAYER,
                self._camera.color_filter_array_phase,
                self._camera.get_color_correction_matrix(),
                self._camera.get_default_white_balance_matrix(),
                self._camera.bit_depth
            )
            self._is_color = True

        self._bit_depth = camera.bit_depth
        self._camera.image_poll_timeout_ms = 0

        # Create two separate queues for each canvas
        self._image_queue1 = queue.Queue(maxsize=2)
        self._image_queue2 = queue.Queue(maxsize=2)
        
        self._stop_event = threading.Event()

    def get_output_queue1(self):
        return self._image_queue1

    def get_output_queue2(self):
        return self._image_queue2

    def stop(self):
        self._stop_event.set()

    def _get_image_for_canvas1(self, frame):
        # Generate a specific image for canvas 1 (e.g., Quadview data)
        width = frame.image_buffer.shape[1]
        height = frame.image_buffer.shape[0]
        with  PolarizationProcessorSDK() as polarization_sdk:           
            with polarization_sdk.create_polarization_processor() as polarization_processor:
                unprocessed_image = frame.image_buffer.reshape(int(height), int(width))
                unprocessed_image = frame.image_buffer >> (self._bit_depth - 8)  # this is the raw image data
                
                output_quadview = np.zeros(shape=(int(height/2), int(width/2)))  # initialize array for QuadView data
                # Top Left Quadrant =
                output_quadview[0:int(height / 4), 0:int(width / 4)] = \
                    unprocessed_image[0::4, 0::4]  # (0,0): top left rotation == camera_polar_phase
                # Top Right Quadrant =
                output_quadview[0:int(height / 4), int(width / 4):int(width / 2)] = \
                    unprocessed_image[0::4, 1::4]  # (0,1): top right rotation
                # Bottom Left Quadrant =
                output_quadview[int(height / 4):int(height / 2), 0:int(width / 4)] = \
                    unprocessed_image[1::4, 0::4]  # (1,0): bottom left rotation
                # Bottom Right Quadrant =
                output_quadview[int(height / 4):int(height / 2), int(width / 4):int(width / 2)] = \
                    unprocessed_image[1::4, 1::4]  # (1,1): bottom right rotation
                # Display QuadView
                quadview_image = Image.fromarray(output_quadview) 
                  
        return Image.fromarray(output_quadview)

    def _get_image_for_canvas2(self, frame):
    # Generate a different image for canvas 2 (e.g., another part of the image)
        width = frame.image_buffer.shape[1]
        height = frame.image_buffer.shape[0]
        with PolarizationProcessorSDK() as polarization_sdk:           
            with polarization_sdk.create_polarization_processor() as polarization_processor:
                unprocessed_image = frame.image_buffer.reshape(int(height), int(width))
                unprocessed_image = unprocessed_image >> (self._bit_depth - 8)  # this is the raw image data
                
                V_norm = unprocessed_image[0::4, 0::4] / 255
                A_norm = unprocessed_image[0::4, 1::4] / 255
                D_norm = unprocessed_image[1::4, 0::4] / 255
                H_norm = unprocessed_image[1::4, 1::4] / 255
                total = V_norm + A_norm + D_norm + H_norm
                
                # Normalize S0 and S1 for colormap application
                S0 = total / total
                S1 = (V_norm - H_norm) / (0.5 * total)
    
                # Apply the colormap
                S0_colored = self.apply_colormap(S0)
                S1_colored = self.apply_colormap(S1)
    
                # Create an output quadview image
                output_quadview = np.zeros((int(height/2), int(width/2), 3), dtype=np.uint8)
                # Top Left Quadrant = S0
                output_quadview[0:int(height / 4), 0:int(width / 4)] = S0_colored
                # Top Right Quadrant = S1
                output_quadview[0:int(height / 4), int(width / 4):int(width / 2)] = S1_colored
                # Bottom Left Quadrant = D
                output_quadview[int(height / 4):int(height / 2), 0:int(width / 4)] = S0_colored  # Ensure grayscale
                # Bottom Right Quadrant = H
                output_quadview[int(height / 4):int(height / 2), int(width / 4):int(width / 2)] = S1_colored  # Ensure grayscale
                
        return Image.fromarray(output_quadview)

    def apply_colormap(self, data):
        # Normalize the data to the range [0, 1]
        data_normalized = (data - np.min(data)) / (np.max(data) - np.min(data) + 1e-8)  # Adding a small epsilon to avoid division by zero
    
        # Use the desired colormap (e.g., 'RdBu')
        cmap = plt.get_cmap('RdBu')  # Change 'RdBu' to your desired colormap
        colored_image = cmap(data_normalized)[:, :, :3] * 255  # Convert to 0-255 range and keep RGB channels
        
        # Convert to uint8
        return colored_image.astype(np.uint8)


    def run(self):
        while not self._stop_event.is_set():
            try:
                frame = self._camera.get_pending_frame_or_null()
                if frame is not None:
                    # Generate different images for each queue
                    pil_image1 = self._get_image_for_canvas1(frame)
                    pil_image2 = self._get_image_for_canvas2(frame)

                    # Put the distinct images into their respective queues
                    self._image_queue1.put_nowait(pil_image1)
                    self._image_queue2.put_nowait(pil_image2)
            except queue.Full:
                pass
            except Exception as error:
                print(f"Encountered error: {error}, image acquisition will stop.")
                break
        print("Image acquisition has stopped")
        if self._is_color:
            self._mono_to_color_processor.dispose()
            self._mono_to_color_sdk.dispose()


""" Main

When run as a script, a simple Tkinter app is created with just a LiveViewCanvas widget. 

"""
if __name__ == "__main__":
    with TLCameraSDK() as sdk:
        camera_list = sdk.discover_available_cameras()
        with sdk.open_camera(camera_list[0]) as camera:

            print("Generating app...")
            root = tk.Tk()
            root.title(camera.name)

            image_acquisition_thread = ImageAcquisitionThread(camera)

            # Create two canvas widgets with smaller fixed sizes
            canvas1 = LiveViewCanvas(parent=root, image_queue=image_acquisition_thread.get_output_queue1(), canvas_width=900, canvas_height=900)
            canvas2 = LiveViewCanvas(parent=root, image_queue=image_acquisition_thread.get_output_queue2(), canvas_width=600, canvas_height=600)
            big_font = font.Font(size=16)
            # Pack canvases explicitly
            canvas1.pack(side="left", fill="both", expand=True)
            canvas2.pack(side="right", fill="both", expand=True)
            tk.Label(root, text="V", font=big_font,fg="white", bg="black").place(x=10, y=10)
            tk.Label(root, text="H", font=big_font,fg="white", bg="black").place(x=460, y=460)
            tk.Label(root, text="D", font=big_font,fg="white", bg="black").place(x=10, y=460)
            tk.Label(root, text="A", font=big_font,fg="white", bg="black").place(x=460, y=10)
            
            print("Setting camera parameters...")
            camera.frames_per_trigger_zero_for_unlimited = 0
            camera.arm(2)
            camera.issue_software_trigger()

            print("Starting image acquisition thread...")
            image_acquisition_thread.start()

            print("App starting")
            root.mainloop()

            print("Waiting for image acquisition thread to finish...")
            image_acquisition_thread.stop()
            image_acquisition_thread.join()

            print("Closing resources...")

    print("App terminated. Goodbye!")


