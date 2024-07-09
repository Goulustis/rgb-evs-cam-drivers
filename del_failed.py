from config import SCENE, RGB_SAVE_DIR, EVS_SAVE_DIR, GREEN, RED, RESET
import os.path as osp
import shutil
import glob
import os

user_input = input(f"continue with deleting \"{RED}{SCENE}{RESET}\"? (yes/no): {RESET}").lower().strip()

# Check the user's input
if user_input != "yes":
    print("Exiting the script.")
    quit()  # This will exit the script

rgb_f = osp.join(RGB_SAVE_DIR, SCENE)
evs_f = osp.join(EVS_SAVE_DIR, SCENE)

rgb_dirs = sorted(glob.glob(osp.join(RGB_SAVE_DIR, SCENE + "*")))
evs_dirs = sorted(glob.glob(osp.join(EVS_SAVE_DIR, SCENE + "*")))
to_del_dirs = rgb_dirs + evs_dirs

for del_dir in to_del_dirs:
    user_input = input(f"deleting \"{RED}{del_dir}{RESET}\"? (yes/no): {RESET}").lower().strip()
    if user_input != "yes":
        continue
    
    try:
        shutil.rmtree(del_dir)
    except:
        os.remove(del_dir)

    print(f"{GREEN} removed {del_dir} {RESET}")