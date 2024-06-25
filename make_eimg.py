import cv2
import argparse
import os 
import os.path as osp
from tqdm import tqdm
import numpy as np
import shutil
from metavision_core.event_io import EventsIterator

import os
import os.path as osp
from tqdm import tqdm

from config import EVS_SAVE_DIR, SCENE

BKG_COL = [29, 37, 52][::-1]
POS_COL = [255, 255, 255]
NEG_COL = [53, 124 ,199][::-1]

def ev_to_img(x, y, p, e_thresh=0.15):
    """
    input:
        evs (np.array [type (t, x, y, p)]): events such that t in [t_st, t_st + time_delta]
    return:
        event_img (np.array): of shape (h, w)
    """
    e_thresh = 0.15
    h, w = 720, 1280

    pos_p = p==1
    neg_p = p==0

    e_cnt = np.zeros((h,w), dtype=np.int32)
    
    np.add.at(e_cnt, (y[pos_p], x[pos_p]), 1)
    np.add.at(e_cnt, (y[neg_p], x[neg_p]), -1)
    
    # assert np.abs(e_img).max() < np.iinfo(np.int8).max, "type needs to be bigger"

    eimg = np.zeros((h, w, 3), dtype=np.uint8)
    eimg[:] = BKG_COL
    eimg[e_cnt > 0] = POS_COL
    eimg[e_cnt < 0] = NEG_COL

    return eimg



def main():
    event_f = f"{EVS_SAVE_DIR}/{SCENE}/events.h5"
    save_dir = f"eimgs/{SCENE}"
    # st_triggers = np.loadtxt(osp.join(osp.dirname(event_f), "st_triggers.txt"))
    n_frames = 120 
    # st_triggers = st_triggers[: n_frames + 1]
    os.makedirs(save_dir, exist_ok=True)

    eventIter= EventsIterator(event_f, delta_t=5000)
    eimgs = []

    print("making event images")
    trig_idx = 0
    xb, yb, tb, pb = [],[],[],[]
    # st_t, end_t = st_triggers[trig_idx], st_triggers[trig_idx + 1]
    pbar = tqdm(total=n_frames)
    for events in eventIter:
        xs, ys, ts, ps = [events[e] for e in list("xytp")]
        xb.append(xs), yb.append(ys), tb.append(ts), pb.append(ps)

        # if ts[-1] > end_t:
        # xs, ys, ts, ps = [np.concatenate(e) for e in [xb, yb, tb, ps]]
        # cond = (st_t < ts) & (ts <= end_t)
        # eimg = ev_to_img(xs[cond], ys[cond], ps[cond])
        # cond = (st_t < ts) & (ts <= end_t)
        eimg = ev_to_img(xs, ys, ps)
        eimg = np.abs(eimg)
        eimgs.append(eimg)

        save_f = osp.join(save_dir, f"{str(trig_idx).zfill(3)}.png")
        u = cv2.imwrite(save_f, eimg)
        assert u

        # xb, yb, tb, pb = xs[~cond], ys[~cond], ts[~cond], ps[~cond]
        trig_idx += 1
        # st_t, end_t = st_triggers[trig_idx], st_triggers[trig_idx + 1]
        pbar.update(1)
        
        if trig_idx > n_frames:
            pbar.close()
            break

    # print('saving event images')
    # for i, eimg in enumerate(eimgs):
    #     eimg[eimg > 100] = 0
    #     eimg = (eimg/eimg.max() * 255).astype(np.uint8)
    #     eimg = eimg.astype(np.uint8)
    #     save_f = osp.join(save_dir, f"{str(i).zfill(3)}.png")
    #     cv2.imwrite(save_f, eimg)

    print("done")


main()



