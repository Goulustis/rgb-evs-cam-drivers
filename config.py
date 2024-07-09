## data saving config
SCENE = "jeff_v9"
RGB_SAVE_DIR = "data_rgb"
EVS_SAVE_DIR = "ev_recordings"

## RGB config
FPS = 30 
# EXP_TIME = 14995  # default exposure time in micro sec
EXP_TIME = 30000
USE_SIXTEEN_BIT = True
GAIN=6.9

## Whole system config
RUN_DURATION = 20  # in seconds

## Event Camera Config
USE_BIAS_CONFIG=True
BIAS_FILE="bias_configs/tuned_biases.bias"

GREEN = '\033[32m'
YELLOW = '\033[33m'
RED = '\033[31m' 
RESET = '\033[0m'
