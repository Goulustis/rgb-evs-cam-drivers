import PySpin
import os
from datetime import datetime

from config import FPS, SCENE, RUN_DURATION, RGB_SAVE_DIR, GREEN, YELLOW, RESET, EXP_TIME


TOTAL_FRAMES_SAVED = 0

def save_raw_image(image, folder):
    """Save an image in raw format to the specified folder with a microsecond timestamp as the filename."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")  # Format: YYYYMMDD_HHMMSS_microseconds
    filename = f'raw_image_{timestamp}.raw'
    path = os.path.join(folder, filename)
    image.Save(path)
    
    global TOTAL_FRAMES_SAVED
    TOTAL_FRAMES_SAVED += 1

def main(desired_fps=FPS, duration_seconds=RUN_DURATION, exp_time=EXP_TIME, save_folder='designated_folder'):
    # Ensure the save folder exists
    os.makedirs(save_folder, exist_ok=True)

    # Initialize the camera system
    system = PySpin.System.GetInstance()
    cam_list = system.GetCameras()
    cam = cam_list.GetByIndex(0)

    try:
        # Initialize and configure the camera
        cam.Init()
        cam.AcquisitionFrameRateEnable.SetValue(True)
        cam.ExposureTime.SetValue(exp_time)
        cam.AcquisitionFrameRate.SetValue(desired_fps)
        gain_node = PySpin.CFloatPtr(nodemap.GetNode("Gain"))
        gain_node.SetValue(6.9)

        ############################## set to 12 bit
        nodemap = cam.GetNodeMap()
        # Access the PixelFormat enumeration node
        node_pixel_format = PySpin.CEnumerationPtr(nodemap.GetNode("PixelFormat"))
        print(PySpin.IsAvailable(node_pixel_format), PySpin.IsWritable(node_pixel_format))
        if PySpin.IsAvailable(node_pixel_format) and PySpin.IsWritable(node_pixel_format):
            # Retrieve the 12-bit pixel format node
            node_pixel_format_12bit = node_pixel_format.GetEntryByName("BayerRG16")
            if PySpin.IsAvailable(node_pixel_format_12bit) and PySpin.IsReadable(node_pixel_format_12bit):
                pixel_format_12bit = node_pixel_format_12bit.GetValue()
                # Set pixel format to 12-bit
                node_pixel_format.SetIntValue(pixel_format_12bit)
                print("Pixel format set to 12-bit.")
            else:
                print("12-bit pixel format not available.")
                return
        else:
            print("Pixel format not available or not writable.")
            return
        ############################333
        
        print(f"{GREEN}RGB CAMERA STARTED!! RUNNING AT {desired_fps} fps for {duration_seconds} sec {RESET}")


        cam.AcquisitionMode.SetValue(PySpin.AcquisitionMode_Continuous)

        # Start capturing images
        cam.BeginAcquisition()

        start_time = datetime.now().timestamp()
        end_time = start_time + duration_seconds

        while datetime.now().timestamp() < end_time:
            # Retrieve the next available image
            image_result = cam.GetNextImage()

            if image_result.IsIncomplete():
                print("Image incomplete with image status", image_result.GetImageStatus())
            else:
                # Save the raw image to the specified folder with a microsecond timestamp in the filename
                save_raw_image(image_result, save_folder)

            # Release the image to prepare for the next one
            image_result.Release()

        print(f"{YELLOW} RGB: Reached the specified duration of {duration_seconds} seconds. Stopping.{RESET}")

    finally:
        # End image acquisition
        cam.EndAcquisition()
        cam.DeInit()
        del cam
        cam_list.Clear()
        system.ReleaseInstance()

    print(f"{GREEN}Total frames saved: {TOTAL_FRAMES_SAVED} {RESET}")

if __name__ == '__main__':

    save_dir = f"{RGB_SAVE_DIR}/{SCENE}"
    main(save_folder=save_dir)

