from tqdm import tqdm
import numpy as np
from PIL import Image
import argparse
import os
import os.path as osp
import glob
import cv2
from concurrent import futures
from functools import partial
from config import RGB_SAVE_DIR, SCENE, USE_SIXTEEN_BIT
from tqdm import tqdm
import json

H, W = 1080, 1440

def parallel_map(f, iterable, max_threads=None, show_pbar=False, desc="", **kwargs):
  """Parallel version of map()."""
  with futures.ThreadPoolExecutor(max_threads) as executor:
    if show_pbar:
      results = tqdm(
          executor.map(f, iterable, **kwargs), total=len(iterable), desc=desc)
    else:
      results = executor.map(f, iterable, **kwargs)
    return list(results)

def raw_to_rgb(raw_f, sixteen_bit=USE_SIXTEEN_BIT, cnst=65536):
    dtype = np.uint8 if not sixteen_bit else np.uint16
    with open(raw_f, "rb") as f:
      img_data = np.frombuffer(f.read(), dtype, H*W).reshape(H, W)
      img = cv2.cvtColor(img_data, cv2.COLOR_BAYER_BG2BGR)
    
    if sixteen_bit:
      img = img.astype(np.float32)/cnst
      img = (np.clip(img, 0, 1)*255).astype(np.uint8)

    return img

def transform_img_and_save(inp, dst_dir, cnst=None):
    """
    inp = (raw_f:str, img_idx:int)
    """

    raw_f, img_idx = inp

    dst_f = osp.join(dst_dir, f"{str(img_idx).zfill(5)}.png")
    img = raw_to_rgb(raw_f, cnst=cnst)
    save_stat = cv2.imwrite(dst_f, img)
    assert save_stat, "save failed !"


def main(input_dir, trigger_f=None):
    print("working on", osp.basename(input_dir))
    raw_fs = sorted(glob.glob(osp.join(input_dir, "*.raw")))


    dst_dir = osp.join(input_dir + "_recons", "images")
    os.makedirs(dst_dir, exist_ok=True)
    map_fn = partial(transform_img_and_save, dst_dir=dst_dir)
    inp_ls = list(zip(raw_fs, range(len(raw_fs))))

    if trigger_f is not None:
      trig = np.loadtxt(trigger_f)
      inp_ls = inp_ls[:(len(trig) + 3)]
    parallel_map(map_fn, inp_ls, show_pbar=True, desc="processing raw")
  
def main_sixteen(input_dir, trigger_f=None):
  print("working on", osp.basename(input_dir))
  raw_fs = sorted(glob.glob(osp.join(input_dir, "*.raw")))

  dst_dir = osp.join(input_dir + "_recons", "images")
  os.makedirs(dst_dir, exist_ok=True)

  # find absolute constant
  def find_max(raw_f):
    with open(raw_f, "rb") as f:
      img_data = np.frombuffer(f.read(), np.uint16, H*W).reshape(H, W)
      img = cv2.cvtColor(img_data, cv2.COLOR_BAYER_BG2BGR)
      return np.percentile(img, 95)
  cnsts = parallel_map(find_max, raw_fs, show_pbar=True, desc="finding norm cnsts")
  cnst = max(cnsts)

  map_fn = partial(transform_img_and_save, dst_dir=dst_dir, cnst=cnst)
  inp_ls = list(zip(raw_fs, range(len(raw_fs))))

  if trigger_f is not None:
    trig = np.loadtxt(trigger_f)
    inp_ls = inp_ls[:(len(trig) + 3)]
  parallel_map(map_fn, inp_ls, show_pbar=True, desc="processing raw")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_dir", default=f"{RGB_SAVE_DIR}/{SCENE}")
    parser.add_argument("-t", "--trigger_f", default=None) 
    args = parser.parse_args()

    metadatjson_f = osp.join(args.input_dir, "metadata.json")
    is_sixteen = False
    if osp.exists(metadatjson_f):
      with open(metadatjson_f, "r") as f:
        is_sixteen = json.load(f)["is_sixteen_bit"]
    
    if is_sixteen:
      main_sixteen(args.input_dir, args.trigger_f)
    else:
      main(args.input_dir, args.trigger_f)
      
# img = raw_to_rgb("SingleCapture_12bit.raw", True).astype(np.float32)
# print(np.percentile(img, 95))
# img = img / np.percentile(img, 95)
# 
# import matplotlib.pyplot as plt
# plt.imshow(img[...,::-1])
# plt.show()
