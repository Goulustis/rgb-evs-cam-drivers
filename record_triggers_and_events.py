import numpy as np
from metavision_core.event_io import EventsIterator, H5EventsWriter
from metavision_core.event_io.raw_reader import initiate_device
from metavision_ml.utils.h5_writer import HDF5Writer
import os.path as osp
import os
from tqdm import tqdm
import time
from utils import read_bias, set_all_biases, write_bias

from config import SCENE, RUN_DURATION, EVS_SAVE_DIR, USE_BIAS_CONFIG


trigger_type = np.dtype({'names':['p','t','id'], 
                         'formats':['<i2','<i8','<i2'], 
                         'offsets':[0,8,16], 
                         'itemsize':24})

# save_dir = "raw_events/calib_checker"
save_dir = f"{EVS_SAVE_DIR}/{SCENE}"
# save_dir = "raw_events/scratch"
os.makedirs(save_dir, exist_ok=True)
def main():
    sec = RUN_DURATION
    max_time = sec*1e6
    trigger_save_path = osp.join(save_dir, "triggers.npy")
    event_path = osp.join(save_dir, "events.h5")
    trigger_path = osp.join(trigger_save_path)

    device = initiate_device("", **{"use_external_triggers":[0]})
    bias_obj = device.get_i_ll_biases()
    if osp.exists("biases.bias") and USE_BIAS_CONFIG:
        bias_config = read_bias("biases.bias")
        set_all_biases(bias_obj, bias_config)
        write_bias(bias_config, osp.join(save_dir, "bias.bias"))
        


    e_iter = EventsIterator.from_device(device, delta_t=50000, max_duration=max_time)
    print("camera on")

    height, width = e_iter.get_size()
    e_writer = H5EventsWriter(event_path, height=height, width=width, compression_backend="zstandard")
    is_rgb_started = False 

    is_printed = False
    trigger_ls = []
    event_ls = []
    pbar = tqdm(total=max_time)
    print("camera running")
    print("saving triggers to", trigger_save_path)
    st_time = time.time()
    for evs in e_iter:
        if evs.size != 0:
            if not is_printed:
                is_printed=True 
                print("event camera running")
            triggers = e_iter.reader.get_ext_trigger_events()
            
            if len(triggers) > 0:
                print("seeing triggers")
            else:
                print("not seeing triggers")

                    
        if evs.size != 0:
            e_writer.write(evs)
            # event_ls.append(evs)

            pbar.n = evs["t"].max()
            pbar.refresh()

        print("time left", sec - (time.time() - st_time))
    
    e_writer.close()
    # trig_writer.close()
    # trigger_ls = np.concatenate(trigger_ls)
    # np.save(trigger_path, trigger_ls)
    np.save(trigger_path, e_iter.reader.get_ext_trigger_events())
    print("done writing")


if __name__ == "__main__":
    main()
