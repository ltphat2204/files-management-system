import os
from typing import List
from FAT32 import FAT32
from NTFS import NTFS

def GetAllAvailableVolumes() -> List[str]:
    return [chr(x) + ":" for x in range(65, 91) if os.path.exists(chr(x) + ":")]

def GetVolumeInformation(volume_name) -> dict[str, str]:
    if FAT32.check_fat32(volume_name):
        vol = FAT32(volume_name)
    elif NTFS.check_ntfs(volume_name):
        vol = NTFS(volume_name)
    else:
        raise Exception("Unsupported volume type")

    return vol.GetInformation()

def GetVolumeHandler(volume_name):
    if FAT32.check_fat32(volume_name):
        vol = FAT32(volume_name)
    elif NTFS.check_ntfs(volume_name):
        vol = NTFS(volume_name)
    else:
        raise Exception("Unsupported volume type")

    return vol