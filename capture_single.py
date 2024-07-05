import PySpin

def capture_and_save_12bit_raw():
    # Retrieve singleton reference to system object
    system = PySpin.System.GetInstance()

    # Get camera list
    cam_list = system.GetCameras()

    if cam_list.GetSize() == 0:
        # Release system instance before exiting
        system.ReleaseInstance()
        print("No camera detected.")
        return None

    # Use the first camera on the list
    cam = cam_list.GetByIndex(0)

    try:
        # Initialize the camera
        cam.Init()

        # Retrieve GenICam nodemap
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

        gain_node = PySpin.CFloatPtr(nodemap.GetNode("Gain"))
        gain_node.SetValue(18)
        cam.ExposureTime.SetValue(30000)

        # Set acquisition mode to single frame
        cam.AcquisitionMode.SetValue(PySpin.AcquisitionMode_SingleFrame)

        # Begin acquiring images
        cam.BeginAcquisition()

        try:
            # Retrieve the next received image and ensure image completion
            image_result = cam.GetNextImage()
            if image_result.IsIncomplete():
                print(f"Image incomplete with image status {image_result.GetImageStatus()}...")
            else:
                # Save image in raw format
                filename = "SingleCapture_12bit.raw"
                image_result.Save(filename)
                print(f"Image saved in raw format at '{filename}'")

                # Release image
                image_result.Release()

        finally:
            # End acquisition
            cam.EndAcquisition()

    finally:
        # Deinitialize camera
        cam.DeInit()
        del cam
        cam_list.Clear()
        system.ReleaseInstance()

# Call the function to capture an image
capture_and_save_12bit_raw()

