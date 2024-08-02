import os
import os.path as osp
import glob
import shutil
import json
import numpy as np

from read_write_model import read_cameras_binary
from config import SCENE

PREP_DIR="/ubc/cs/research/kmyi/matthew/backup_copy/raw_real_ednerf_data/work_dir"
# VID_DIR="/ubc/cs/research/kmyi/matthew/backup_copy/raw_real_ednerf_data/Videos"
# EV_DIR="/ubc/cs/research/kmyi/matthew/backup_copy/raw_real_ednerf_data/ecam_code/raw_events"
# # REL_CAM_PATH="/ubc/cs/research/kmyi/matthew/backup_copy/raw_real_ednerf_data/ecam_code/raw_events/calib_checker/rel_cam.json"
# REL_CAM_PATH="/ubc/cs/research/kmyi/matthew/backup_copy/raw_real_ednerf_data/ecam_code/raw_events/calib_new_v4/rel_cam.json"

VID_DIR="/ubc/cs/research/kmyi/matthew/backup_copy/raw_real_ednerf_data/rgb-evs-cam-drivers/data_rgb"
EV_DIR="/ubc/cs/research/kmyi/matthew/backup_copy/raw_real_ednerf_data/rgb-evs-cam-drivers/ev_recordings"
REL_CAM_PATH="/ubc/cs/research/kmyi/matthew/backup_copy/raw_real_ednerf_data/rgb-evs-cam-drivers/ev_recordings/calib_v7/rel_cam.json"
#RGB_CAM_PATH="/ubc/cs/research/kmyi/matthew/backup_copy/raw_real_ednerf_data/rgb-evs-cam-drivers/data_rgb/calib_v8_recons/sparse/0/cameras.bin"
#RGB_CAM_PATH="/ubc/cs/research/kmyi/matthew/backup_copy/raw_real_ednerf_data/rgb-evs-cam-drivers/data_rgb/calib_v11_recons/sparse/0/cameras.bin"
#RGB_CAM_PATH="/ubc/cs/research/kmyi/matthew/backup_copy/raw_real_ednerf_data/rgb-evs-cam-drivers/data_rgb/calib_v12_recons/sparse/0/cameras.bin"
#RGB_CAM_PATH="/ubc/cs/research/kmyi/matthew/backup_copy/raw_real_ednerf_data/rgb-evs-cam-drivers/data_rgb/calib_v13_recons/sparse/0/cameras.bin"
#RGB_CAM_PATH="/ubc/cs/research/kmyi/matthew/backup_copy/raw_real_ednerf_data/rgb-evs-cam-drivers/data_rgb/calib_v15_recons/sparse/0/cameras.bin"
RGB_CAM_PATH="/ubc/cs/research/kmyi/matthew/backup_copy/raw_real_ednerf_data/rgb-evs-cam-drivers/data_rgb/calib_v16_recons/sparse/0/cameras.bin"




def load_colmap_cam(cam_f):
    # fx, fy, cx, cy, k1, k2, p1, p2
    cam_params = read_cameras_binary(RGB_CAM_PATH)[1].params
    K, D = cam_params[:4], cam_params[4:]

    fx, fy, cx, cy = K
    K = np.array([[fx, 0, cx],
                  [0, fy, cy],
                  [0, 0, 1]])
    return K, D

def copy_rel_cam(dst_f):
    if RGB_CAM_PATH is None:
        shutil.copyfile(REL_CAM_PATH, dst_f)
    else:
        print("updating rgb intrinsics")
        with open(REL_CAM_PATH, "r") as f:
            cam_data = json.load(f)

        K, D = load_colmap_cam(RGB_CAM_PATH)
        cam_data["M1"] = K.tolist()
        cam_data["dist1"] = D.reshape(-1,1).tolist()

        with open(dst_f, "w") as f:
            json.dump(cam_data, f, indent=2)



def prep_data_for_format(scene_name = SCENE):
    dst_dir = osp.join(PREP_DIR, scene_name)
    os.makedirs(dst_dir, exist_ok=True)
    print(f"working on {scene_name}")


    print("copying colmap")
    src_colmap_dir = osp.join(VID_DIR, f"{scene_name}_recons")
    dst_colmap_dir = osp.join(dst_dir, f"{scene_name}_recon")
    # shutil.copytree(src_colmap_dir, dst_colmap_dir)
    os.symlink(src_colmap_dir, dst_colmap_dir) if not osp.islink(dst_colmap_dir) else None
 
    print("copying events")
    src_event_f = osp.join(EV_DIR, scene_name, "events.h5")
    dst_event_f = osp.join(dst_dir, "events.h5")
    # shutil.copyfile(src_event_f, dst_event_f)
    os.symlink(src_event_f, dst_event_f) if not osp.islink(dst_event_f) else None

    src_proc_evs_f = osp.join(EV_DIR, scene_name, "processed_events.h5")
    if osp.exists(src_proc_evs_f):
        dst_proc_evs_f = osp.join(dst_dir, "processed_events.h5")
        os.symlink(src_proc_evs_f, dst_proc_evs_f) if not osp.islink(dst_proc_evs_f) else None
 
    print("copying triggers")
    src_trigger_f = osp.join(EV_DIR, scene_name, "st_triggers.txt")  # change to desire trigger
    # src_trigger_f = osp.join(VID_DIR, scene_name, "triggers.txt")
    dst_trigger_f = osp.join(dst_dir, "triggers.txt")
    shutil.copyfile(src_trigger_f, dst_trigger_f)
 
    src_trigger_f = osp.join(EV_DIR, scene_name, "st_triggers.txt")
    dst_trigger_f = osp.join(dst_dir, "st_triggers.txt")
    shutil.copyfile(src_trigger_f, dst_trigger_f)
 
    src_trigger_f = osp.join(EV_DIR, scene_name, "end_triggers.txt")
    dst_trigger_f = osp.join(dst_dir, "end_triggers.txt")
    shutil.copyfile(src_trigger_f, dst_trigger_f)

    print("copying relative cams")
    dst_rel_cam_f = osp.join(dst_dir, "rel_cam.json")
    #shutil.copyfile(REL_CAM_PATH, dst_rel_cam_f)
    copy_rel_cam(dst_rel_cam_f)

    print(f"complete preperation for {scene_name}")


if __name__ == "__main__":
    prep_data_for_format()
