import os
import torch
import warnings


def get_global_device():
    # TOBEREMOVE
    warnings.warn("get_global_device is deprecated and will be removed in future versions. Please manage device settings within your application context.", DeprecationWarning)
    env_device = os.environ.get('LMT_DEVICE')
    if env_device:
        return env_device
    return "cuda" if torch.cuda.is_available() else "cpu"


def set_global_device(device: str):
    # TOBEREMOVE
    warnings.warn("set_global_device is deprecated and will be removed in future versions. Please manage device settings within your application context.", DeprecationWarning)
    os.environ['LMT_DEVICE'] = device
    return device
