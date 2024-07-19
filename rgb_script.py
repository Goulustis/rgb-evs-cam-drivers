import PySpin
import os
from datetime import datetime
import json
import os.path as osp

from config import (FPS, SCENE, RUN_DURATION, RGB_SAVE_DIR, 
                    GREEN, YELLOW, RESET, EXP_TIME, USE_SIXTEEN_BIT, GAIN)


TOTAL_FRAMES_SAVED = 0

def save_raw_image(image, folder):
    """Save an image in raw format to the specified folder with a microsecond timestamp as the filename."""
    timestamp = image.GetTimeStamp()  # in microsec
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

        nodemap = cam.GetNodeMap()
        gain_node = PySpin.CFloatPtr(nodemap.GetNode("Gain"))
        gain_node.SetValue(GAIN)

        # Access the PixelFormat enumeration node
        if USE_SIXTEEN_BIT:
            node_pixel_format = PySpin.CEnumerationPtr(nodemap.GetNode("PixelFormat"))
            node_pixel_format_16bit = node_pixel_format.GetEntryByName("BayerRG16")
            pixel_format_16bit = node_pixel_format_16bit.GetValue()
            node_pixel_format.SetIntValue(pixel_format_16bit)
        
        print(f"{GREEN}RGB CAMERA STARTED!! RUNNING AT {desired_fps} fps for {duration_seconds} sec {RESET}")


        cam.AcquisitionMode.SetValue(PySpin.AcquisitionMode_Continuous)

        start_time = datetime.now().timestamp()
        end_time = start_time + duration_seconds

        img_idxs = 0
        successes = []
        time_stamps = []
        
        # Start capturing images
        cam.BeginAcquisition()
        while datetime.now().timestamp() < end_time:
            # Retrieve the next available image
            image_result = cam.GetNextImage()

            if image_result.IsIncomplete():
                print("Image incomplete with image status", image_result.GetImageStatus())
            else:
                # Save the raw image to the specified folder with a microsecond timestamp in the filename
                save_raw_image(image_result, save_folder)
                successes.append(img_idxs)
                time_stamps.append(image_result.GetTimeStamp())
            img_idxs += 1

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
    with open(osp.join(save_dir, "metadata.json"), "w") as f:
        metadata = {"exposure_time": exp_time,
                    "is_sixteen_bit":USE_SIXTEEN_BIT,
                    "success_idxs": successes}
        json.dump(metadata, f, indent=2)

if __name__ == '__main__':

    save_dir = f"{RGB_SAVE_DIR}/{SCENE}"
    main(save_folder=save_dir)

