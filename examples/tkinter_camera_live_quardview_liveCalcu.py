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
                S0 = total / 2  # S0 normalization
                S1 = (V_norm - H_norm) / (0.5 * total)  # S1 normalization
                S2 = (A_norm - D_norm)/ (0.5 * total)  # S2 normalization
                Dop=np.sqrt(S1**2+S2**2)/S0
                # w,h=len(S1)
                
                # Apply the colormap
                S0_colored = self.apply_colormap_hot(S0)
                S1_colored = self.apply_colormap(S1)
                S2_colored = self.apply_colormap(S2)
                Dop_colored = self.apply_colormap_hot(Dop)
                
                # Create an output quadview image
                output_quadview = np.zeros((int(height/2), int(width/2), 3), dtype=np.uint8)
                # Top Left Quadrant = S0
                output_quadview[0:int(height / 4), 0:int(width / 4)] = S0_colored
                # Top Right Quadrant = S1
                output_quadview[0:int(height / 4), int(width / 4):int(width / 2)] = S1_colored
                # Bottom Left Quadrant = S2
                output_quadview[int(height / 4):int(height / 2), 0:int(width / 4)] = Dop_colored  # Ensure grayscale
                # Bottom Right Quadrant = S3
                output_quadview[int(height / 4):int(height / 2), int(width / 4):int(width / 2)] = S2_colored  # Ensure grayscale
                
                
                
                # Create and add the seismic color bar
                color_bar_height = int(height / 2)  # Height of the color bar
                color_bar_width = 40   # Width of the color bar
                color_bar = np.zeros((color_bar_height, color_bar_width, 3), dtype=np.uint8)
                color_bar_hot = np.zeros((color_bar_height, color_bar_width, 3), dtype=np.uint8)
                new_matrix=np.ones((color_bar_height, 15,3),dtype=np.uint8)*255
                
                S0_Dop=np.vstack((output_quadview[0:int(height / 4), 0:int(width / 4)], output_quadview[int(height / 4):int(height / 2), 0:int(width / 4)]))
                S1_S2=np.vstack((output_quadview[0:int(height / 4), int(width / 4):int(width / 2)], output_quadview[int(height / 4):int(height / 2), int(width / 4):int(width / 2)]))
                
                # Create a vertical gradient based on the colormap
                gradient = np.linspace(1,0, color_bar_height)  # Create an array from 1 to 0
                # Apply the colormap to the gradient
                color_image = plt.get_cmap('seismic')(gradient)  # This gives an array of shape (height, 4)
                color_image_hot = plt.get_cmap('hot')(gradient)
                # Convert to RGB (discarding the alpha channel) and scale to 0-255
                color_bar = (color_image[:, :3] * 255).astype(np.uint8)  # Shape will be (height, 3) 
                color_bar_hot = (color_image_hot[:, :3] * 255).astype(np.uint8)  # Shape will be (height, 3)
                # Reshape to (color_bar_height, color_bar_width, 3)
                color_bar_3d = np.tile(color_bar[:, np.newaxis, :], (1, color_bar_width, 1)) 
                color_bar_3d_hot = np.tile(color_bar_hot[:, np.newaxis, :], (1, color_bar_width, 1))
                
                
                S0_Dop_c=np.hstack((S0_Dop, new_matrix,color_bar_3d_hot))
                S1_S2_c=np.hstack((S1_S2, new_matrix,color_bar_3d))
                # Combine the quadview image and the color bar
                output_quadview_with_colorbar = np.hstack((S0_Dop_c,new_matrix, S1_S2_c))
            
        return Image.fromarray(output_quadview_with_colorbar)

   

    def apply_colormap(self, data):
        
        matrix = np.clip(data, -1, 1)
            # Use the 'seismic' colormap
        cmap = plt.get_cmap('seismic')
        normalized_data = (matrix + 1) / 2
        # Apply the colormap without normalizing the data again
        colored_image = cmap(normalized_data)  # This gives a float array in the range [0, 1]
        # Convert to uint8 for image display
        colored_image_uint8 = (colored_image[:, :, :3] * 255).astype(np.uint8)
        return colored_image_uint8
    
    def apply_colormap_hot(self, data):
        
        matrix = np.clip(data, 0, 1)    
        cmap = plt.get_cmap('hot')
        # Apply the colormap without normalizing the data again
        colored_image = cmap(matrix)  # This gives a float array in the range [0, 1]   
        # Convert to uint8 for image display
        colored_image_uint8 = (colored_image[:, :, :3] * 255).astype(np.uint8)
        return colored_image_uint8


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
            
            canvas_width, canvas_height=800,800
            # Create two canvas widgets with fixed sizes
            canvas1 = LiveViewCanvas(parent=root, image_queue=image_acquisition_thread.get_output_queue1(), canvas_width=canvas_width, canvas_height=canvas_height)
            canvas2 = LiveViewCanvas(parent=root, image_queue=image_acquisition_thread.get_output_queue2(), canvas_width=canvas_width, canvas_height=canvas_height)
            
            # Create the color bar canvas
            # colorbar = ColorBarCanvas(parent=root)

            # Pack canvases and colorbar
            canvas1.pack(side="left", fill="both", expand=True)
            canvas2.pack(side="right", fill="both", expand=True)
            # colorbar.pack(side="right", fill="x")
            

            big_font = font.Font(size=16)
            tk.Label(root, text="V", font=big_font, fg="white", bg="black").place(x=0, y=0)
            tk.Label(root, text="H", font=big_font, fg="white", bg="black").place(x=canvas_width/2, y=canvas_height/2)
            tk.Label(root, text="D", font=big_font, fg="white", bg="black").place(x=0, y=canvas_height/2)
            tk.Label(root, text="A", font=big_font, fg="white", bg="black").place(x=canvas_width/2, y=0)

            tk.Label(root, text="S1", font=big_font, fg="white", bg="black").place(x=canvas_width*3/2+20, y=0)
            tk.Label(root, text="S0", font=big_font, fg="white", bg="black").place(x=canvas_width+20, y=0)
            tk.Label(root, text="S2", font=big_font, fg="white", bg="black").place(x=canvas_width*3/2+20, y=canvas_height/2)
            tk.Label(root, text="DoP", font=big_font, fg="white", bg="black").place(x=canvas_width+20, y=canvas_height/2)
            
            
            
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




