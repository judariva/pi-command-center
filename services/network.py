"""Servicio avanzado de escaneo de red."""
import asyncio
import logging
import re
import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path

from utils.shell import run_async, run_sync
from config import config

logger = logging.getLogger(__name__)

# Base de datos OUI para fabricantes (top 100+)
OUI_DATABASE = {
    "00:00:0C": "Cisco",
    "00:1A:2B": "Ayecom",
    "00:1B:63": "Apple",
    "00:1C:B3": "Apple",
    "00:1D:4F": "Apple",
    "00:1E:C2": "Apple",
    "00:1F:5B": "Apple",
    "00:1F:F3": "Apple",
    "00:21:E9": "Apple",
    "00:22:41": "Apple",
    "00:23:12": "Apple",
    "00:23:32": "Apple",
    "00:23:6C": "Apple",
    "00:23:DF": "Apple",
    "00:24:36": "Apple",
    "00:25:00": "Apple",
    "00:25:4B": "Apple",
    "00:25:BC": "Apple",
    "00:26:08": "Apple",
    "00:26:4A": "Apple",
    "00:26:B0": "Apple",
    "00:26:BB": "Apple",
    "00:50:56": "VMware",
    "00:0C:29": "VMware",
    "00:1C:42": "Parallels",
    "08:00:27": "VirtualBox",
    "18:65:90": "Apple",
    "20:C9:D0": "Apple",
    "24:A0:74": "Apple",
    "28:6A:BA": "Apple",
    "2C:BE:08": "Apple",
    "34:C0:59": "Apple",
    "38:C9:86": "Apple",
    "3C:06:30": "Apple",
    "3C:D0:F8": "Apple",
    "40:6C:8F": "Apple",
    "44:D8:84": "Apple",
    "48:60:BC": "Apple",
    "4C:57:CA": "Apple",
    "50:EA:D6": "Apple",
    "54:26:96": "Apple",
    "54:72:4F": "Apple",
    "58:55:CA": "Apple",
    "5C:59:48": "Apple",
    "60:03:08": "Apple",
    "60:69:44": "Apple",
    "64:A5:C3": "Apple",
    "68:5B:35": "Apple",
    "68:96:7B": "Apple",
    "68:D9:3C": "Apple",
    "6C:40:08": "Apple",
    "6C:94:F8": "Apple",
    "6C:C2:6B": "Apple",
    "70:3E:AC": "Apple",
    "74:E1:B6": "Apple",
    "78:31:C1": "Apple",
    "78:CA:39": "Apple",
    "7C:6D:62": "Apple",
    "7C:D1:C3": "Apple",
    "80:E6:50": "Apple",
    "84:38:35": "Apple",
    "84:78:8B": "Apple",
    "84:FC:FE": "Apple",
    "88:63:DF": "Apple",
    "88:C6:63": "Apple",
    "8C:00:6D": "Apple",
    "8C:29:37": "Apple",
    "8C:7C:92": "Apple",
    "8C:85:90": "Apple",
    "90:8D:6C": "Apple",
    "90:B2:1F": "Apple",
    "94:E9:6A": "Apple",
    "98:01:A7": "Apple",
    "98:D6:BB": "Apple",
    "9C:F4:8E": "Apple",
    "A0:99:9B": "Apple",
    "A4:67:06": "Apple",
    "A4:D1:8C": "Apple",
    "A8:5C:2C": "Apple",
    "A8:88:08": "Apple",
    "A8:BB:CF": "Apple",
    "AC:29:3A": "Apple",
    "AC:3C:0B": "Apple",
    "AC:61:EA": "Apple",
    "AC:87:A3": "Apple",
    "AC:BC:32": "Apple",
    "AC:FD:EC": "Apple",
    "B0:34:95": "Apple",
    "B0:65:BD": "Apple",
    "B0:9F:BA": "Apple",
    "B4:18:D1": "Apple",
    "B4:F0:AB": "Apple",
    "B8:17:C2": "Apple",
    "B8:41:A4": "Apple",
    "B8:63:4D": "Apple",
    "B8:78:2E": "Apple",
    "B8:C1:11": "Apple",
    "B8:E8:56": "Apple",
    "B8:F6:B1": "Apple",
    "B8:FF:61": "Apple",
    "BC:3B:AF": "Apple",
    "BC:52:B7": "Apple",
    "BC:67:78": "Apple",
    "BC:A9:20": "Apple",
    "C0:63:94": "Apple",
    "C0:84:7A": "Apple",
    "C0:9F:42": "Apple",
    "C0:CC:F8": "Apple",
    "C4:2C:03": "Apple",
    "C8:1E:E7": "Apple",
    "C8:2A:14": "Apple",
    "C8:33:4B": "Apple",
    "C8:69:CD": "Apple",
    "C8:B5:B7": "Apple",
    "C8:E0:EB": "Apple",
    "CC:08:8D": "Apple",
    "CC:20:8C": "Apple",
    "CC:78:5F": "Apple",
    "D0:03:4B": "Apple",
    "D0:23:DB": "Apple",
    "D0:4F:7E": "Apple",
    "D4:9A:20": "Apple",
    "D4:F4:6F": "Apple",
    "D8:00:4D": "Apple",
    "D8:1D:72": "Apple",
    "D8:96:95": "Apple",
    "D8:9E:3F": "Apple",
    "D8:A2:5E": "Apple",
    "D8:BB:2C": "Apple",
    "D8:CF:9C": "Apple",
    "DC:2B:2A": "Apple",
    "DC:37:14": "Apple",
    "DC:41:5F": "Apple",
    "DC:56:E7": "Apple",
    "DC:86:D8": "Apple",
    "DC:9B:9C": "Apple",
    "E0:5F:45": "Apple",
    "E0:66:78": "Apple",
    "E0:AC:CB": "Apple",
    "E0:B5:2D": "Apple",
    "E0:C7:67": "Apple",
    "E0:F8:47": "Apple",
    "E4:25:E7": "Apple",
    "E4:8B:7F": "Apple",
    "E4:C6:3D": "Apple",
    "E4:CE:8F": "Apple",
    "E8:04:0B": "Apple",
    "E8:06:88": "Apple",
    "E8:80:2E": "Apple",
    "E8:8D:28": "Apple",
    "EC:35:86": "Apple",
    "EC:85:2F": "Apple",
    "F0:24:75": "Apple",
    "F0:99:BF": "Apple",
    "F0:B4:79": "Apple",
    "F0:C1:F1": "Apple",
    "F0:CB:A1": "Apple",
    "F0:D1:A9": "Apple",
    "F0:DB:E2": "Apple",
    "F0:DC:E2": "Apple",
    "F0:F6:1C": "Apple",
    "F4:0F:24": "Apple",
    "F4:1B:A1": "Apple",
    "F4:37:B7": "Apple",
    "F4:5C:89": "Apple",
    "F4:F1:5A": "Apple",
    "F4:F9:51": "Apple",
    "F8:1E:DF": "Apple",
    "F8:27:93": "Apple",
    "F8:62:14": "Apple",
    "F8:95:C7": "Apple",
    "FC:25:3F": "Apple",
    "FC:E9:98": "Apple",
    # Samsung
    "00:07:AB": "Samsung",
    "00:12:47": "Samsung",
    "00:12:FB": "Samsung",
    "00:13:77": "Samsung",
    "00:15:B9": "Samsung",
    "00:16:32": "Samsung",
    "00:16:6B": "Samsung",
    "00:16:6C": "Samsung",
    "00:17:C9": "Samsung",
    "00:17:D5": "Samsung",
    "00:18:AF": "Samsung",
    "00:1A:8A": "Samsung",
    "00:1D:25": "Samsung",
    "00:1D:F6": "Samsung",
    "00:1E:7D": "Samsung",
    "00:1F:CC": "Samsung",
    "00:1F:CD": "Samsung",
    "00:21:19": "Samsung",
    "00:21:4C": "Samsung",
    "00:21:D1": "Samsung",
    "00:21:D2": "Samsung",
    "00:23:39": "Samsung",
    "00:23:3A": "Samsung",
    "00:23:99": "Samsung",
    "00:23:D6": "Samsung",
    "00:23:D7": "Samsung",
    "00:24:54": "Samsung",
    "00:24:90": "Samsung",
    "00:24:91": "Samsung",
    "00:24:E9": "Samsung",
    "00:25:66": "Samsung",
    "00:25:67": "Samsung",
    "00:26:37": "Samsung",
    "00:26:5D": "Samsung",
    "00:26:5F": "Samsung",
    # Google/Android
    "00:1A:11": "Google",
    "54:60:09": "Google",
    "94:EB:2C": "Google",
    "A4:77:33": "Google",
    "F4:F5:D8": "Google",
    "F4:F5:E8": "Google",
    # Amazon
    "00:FC:8B": "Amazon",
    "0C:47:C9": "Amazon",
    "10:CE:A9": "Amazon",
    "18:74:2E": "Amazon",
    "28:EF:01": "Amazon",
    "34:D2:70": "Amazon",
    "38:F7:3D": "Amazon",
    "40:B4:CD": "Amazon",
    "44:65:0D": "Amazon",
    "4C:EF:C0": "Amazon",
    "50:DC:E7": "Amazon",
    "50:F5:DA": "Amazon",
    "68:37:E9": "Amazon",
    "68:54:FD": "Amazon",
    "6C:56:97": "Amazon",
    "74:C2:46": "Amazon",
    "78:E1:03": "Amazon",
    "84:D6:D0": "Amazon",
    "88:71:B1": "Amazon",
    "A0:02:DC": "Amazon",
    "AC:63:BE": "Amazon",
    "B4:7C:9C": "Amazon",
    "B4:A8:28": "Amazon",
    "C8:3D:D4": "Amazon",
    "CC:9E:A2": "Amazon",
    "F0:27:2D": "Amazon",
    "F0:72:EA": "Amazon",
    "FC:65:DE": "Amazon",
    # Xiaomi
    "00:9E:C8": "Xiaomi",
    "04:CF:8C": "Xiaomi",
    "0C:1D:AF": "Xiaomi",
    "10:2A:B3": "Xiaomi",
    "14:F6:5A": "Xiaomi",
    "18:59:36": "Xiaomi",
    "20:34:FB": "Xiaomi",
    "28:6C:07": "Xiaomi",
    "28:E3:1F": "Xiaomi",
    "34:80:B3": "Xiaomi",
    "38:A4:ED": "Xiaomi",
    "3C:BD:D8": "Xiaomi",
    "44:23:7C": "Xiaomi",
    "50:64:2B": "Xiaomi",
    "58:44:98": "Xiaomi",
    "5C:AF:06": "Xiaomi",
    "64:09:80": "Xiaomi",
    "64:B4:73": "Xiaomi",
    "68:28:BA": "Xiaomi",
    "74:23:44": "Xiaomi",
    "74:51:BA": "Xiaomi",
    "78:02:F8": "Xiaomi",
    "78:11:DC": "Xiaomi",
    "7C:1D:D9": "Xiaomi",
    "84:F3:EB": "Xiaomi",
    "88:C3:97": "Xiaomi",
    "8C:BE:BE": "Xiaomi",
    "98:FA:E3": "Xiaomi",
    "9C:99:A0": "Xiaomi",
    "A4:D5:78": "Xiaomi",
    "AC:C1:EE": "Xiaomi",
    "B0:E2:35": "Xiaomi",
    "C4:0B:CB": "Xiaomi",
    "C4:6A:B7": "Xiaomi",
    "D4:97:0B": "Xiaomi",
    "E4:46:DA": "Xiaomi",
    "F0:B4:29": "Xiaomi",
    "F4:F5:DB": "Xiaomi",
    "F8:A4:5F": "Xiaomi",
    "FC:64:BA": "Xiaomi",
    # Huawei
    "00:18:82": "Huawei",
    "00:1E:10": "Huawei",
    "00:25:68": "Huawei",
    "00:25:9E": "Huawei",
    "00:46:4B": "Huawei",
    "00:66:4B": "Huawei",
    "00:E0:FC": "Huawei",
    "04:02:1F": "Huawei",
    "04:25:C5": "Huawei",
    "04:33:89": "Huawei",
    "04:4F:4C": "Huawei",
    "04:B0:E7": "Huawei",
    "04:C0:6F": "Huawei",
    "04:F9:38": "Huawei",
    "08:19:A6": "Huawei",
    "08:63:61": "Huawei",
    "08:7A:4C": "Huawei",
    "08:E8:4F": "Huawei",
    "0C:37:DC": "Huawei",
    "0C:45:BA": "Huawei",
    "0C:96:BF": "Huawei",
    # Intel
    "00:02:B3": "Intel",
    "00:03:47": "Intel",
    "00:04:23": "Intel",
    "00:07:E9": "Intel",
    "00:0C:F1": "Intel",
    "00:0E:0C": "Intel",
    "00:0E:35": "Intel",
    "00:11:11": "Intel",
    "00:12:F0": "Intel",
    "00:13:02": "Intel",
    "00:13:20": "Intel",
    "00:13:CE": "Intel",
    "00:13:E8": "Intel",
    "00:15:00": "Intel",
    "00:15:17": "Intel",
    "00:16:6F": "Intel",
    "00:16:76": "Intel",
    "00:16:EA": "Intel",
    "00:16:EB": "Intel",
    "00:18:DE": "Intel",
    "00:19:D1": "Intel",
    "00:19:D2": "Intel",
    "00:1B:21": "Intel",
    "00:1B:77": "Intel",
    "00:1C:BF": "Intel",
    "00:1C:C0": "Intel",
    "00:1D:E0": "Intel",
    "00:1D:E1": "Intel",
    "00:1E:64": "Intel",
    "00:1E:65": "Intel",
    "00:1E:67": "Intel",
    "00:1F:3B": "Intel",
    "00:1F:3C": "Intel",
    "00:20:E0": "Intel",
    "00:21:5C": "Intel",
    "00:21:5D": "Intel",
    "00:21:6A": "Intel",
    "00:21:6B": "Intel",
    "00:22:FA": "Intel",
    "00:22:FB": "Intel",
    "00:23:14": "Intel",
    "00:23:15": "Intel",
    "00:24:D6": "Intel",
    "00:24:D7": "Intel",
    "00:26:C6": "Intel",
    "00:26:C7": "Intel",
    "00:27:10": "Intel",
    # Raspberry Pi
    "B8:27:EB": "Raspberry Pi",
    "DC:A6:32": "Raspberry Pi",
    "E4:5F:01": "Raspberry Pi",
    "28:CD:C1": "Raspberry Pi",
    "D8:3A:DD": "Raspberry Pi",
    # TP-Link
    "00:27:19": "TP-Link",
    "14:CC:20": "TP-Link",
    "14:CF:92": "TP-Link",
    "18:A6:F7": "TP-Link",
    "1C:3B:F3": "TP-Link",
    "30:B5:C2": "TP-Link",
    "50:C7:BF": "TP-Link",
    "54:C8:0F": "TP-Link",
    "60:E3:27": "TP-Link",
    "64:70:02": "TP-Link",
    "6C:5A:B0": "TP-Link",
    "78:A1:06": "TP-Link",
    "90:F6:52": "TP-Link",
    "A0:F3:C1": "TP-Link",
    "AC:84:C6": "TP-Link",
    "B0:4E:26": "TP-Link",
    "B0:95:75": "TP-Link",
    "C0:25:E9": "TP-Link",
    "C4:E9:84": "TP-Link",
    "C8:3A:35": "TP-Link",
    "CC:34:29": "TP-Link",
    "D8:07:B6": "TP-Link",
    "E8:94:F6": "TP-Link",
    "EC:08:6B": "TP-Link",
    "EC:17:2F": "TP-Link",
    "F4:EC:38": "TP-Link",
    "F8:1A:67": "TP-Link",
    # ESP/IoT
    "18:FE:34": "Espressif",
    "24:0A:C4": "Espressif",
    "24:62:AB": "Espressif",
    "24:6F:28": "Espressif",
    "24:B2:DE": "Espressif",
    "2C:3A:E8": "Espressif",
    "30:AE:A4": "Espressif",
    "3C:61:05": "Espressif",
    "3C:71:BF": "Espressif",
    "40:F5:20": "Espressif",
    "4C:11:AE": "Espressif",
    "4C:75:25": "Espressif",
    "5C:CF:7F": "Espressif",
    "60:01:94": "Espressif",
    "68:C6:3A": "Espressif",
    "7C:9E:BD": "Espressif",
    "80:7D:3A": "Espressif",
    "84:0D:8E": "Espressif",
    "84:CC:A8": "Espressif",
    "84:F3:EB": "Espressif",
    "8C:AA:B5": "Espressif",
    "90:97:D5": "Espressif",
    "98:CD:AC": "Espressif",
    "98:F4:AB": "Espressif",
    "A0:20:A6": "Espressif",
    "A4:7B:9D": "Espressif",
    "A4:CF:12": "Espressif",
    "AC:D0:74": "Espressif",
    "B4:E6:2D": "Espressif",
    "BC:DD:C2": "Espressif",
    "C4:4F:33": "Espressif",
    "C8:2B:96": "Espressif",
    "CC:50:E3": "Espressif",
    "D8:A0:1D": "Espressif",
    "D8:BF:C0": "Espressif",
    "DC:4F:22": "Espressif",
    "EC:FA:BC": "Espressif",
    "F0:08:D1": "Espressif",
    # LG
    "00:1C:62": "LG",
    "00:1E:75": "LG",
    "00:1F:6B": "LG",
    "00:1F:E3": "LG",
    "00:22:A9": "LG",
    "00:24:83": "LG",
    "00:25:E5": "LG",
    "00:26:E2": "LG",
    "00:34:DA": "LG",
    "00:AA:70": "LG",
    "04:D6:AA": "LG",
    "08:D4:6A": "LG",
    "10:68:3F": "LG",
    "10:F9:6F": "LG",
    "14:C9:13": "LG",
    "18:67:B0": "LG",
    "1C:BC:4B": "LG",
    "1C:CF:26": "LG",
    "20:21:A5": "LG",
    "20:3D:BD": "LG",
    "28:3F:69": "LG",
    "2C:54:CF": "LG",
    "30:19:66": "LG",
    "30:8C:FB": "LG",
    "34:4D:F7": "LG",
    "38:8C:50": "LG",
    "3C:BD:D8": "LG",
    "40:B8:9A": "LG",
    "44:07:4F": "LG",
    # Sony
    "00:01:4A": "Sony",
    "00:04:1F": "Sony",
    "00:0A:D9": "Sony",
    "00:0B:6A": "Sony",
    "00:0E:07": "Sony",
    "00:0F:DE": "Sony",
    "00:12:EE": "Sony",
    "00:13:A9": "Sony",
    "00:15:C1": "Sony",
    "00:16:20": "Sony",
    "00:18:13": "Sony",
    "00:19:63": "Sony",
    "00:19:C5": "Sony",
    "00:1A:75": "Sony",
    "00:1A:80": "Sony",
    "00:1C:A4": "Sony",
    "00:1D:28": "Sony",
    "00:1D:BA": "Sony",
    "00:1E:A4": "Sony",
    "00:1F:E4": "Sony",
    "00:21:9E": "Sony",
    "00:23:45": "Sony",
    "00:24:8D": "Sony",
    "00:24:BE": "Sony",
    "28:0D:FC": "Sony",
    # Vodafone (routers)
    "00:09:DF": "Vodafone",
    "00:0F:3D": "Vodafone",
    "00:13:4E": "Vodafone",
    "00:14:7B": "Vodafone",
    "00:1E:2A": "Vodafone",
    "00:22:3F": "Vodafone",
    "00:24:D4": "Vodafone",
    "08:95:2A": "Vodafone",
    "18:62:2C": "Vodafone",
    "1C:B0:44": "Vodafone",
    "38:43:7D": "Vodafone",
    "58:23:8C": "Vodafone",
    "70:F3:95": "Vodafone",
    "84:26:15": "Vodafone",
    "88:71:B1": "Vodafone",
    "D0:05:2A": "Vodafone",
    "E8:DF:70": "Vodafone",
    # Realtek
    "00:E0:4C": "Realtek",
    "52:54:00": "Realtek/QEMU",
    # Microsoft
    "00:03:FF": "Microsoft",
    "00:0D:3A": "Microsoft",
    "00:12:5A": "Microsoft",
    "00:15:5D": "Microsoft",
    "00:17:FA": "Microsoft",
    "00:1D:D8": "Microsoft",
    "00:22:48": "Microsoft",
    "00:25:AE": "Microsoft",
    "00:50:F2": "Microsoft",
    "28:18:78": "Microsoft",
    "30:59:B7": "Microsoft",
    "50:1A:C5": "Microsoft",
    "58:82:A8": "Microsoft",
    "60:45:BD": "Microsoft",
    "7C:1E:52": "Microsoft",
    "7C:ED:8D": "Microsoft",
    "98:5F:D3": "Microsoft",
    "B4:AE:2B": "Microsoft",
    "C8:3F:26": "Microsoft",
    "DC:B4:C4": "Microsoft",
    # LG Electronics
    "60:45:E8": "LG Electronics",
    "00:1C:62": "LG Electronics",
    "00:1E:75": "LG Electronics",
    "00:1F:6B": "LG Electronics",
    "00:1F:E2": "LG Electronics",
    "00:22:A9": "LG Electronics",
    "00:24:83": "LG Electronics",
    "00:25:E5": "LG Electronics",
    "00:26:E2": "LG Electronics",
    "00:34:DA": "LG Electronics",
    "00:AA:70": "LG Electronics",
    "10:68:3F": "LG Electronics",
    "14:C9:13": "LG Electronics",
    "2C:54:CF": "LG Electronics",
    "30:8C:FB": "LG Electronics",
    "34:4D:F7": "LG Electronics",
    "38:8C:50": "LG Electronics",
    "58:A2:B5": "LG Electronics",
    "64:99:5D": "LG Electronics",
    "78:5D:C8": "LG Electronics",
    "88:C9:D0": "LG Electronics",
    "A8:16:B2": "LG Electronics",
    "A8:23:FE": "LG Electronics",
    "B4:E6:2A": "LG Electronics",
    "C4:36:6C": "LG Electronics",
    "CC:2D:8C": "LG Electronics",
    "E8:5B:5B": "LG Electronics",
    "F8:0C:F3": "LG Electronics",
    "FC:F1:52": "LG Electronics",
    # TP-Link
    "E4:FA:C4": "TP-Link",
    "84:D8:1B": "TP-Link",
    "00:1D:0F": "TP-Link",
    "00:23:CD": "TP-Link",
    "00:27:19": "TP-Link",
    "14:CC:20": "TP-Link",
    "14:CF:92": "TP-Link",
    "18:A6:F7": "TP-Link",
    "1C:3B:F3": "TP-Link",
    "30:B5:C2": "TP-Link",
    "50:3E:AA": "TP-Link",
    "50:C7:BF": "TP-Link",
    "54:C8:0F": "TP-Link",
    "5C:63:BF": "TP-Link",
    "60:E3:27": "TP-Link",
    "64:56:01": "TP-Link",
    "64:70:02": "TP-Link",
    "6C:5A:B0": "TP-Link",
    "78:44:76": "TP-Link",
    "90:F6:52": "TP-Link",
    "98:DA:C4": "TP-Link",
    "A4:2B:B0": "TP-Link",
    "A8:57:4E": "TP-Link",
    "AC:84:C6": "TP-Link",
    "B0:4E:26": "TP-Link",
    "B0:95:75": "TP-Link",
    "BC:46:99": "TP-Link",
    "C0:25:E9": "TP-Link",
    "C4:E9:84": "TP-Link",
    "CC:34:29": "TP-Link",
    "D4:6E:0E": "TP-Link",
    "D8:07:B6": "TP-Link",
    "D8:47:32": "TP-Link",
    "E4:D3:32": "TP-Link",
    "EC:08:6B": "TP-Link",
    "EC:17:2F": "TP-Link",
    "F4:F2:6D": "TP-Link",
    "F8:1A:67": "TP-Link",
    "F8:D1:11": "TP-Link",
    # Intel
    "BC:03:58": "Intel Corporate",
    "00:02:B3": "Intel Corporate",
    "00:03:47": "Intel Corporate",
    "00:04:23": "Intel Corporate",
    "00:07:E9": "Intel Corporate",
    "00:0E:0C": "Intel Corporate",
    "00:0E:35": "Intel Corporate",
    "00:11:11": "Intel Corporate",
    "00:12:F0": "Intel Corporate",
    "00:13:02": "Intel Corporate",
    "00:13:20": "Intel Corporate",
    "00:13:CE": "Intel Corporate",
    "00:13:E8": "Intel Corporate",
    "00:15:00": "Intel Corporate",
    "00:15:17": "Intel Corporate",
    "00:16:6F": "Intel Corporate",
    "00:16:76": "Intel Corporate",
    "00:16:EA": "Intel Corporate",
    "00:16:EB": "Intel Corporate",
    "00:18:DE": "Intel Corporate",
    "00:19:D1": "Intel Corporate",
    "00:1B:21": "Intel Corporate",
    "00:1B:77": "Intel Corporate",
    "00:1C:BF": "Intel Corporate",
    "00:1D:E0": "Intel Corporate",
    "00:1E:64": "Intel Corporate",
    "00:1E:65": "Intel Corporate",
    "00:1F:3B": "Intel Corporate",
    "00:1F:3C": "Intel Corporate",
    "00:20:E0": "Intel Corporate",
    "00:21:5C": "Intel Corporate",
    "00:21:5D": "Intel Corporate",
    "00:21:6A": "Intel Corporate",
    "00:21:6B": "Intel Corporate",
    "00:22:FA": "Intel Corporate",
    "00:22:FB": "Intel Corporate",
    "00:23:14": "Intel Corporate",
    "00:23:15": "Intel Corporate",
    "00:24:D6": "Intel Corporate",
    "00:24:D7": "Intel Corporate",
    "00:26:C6": "Intel Corporate",
    "00:26:C7": "Intel Corporate",
    "00:27:10": "Intel Corporate",
    "24:77:03": "Intel Corporate",
    "3C:A9:F4": "Intel Corporate",
    "48:51:B7": "Intel Corporate",
    "50:76:AF": "Intel Corporate",
    "58:91:CF": "Intel Corporate",
    "5C:51:4F": "Intel Corporate",
    "64:80:99": "Intel Corporate",
    "68:05:CA": "Intel Corporate",
    "6C:88:14": "Intel Corporate",
    "78:92:9C": "Intel Corporate",
    "7C:5C:F8": "Intel Corporate",
    "84:3A:4B": "Intel Corporate",
    "88:53:2E": "Intel Corporate",
    "8C:F5:A3": "Intel Corporate",
    "98:4F:EE": "Intel Corporate",
    "9C:4E:36": "Intel Corporate",
    "A0:36:9F": "Intel Corporate",
    "A4:4E:31": "Intel Corporate",
    "A4:C4:94": "Intel Corporate",
    "AC:7B:A1": "Intel Corporate",
    "B4:6B:FC": "Intel Corporate",
    "B8:03:05": "Intel Corporate",
    "C8:0A:A9": "Intel Corporate",
    "D4:3D:7E": "Intel Corporate",
    "D8:FC:93": "Intel Corporate",
    "E0:94:67": "Intel Corporate",
    "E8:B1:FC": "Intel Corporate",
    "F4:8C:50": "Intel Corporate",
    "F8:16:54": "Intel Corporate",
    "FC:F8:AE": "Intel Corporate",
    # Amazon
    "18:48:BE": "Amazon Technologies",
    "00:DC:B2": "Amazon Technologies",
    "0C:47:C9": "Amazon Technologies",
    "10:CE:A9": "Amazon Technologies",
    "14:91:82": "Amazon Technologies",
    "18:74:2E": "Amazon Technologies",
    "1C:12:B0": "Amazon Technologies",
    "24:4C:E3": "Amazon Technologies",
    "28:EF:01": "Amazon Technologies",
    "34:D2:70": "Amazon Technologies",
    "38:F7:3D": "Amazon Technologies",
    "40:A2:DB": "Amazon Technologies",
    "44:00:49": "Amazon Technologies",
    "44:65:0D": "Amazon Technologies",
    "50:DC:E7": "Amazon Technologies",
    "5C:41:5A": "Amazon Technologies",
    "68:37:E9": "Amazon Technologies",
    "68:54:FD": "Amazon Technologies",
    "6C:56:97": "Amazon Technologies",
    "74:75:48": "Amazon Technologies",
    "74:C2:46": "Amazon Technologies",
    "78:E1:03": "Amazon Technologies",
    "84:D6:D0": "Amazon Technologies",
    "8C:09:04": "Amazon Technologies",
    "90:CD:B6": "Amazon Technologies",
    "A0:02:DC": "Amazon Technologies",
    "AC:63:BE": "Amazon Technologies",
    "B0:FC:0D": "Amazon Technologies",
    "B4:7C:9C": "Amazon Technologies",
    "C8:A2:CE": "Amazon Technologies",
    "CC:F7:35": "Amazon Technologies",
    "F0:27:2D": "Amazon Technologies",
    "F0:F0:A4": "Amazon Technologies",
    "FC:65:DE": "Amazon Technologies",
    "FE:01:5D": "Amazon Technologies",
    # Sercomm / Routers
    "7C:13:1D": "Sercomm",
    "00:0E:38": "Sercomm",
    "00:1A:2A": "Sercomm",
    "00:1D:CE": "Sercomm",
    "00:1E:E5": "Sercomm",
    "00:22:6B": "Sercomm",
    "00:26:5B": "Sercomm",
    "08:76:FF": "Sercomm",
    "20:4E:7F": "Sercomm",
    "34:68:95": "Sercomm",
    "44:E9:DD": "Sercomm",
    "54:67:51": "Sercomm",
    "5C:A3:9D": "Sercomm",
    "6C:B0:CE": "Sercomm",
    "74:88:2A": "Sercomm",
    "78:96:82": "Sercomm",
    "80:20:DA": "Sercomm",
    "84:A4:23": "Sercomm",
    "88:71:B1": "Sercomm",
    "90:4E:2B": "Sercomm",
    "94:CC:B9": "Sercomm",
    "A0:04:60": "Sercomm",
    "A4:2B:8C": "Sercomm",
    "A4:91:B1": "Sercomm",
    "B4:A5:EF": "Sercomm",
    "C8:6C:87": "Sercomm",
    "D4:21:22": "Sercomm",
    "E8:65:D4": "Sercomm",
    "F0:84:2F": "Sercomm",
    "F4:28:53": "Sercomm",
    "FC:94:E3": "Sercomm",
    # Espressif (ESP32/ESP8266)
    "08:65:F0": "Espressif",
    "24:0A:C4": "Espressif",
    "24:6F:28": "Espressif",
    "24:B2:DE": "Espressif",
    "2C:3A:E8": "Espressif",
    "30:83:98": "Espressif",
    "30:AE:A4": "Espressif",
    "3C:61:05": "Espressif",
    "3C:71:BF": "Espressif",
    "48:3F:DA": "Espressif",
    "4C:11:AE": "Espressif",
    "4C:75:25": "Espressif",
    "5C:CF:7F": "Espressif",
    "60:01:94": "Espressif",
    "68:C6:3A": "Espressif",
    "7C:9E:BD": "Espressif",
    "80:7D:3A": "Espressif",
    "84:0D:8E": "Espressif",
    "84:CC:A8": "Espressif",
    "84:F3:EB": "Espressif",
    "8C:AA:B5": "Espressif",
    "90:97:D5": "Espressif",
    "98:CD:AC": "Espressif",
    "A0:20:A6": "Espressif",
    "A4:7B:9D": "Espressif",
    "A4:CF:12": "Espressif",
    "AC:67:B2": "Espressif",
    "B4:E6:2D": "Espressif",
    "BC:DD:C2": "Espressif",
    "C4:4F:33": "Espressif",
    "C8:2B:96": "Espressif",
    "CC:50:E3": "Espressif",
    "D8:A0:1D": "Espressif",
    "D8:BF:C0": "Espressif",
    "DC:4F:22": "Espressif",
    "E0:98:06": "Espressif",
    "E8:DB:84": "Espressif",
    "EC:FA:BC": "Espressif",
    "F0:08:D1": "Espressif",
    "F4:CF:A2": "Espressif",
}


# Patrones de hostname conocidos -> tipo de dispositivo
HOSTNAME_PATTERNS = {
    # Apple
    r'(?i)^iphone': ('iPhone', 'iOS'),
    r'(?i)^ipad': ('iPad', 'iOS'),
    r'(?i)^macbook': ('MacBook', 'macOS'),
    r'(?i)^imac': ('iMac', 'macOS'),
    r'(?i)^mac-?mini': ('Mac Mini', 'macOS'),
    r'(?i)^mac-?pro': ('Mac Pro', 'macOS'),
    r'(?i)^apple-?tv': ('Apple TV', 'tvOS'),
    r'(?i)^homepod': ('HomePod', 'SmartSpeaker'),
    r'(?i)^airpods': ('AirPods', 'Audio'),
    r'(?i)^watch': ('Apple Watch', 'watchOS'),
    r'(?i)-core$': ('Apple Device', 'Apple'),  # judariva-core pattern
    # Android
    r'(?i)^android-?[a-f0-9]+': ('Android', 'Android'),
    r'(?i)^galaxy': ('Samsung Galaxy', 'Android'),
    r'(?i)^sm-[a-z]': ('Samsung', 'Android'),
    r'(?i)^pixel': ('Google Pixel', 'Android'),
    r'(?i)^oneplus': ('OnePlus', 'Android'),
    r'(?i)^xiaomi|^redmi|^poco': ('Xiaomi', 'Android'),
    r'(?i)^huawei|^honor': ('Huawei', 'Android'),
    r'(?i)^oppo|^realme': ('Oppo', 'Android'),
    # Windows
    r'(?i)^desktop-[a-z0-9]+': ('Windows PC', 'Windows'),
    r'(?i)^laptop-[a-z0-9]+': ('Windows Laptop', 'Windows'),
    r'(?i)^win-?[a-z0-9]+': ('Windows PC', 'Windows'),
    r'(?i)^pc-?[a-z0-9]+': ('Windows PC', 'Windows'),
    r'(?i)^surface': ('Surface', 'Windows'),
    # Linux
    r'(?i)^raspberry': ('Raspberry Pi', 'Linux'),
    r'(?i)^pi-?hole': ('Pi-hole', 'Linux'),
    r'(?i)^ubuntu|^debian|^fedora|^arch': ('Linux PC', 'Linux'),
    # Smart TV / Media
    r'(?i)^lgwebostv|^lg-?tv': ('LG TV', 'SmartTV'),
    r'(?i)^\[lg\]|^lgtv': ('LG TV', 'SmartTV'),
    r'(?i)^samsung-?tv|^tizen': ('Samsung TV', 'SmartTV'),
    r'(?i)^sony-?tv|^bravia': ('Sony TV', 'SmartTV'),
    r'(?i)^roku': ('Roku', 'SmartTV'),
    r'(?i)^chromecast|^google-?cast': ('Chromecast', 'SmartTV'),
    r'(?i)^fire-?tv|^amazon-?fire': ('Fire TV', 'SmartTV'),
    r'(?i)^shield': ('Nvidia Shield', 'SmartTV'),
    # Gaming
    r'(?i)^playstation|^ps[345]': ('PlayStation', 'Gaming'),
    r'(?i)^xbox': ('Xbox', 'Gaming'),
    r'(?i)^nintendo|^switch': ('Nintendo Switch', 'Gaming'),
    # IoT / Smart Home
    r'(?i)^esp-?[0-9a-f]+|^esp32|^esp8266': ('ESP Device', 'IoT'),
    r'(?i)^tasmota': ('Tasmota Device', 'IoT'),
    r'(?i)^shelly': ('Shelly', 'IoT'),
    r'(?i)^sonoff': ('Sonoff', 'IoT'),
    r'(?i)^tuya|^smart-?life': ('Tuya Device', 'IoT'),
    r'(?i)^hue-?bridge|^philips-?hue': ('Philips Hue', 'IoT'),
    r'(?i)^nest': ('Nest', 'IoT'),
    r'(?i)^ring': ('Ring', 'Camera'),
    r'(?i)^ecobee|^tado': ('Thermostat', 'IoT'),
    r'(?i)^tp-?link|^kasa': ('TP-Link Smart', 'IoT'),
    r'(?i)^p100|^p110|^hs100|^hs110|^hs200': ('TP-Link Plug', 'IoT'),
    # Voice assistants
    r'(?i)^echo|^amazon-?echo': ('Amazon Echo', 'SmartSpeaker'),
    r'(?i)^alexa': ('Alexa Device', 'SmartSpeaker'),
    r'(?i)^google-?home|^nest-?mini|^nest-?hub': ('Google Home', 'SmartSpeaker'),
    # Network
    r'(?i)^router|^gateway': ('Router', 'Network'),
    r'(?i)^vodafone|^sercomm': ('Vodafone Router', 'Network'),
    r'(?i)^unifi|^ubnt': ('UniFi', 'Network'),
    r'(?i)^ap-?[0-9]+|^access-?point': ('Access Point', 'Network'),
    # Printers
    r'(?i)^hp-?|^hpprinter|^officejet|^laserjet|^deskjet': ('HP Printer', 'Printer'),
    r'(?i)^epson|^et-?[0-9]+|^xp-?[0-9]+': ('Epson Printer', 'Printer'),
    r'(?i)^canon|^pixma': ('Canon Printer', 'Printer'),
    r'(?i)^brother': ('Brother Printer', 'Printer'),
}

# Puertos -> tipo de dispositivo
PORT_FINGERPRINTS = {
    22: [('SSH', 'Linux/Server')],
    62078: [('iPhone Sync', 'iOS')],
    5353: [('mDNS', None)],  # Many devices
    8008: [('Chromecast', 'SmartTV')],
    8009: [('Chromecast', 'SmartTV')],
    8443: [('Plex/HTTPS', 'MediaServer')],
    32400: [('Plex', 'MediaServer')],
    9100: [('Printer', 'Printer')],
    515: [('LPD Printer', 'Printer')],
    631: [('CUPS/IPP', 'Printer')],
    3389: [('RDP', 'Windows')],
    445: [('SMB', 'Windows/NAS')],
    139: [('NetBIOS', 'Windows')],
    548: [('AFP', 'macOS')],
    3283: [('Apple Remote', 'macOS')],
    5000: [('Synology', 'NAS')],
    5001: [('Synology SSL', 'NAS')],
    80: [('HTTP', None)],
    443: [('HTTPS', None)],
    1883: [('MQTT', 'IoT')],
    8883: [('MQTT SSL', 'IoT')],
    1900: [('UPnP/SSDP', None)],
    7000: [('AirPlay', 'Apple')],
    7100: [('AirPlay', 'Apple')],
    5060: [('SIP', 'VoIP')],
    554: [('RTSP', 'Camera')],
    8080: [('HTTP Alt', None)],
    9000: [('PHP-FPM/Portainer', 'Server')],
}

# Fabricantes -> tipo probable
VENDOR_DEVICE_HINTS = {
    'Apple': 'Apple',
    'Samsung': 'Android',
    'Xiaomi': 'Android',
    'Huawei': 'Android',
    'OnePlus': 'Android',
    'Google': 'Android',
    'LG Electronics': 'SmartTV',
    'Sony': 'SmartTV',
    'Roku': 'SmartTV',
    'Amazon': 'SmartSpeaker',
    'Sonos': 'SmartSpeaker',
    'TP-Link': 'IoT',
    'Shelly': 'IoT',
    'Espressif': 'IoT',
    'Tuya': 'IoT',
    'Philips': 'IoT',
    'Belkin': 'IoT',
    'HP': 'Printer',
    'Epson': 'Printer',
    'Canon': 'Printer',
    'Brother': 'Printer',
    'Synology': 'NAS',
    'QNAP': 'NAS',
    'Western Digital': 'NAS',
    'Cisco': 'Network',
    'Netgear': 'Network',
    'Ubiquiti': 'Network',
    'Asus': 'Network',
    'Hikvision': 'Camera',
    'Dahua': 'Camera',
    'Reolink': 'Camera',
    'Ring': 'Camera',
    'Nest': 'IoT',
    'Raspberry': 'Linux',
    'Intel': 'PC',
    'Dell': 'PC',
    'Lenovo': 'PC',
    'HP Inc': 'PC',
    'Hewlett': 'PC',
    'Acer': 'PC',
    'Microsoft': 'Windows',
    'VMware': 'VM',
    'VirtualBox': 'VM',
    'Sernet': 'Router',
    'Sercomm': 'Router',
    'Vodafone': 'Router',
    'Technicolor': 'Router',
    'Arcadyan': 'Router',
    'ZTE': 'Router',
    'Sagemcom': 'Router',
}


@dataclass
class NetworkDevice:
    """Dispositivo de red con información completa."""
    mac: str
    ip: str
    hostname: str = ""
    vendor: str = ""
    os_guess: str = ""
    open_ports: List[int] = field(default_factory=list)
    last_seen: datetime = field(default_factory=datetime.now)
    first_seen: datetime = field(default_factory=datetime.now)
    times_seen: int = 1
    source: str = ""
    is_online: bool = True
    mdns_name: str = ""        # Nombre mDNS/Bonjour
    mdns_services: List[str] = field(default_factory=list)  # Servicios anunciados
    ssdp_info: str = ""        # Info SSDP/UPnP
    detected_type: str = ""    # Tipo detectado manualmente

    def __post_init__(self):
        self.mac = self._format_mac(self.mac)
        if not self.vendor:
            self.vendor = self._lookup_vendor(self.mac)

    @staticmethod
    def _format_mac(mac: str) -> str:
        """Normaliza formato MAC."""
        if not mac:
            return ""
        clean = mac.upper().replace(':', '').replace('-', '').replace('.', '')
        if len(clean) != 12:
            return mac.upper()
        return ':'.join(clean[i:i+2] for i in range(0, 12, 2))

    @staticmethod
    def _lookup_vendor(mac: str) -> str:
        """Busca fabricante en base de datos OUI."""
        if not mac or len(mac) < 8:
            return ""
        prefix = mac[:8].upper()
        return OUI_DATABASE.get(prefix, "")

    @property
    def display_name(self) -> str:
        """Nombre para mostrar (prioridad: mdns > hostname > vendor)."""
        # mDNS suele tener nombres más descriptivos
        if self.mdns_name and self.mdns_name not in ('*', '?'):
            return self.mdns_name.replace('.local', '')
        if self.hostname and self.hostname not in ('*', '?', 'unknown', self.ip):
            return self.hostname
        if self.vendor:
            return self.vendor
        return self.ip

    def _detect_from_hostname(self) -> Tuple[Optional[str], Optional[str]]:
        """Detecta tipo desde hostname con patrones."""
        hostname = self.hostname or self.mdns_name or ""
        for pattern, (name, dev_type) in HOSTNAME_PATTERNS.items():
            if re.match(pattern, hostname):
                return name, dev_type
        return None, None

    def _detect_from_ports(self) -> Optional[str]:
        """Detecta tipo desde puertos abiertos."""
        if not self.open_ports:
            return None

        # Priorizar puertos más específicos
        priority_ports = [62078, 9100, 515, 631, 32400, 8008, 8009, 548, 3283, 554]
        for port in priority_ports:
            if port in self.open_ports:
                for name, dev_type in PORT_FINGERPRINTS.get(port, []):
                    if dev_type:
                        return dev_type
        return None

    def _detect_from_mdns(self) -> Optional[str]:
        """Detecta tipo desde servicios mDNS."""
        services = ' '.join(self.mdns_services).lower()

        if '_airplay' in services or '_raop' in services:
            return 'Apple'
        if '_googlecast' in services:
            return 'SmartTV'
        if '_ipp' in services or '_printer' in services:
            return 'Printer'
        if '_homekit' in services:
            return 'IoT'
        if '_spotify' in services:
            return 'SmartSpeaker'
        if '_hap' in services:  # HomeKit Accessory Protocol
            return 'IoT'
        if '_smb' in services or '_afpovertcp' in services:
            return 'NAS'
        return None

    def _detect_from_vendor(self) -> Optional[str]:
        """Detecta tipo desde vendor."""
        if not self.vendor:
            return None
        vendor_lower = self.vendor.lower()
        for vendor_key, hint in VENDOR_DEVICE_HINTS.items():
            if vendor_key.lower() in vendor_lower:
                return hint
        return None

    @property
    def device_type(self) -> str:
        """Tipo de dispositivo inferido con múltiples fuentes."""
        # Si está manualmente detectado, usar ese
        if self.detected_type:
            return self.detected_type

        # 1. Hostname patterns (más fiable)
        name, dtype = self._detect_from_hostname()
        if dtype:
            return dtype

        # 2. mDNS services
        mdns_type = self._detect_from_mdns()
        if mdns_type:
            return mdns_type

        # 3. Puertos específicos
        port_type = self._detect_from_ports()
        if port_type:
            return port_type

        # 4. SSDP info
        if self.ssdp_info:
            ssdp = self.ssdp_info.lower()
            if 'tv' in ssdp or 'mediarenderer' in ssdp:
                return 'SmartTV'
            if 'printer' in ssdp:
                return 'Printer'
            if 'nas' in ssdp or 'storage' in ssdp:
                return 'NAS'

        # 5. Vendor hints
        vendor_type = self._detect_from_vendor()
        if vendor_type:
            return vendor_type

        # 6. Fallback: análisis de texto
        text = f"{self.vendor} {self.hostname} {self.os_guess} {self.mdns_name}".lower()

        if any(x in text for x in ['iphone', 'ipad']):
            return "iOS"
        if 'apple' in text and 'tv' not in text:
            return "Apple"
        if any(x in text for x in ['android', 'samsung', 'xiaomi', 'huawei', 'galaxy', 'pixel']):
            return "Android"
        if any(x in text for x in ['windows', 'microsoft', 'desktop-', 'laptop-']):
            return "Windows"
        if any(x in text for x in ['linux', 'ubuntu', 'debian', 'raspberry', 'pi']):
            return "Linux"
        if any(x in text for x in ['tv', 'roku', 'chromecast', 'fire', 'shield', 'webos', 'tizen']):
            return "SmartTV"
        if any(x in text for x in ['alexa', 'echo', 'homepod', 'google home', 'nest mini', 'sonos']):
            return "SmartSpeaker"
        if any(x in text for x in ['esp', 'tasmota', 'tuya', 'shelly', 'sonoff', 'smart']):
            return "IoT"
        if any(x in text for x in ['router', 'gateway', 'vodafone', 'modem']):
            return "Router"
        if any(x in text for x in ['printer', 'print', 'hp ', 'epson', 'canon', 'brother']):
            return "Printer"
        if any(x in text for x in ['camera', 'cam', 'ring', 'nest cam', 'hikvision', 'reolink']):
            return "Camera"
        if any(x in text for x in ['playstation', 'ps4', 'ps5', 'xbox', 'nintendo', 'switch']):
            return "Gaming"
        if any(x in text for x in ['synology', 'qnap', 'nas', 'diskstation']):
            return "NAS"

        return "Unknown"

    @property
    def device_name(self) -> str:
        """Nombre específico del dispositivo si se conoce."""
        name, _ = self._detect_from_hostname()
        if name:
            return name
        return self.device_type

    @property
    def icon(self) -> str:
        """Emoji según tipo."""
        icons = {
            "iOS": "📱",
            "iPhone": "📱",
            "iPad": "📱",
            "Apple": "🍎",
            "macOS": "💻",
            "tvOS": "📺",
            "watchOS": "⌚",
            "Android": "🤖",
            "Windows": "🪟",
            "Linux": "🐧",
            "SmartTV": "📺",
            "SmartSpeaker": "🔊",
            "IoT": "🏠",
            "Router": "📡",
            "Network": "📡",
            "Printer": "🖨️",
            "Camera": "📷",
            "Gaming": "🎮",
            "NAS": "💾",
            "MediaServer": "🎬",
            "Server": "🖥️",
            "PC": "🖥️",
            "VM": "☁️",
            "VoIP": "📞",
            "Audio": "🎧",
            "Unknown": "📶"
        }
        return icons.get(self.device_type, "📶")


class NetworkService:
    """Servicio avanzado de red."""

    def __init__(self):
        self._cache: Dict[str, NetworkDevice] = {}
        self._last_scan: Optional[datetime] = None
        self._history_file = Path(config.DATA_DIR) / "network_history.json"
        self._load_history()

    def _load_history(self):
        """Carga historial de dispositivos."""
        if not self._history_file.exists():
            return

        try:
            with open(self._history_file) as f:
                data = json.load(f)
            for mac, info in data.items():
                self._cache[mac] = NetworkDevice(
                    mac=mac,
                    ip=info.get('ip', ''),
                    hostname=info.get('hostname', ''),
                    vendor=info.get('vendor', ''),
                    os_guess=info.get('os_guess', ''),
                    open_ports=info.get('open_ports', []),
                    first_seen=datetime.fromisoformat(info['first_seen']) if 'first_seen' in info else datetime.now(),
                    last_seen=datetime.fromisoformat(info['last_seen']) if 'last_seen' in info else datetime.now(),
                    times_seen=info.get('times_seen', 1),
                    is_online=False
                )
        except Exception as e:
            logger.error(f"Error cargando historial: {e}")

    def _save_history(self):
        """Guarda historial de dispositivos."""
        try:
            config.ensure_data_dir()
            data = {}
            for mac, device in self._cache.items():
                data[mac] = {
                    'ip': device.ip,
                    'hostname': device.hostname,
                    'vendor': device.vendor,
                    'os_guess': device.os_guess,
                    'open_ports': device.open_ports,
                    'first_seen': device.first_seen.isoformat(),
                    'last_seen': device.last_seen.isoformat(),
                    'times_seen': device.times_seen,
                }
            with open(self._history_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error guardando historial: {e}")

    async def scan_all(self, deep: bool = False, use_cache: bool = False) -> List[NetworkDevice]:
        """
        Escaneo completo de red.

        Args:
            deep: Si True, hace escaneo nmap (más lento pero más info)
            use_cache: Si True, devuelve cache si fue escaneado hace menos de 30s
        """
        # Si use_cache y el cache es reciente, devolver cache
        if use_cache and self._last_scan:
            age = (datetime.now() - self._last_scan).total_seconds()
            if age < 30:
                online = [d for d in self._cache.values() if d.is_online]
                return sorted(online, key=lambda d: self._ip_sort_key(d.ip))

        # Marcar todos como offline
        for device in self._cache.values():
            device.is_online = False

        # Escaneos en paralelo (básicos + discovery)
        tasks = [
            self._scan_arp(),
            self._scan_dhcp_leases(),
            self._scan_pihole_network(),
            self._scan_mdns(),      # Descubrimiento mDNS/Bonjour
            self._scan_ssdp(),      # Descubrimiento UPnP/SSDP
        ]

        if deep:
            tasks.append(self._scan_nmap())

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Combinar resultados
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Error en scan: {result}")
                continue
            for device in result:
                self._merge_device(device)

        self._last_scan = datetime.now()
        self._save_history()

        # Devolver solo los online, ordenados
        online = [d for d in self._cache.values() if d.is_online]
        return sorted(online, key=lambda d: self._ip_sort_key(d.ip))

    def _merge_device(self, new: NetworkDevice):
        """Merge información de dispositivo."""
        mac = new.mac
        if mac in self._cache:
            existing = self._cache[mac]
            existing.ip = new.ip or existing.ip
            existing.hostname = new.hostname or existing.hostname
            existing.vendor = new.vendor or existing.vendor
            existing.os_guess = new.os_guess or existing.os_guess
            # Nuevos campos de discovery
            existing.mdns_name = new.mdns_name or existing.mdns_name
            existing.ssdp_info = new.ssdp_info or existing.ssdp_info
            if new.mdns_services:
                existing.mdns_services = list(set(existing.mdns_services + new.mdns_services))
            if new.open_ports:
                existing.open_ports = list(set(existing.open_ports + new.open_ports))
            existing.last_seen = datetime.now()
            existing.times_seen += 1
            existing.is_online = True
        else:
            new.is_online = True
            new.first_seen = datetime.now()
            self._cache[mac] = new

    async def _scan_arp(self) -> List[NetworkDevice]:
        """Escaneo ARP rápido."""
        devices = []
        stdout, stderr, code = await run_async(
            "sudo arp-scan -l -q --retry=2 2>/dev/null",
            timeout=30
        )

        if code != 0:
            logger.warning(f"arp-scan falló: {stderr}")
            return devices

        for line in stdout.split('\n'):
            if not line or not re.match(r'^\d+\.', line):
                continue
            parts = line.split('\t')
            if len(parts) >= 2:
                devices.append(NetworkDevice(
                    ip=parts[0].strip(),
                    mac=parts[1].strip(),
                    vendor=parts[2].strip() if len(parts) > 2 else "",
                    source="arp"
                ))

        return devices

    async def _scan_dhcp_leases(self) -> List[NetworkDevice]:
        """Lee leases DHCP de Pi-hole."""
        devices = []
        stdout, _, code = await run_async(
            "docker exec pihole cat /etc/pihole/dhcp.leases 2>/dev/null",
            timeout=10
        )

        if code != 0 or not stdout:
            return devices

        for line in stdout.split('\n'):
            parts = line.split()
            if len(parts) >= 4:
                hostname = parts[3] if parts[3] != '*' else ""
                devices.append(NetworkDevice(
                    mac=parts[1],
                    ip=parts[2],
                    hostname=hostname,
                    source="dhcp"
                ))

        return devices

    async def _scan_pihole_network(self) -> List[NetworkDevice]:
        """Lee tabla de red de Pi-hole."""
        devices = []
        stdout, _, code = await run_async(
            '''docker exec pihole sqlite3 /etc/pihole/pihole-FTL.db \
            "SELECT hwaddr, ip, name FROM network WHERE hwaddr != '' ORDER BY lastQuery DESC LIMIT 100" 2>/dev/null''',
            timeout=10
        )

        if code != 0 or not stdout:
            return devices

        for line in stdout.split('\n'):
            parts = line.split('|')
            if len(parts) >= 2 and parts[0]:
                devices.append(NetworkDevice(
                    mac=parts[0],
                    ip=parts[1] if len(parts) > 1 else "",
                    hostname=parts[2] if len(parts) > 2 else "",
                    source="pihole"
                ))

        return devices

    async def _scan_mdns(self) -> List[NetworkDevice]:
        """Descubrimiento de dispositivos via mDNS/Bonjour/Avahi."""
        devices = []

        # Servicios mDNS comunes a buscar
        services = [
            '_airplay._tcp',      # Apple AirPlay
            '_raop._tcp',         # Apple Remote Audio
            '_googlecast._tcp',   # Chromecast
            '_spotify-connect._tcp',  # Spotify
            '_ipp._tcp',          # Impresoras IPP
            '_printer._tcp',      # Impresoras
            '_http._tcp',         # Servidores web
            '_homekit._tcp',      # HomeKit
            '_hap._tcp',          # HomeKit Accessory Protocol
            '_smb._tcp',          # Samba/Windows shares
            '_afpovertcp._tcp',   # Apple File Protocol
            '_ssh._tcp',          # SSH servers
            '_device-info._tcp',  # Device info
        ]

        for service in services:
            try:
                stdout, _, code = await run_async(
                    f"avahi-browse -rpt {service} 2>/dev/null | head -50",
                    timeout=5
                )

                if code != 0 or not stdout:
                    continue

                for line in stdout.split('\n'):
                    if not line or line.startswith('+'):
                        continue

                    parts = line.split(';')
                    if len(parts) < 8:
                        continue

                    try:
                        # =;interface;protocol;name;type;domain;hostname;ip;port;txt
                        if parts[0] != '=':
                            continue

                        hostname = parts[6].replace('.local', '') if len(parts) > 6 else ''
                        ip = parts[7] if len(parts) > 7 else ''

                        if not ip or not ip.startswith('192.168.'):
                            continue

                        # Obtener MAC via ARP
                        arp_out, _, _ = await run_async(f"arp -n {ip} 2>/dev/null", timeout=2)
                        mac = ""
                        if arp_out:
                            mac_match = re.search(r'([0-9a-f:]{17})', arp_out, re.I)
                            if mac_match:
                                mac = mac_match.group(1)

                        if not mac:
                            continue

                        # Buscar si ya existe
                        existing = None
                        for d in devices:
                            if d.mac == mac:
                                existing = d
                                break

                        if existing:
                            if service not in existing.mdns_services:
                                existing.mdns_services.append(service)
                            if not existing.mdns_name:
                                existing.mdns_name = hostname
                        else:
                            devices.append(NetworkDevice(
                                mac=mac,
                                ip=ip,
                                mdns_name=hostname,
                                mdns_services=[service],
                                source="mdns"
                            ))
                    except Exception as e:
                        logger.debug(f"Error parsing mDNS line: {e}")
                        continue

            except Exception as e:
                logger.debug(f"Error scanning mDNS service {service}: {e}")
                continue

        return devices

    async def _scan_ssdp(self) -> List[NetworkDevice]:
        """Descubrimiento de dispositivos via SSDP/UPnP."""
        devices = []

        # Enviar M-SEARCH para descubrir dispositivos UPnP
        ssdp_request = (
            'M-SEARCH * HTTP/1.1\r\n'
            'HOST: 239.255.255.250:1900\r\n'
            'MAN: "ssdp:discover"\r\n'
            'MX: 2\r\n'
            'ST: ssdp:all\r\n'
            '\r\n'
        )

        try:
            # Usar netcat para enviar SSDP multicast
            stdout, _, code = await run_async(
                f"timeout 3 bash -c 'echo -e \"{ssdp_request}\" | nc -u -w2 239.255.255.250 1900 2>/dev/null' | head -100",
                timeout=5
            )

            if code != 0 or not stdout:
                return devices

            # Parsear respuestas SSDP
            current_ip = None
            current_info = []

            for line in stdout.split('\n'):
                line = line.strip()

                if line.startswith('HTTP/'):
                    # Nueva respuesta
                    if current_ip and current_info:
                        # Obtener MAC via ARP
                        arp_out, _, _ = await run_async(f"arp -n {current_ip} 2>/dev/null", timeout=2)
                        mac = ""
                        if arp_out:
                            mac_match = re.search(r'([0-9a-f:]{17})', arp_out, re.I)
                            if mac_match:
                                mac = mac_match.group(1)

                        if mac:
                            devices.append(NetworkDevice(
                                mac=mac,
                                ip=current_ip,
                                ssdp_info=' | '.join(current_info)[:200],
                                source="ssdp"
                            ))

                    current_ip = None
                    current_info = []

                elif line.startswith('LOCATION:'):
                    # Extraer IP de la URL
                    match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                    if match:
                        current_ip = match.group(1)

                elif line.startswith('SERVER:') or line.startswith('ST:'):
                    info = line.split(':', 1)[1].strip()
                    if info and len(info) > 2:
                        current_info.append(info)

            # Última respuesta
            if current_ip and current_info:
                arp_out, _, _ = await run_async(f"arp -n {current_ip} 2>/dev/null", timeout=2)
                mac = ""
                if arp_out:
                    mac_match = re.search(r'([0-9a-f:]{17})', arp_out, re.I)
                    if mac_match:
                        mac = mac_match.group(1)

                if mac:
                    devices.append(NetworkDevice(
                        mac=mac,
                        ip=current_ip,
                        ssdp_info=' | '.join(current_info)[:200],
                        source="ssdp"
                    ))

        except Exception as e:
            logger.debug(f"Error in SSDP scan: {e}")

        return devices

    async def _scan_nmap(self) -> List[NetworkDevice]:
        """Escaneo nmap con detección de OS (lento)."""
        devices = []

        # Escaneo rápido de puertos comunes + detección OS
        stdout, stderr, code = await run_async(
            f"sudo nmap -sn -O --osscan-limit {config.LOCAL_NETWORK} 2>/dev/null",
            timeout=120
        )

        if code != 0:
            # Fallback sin detección OS
            stdout, _, code = await run_async(
                f"sudo nmap -sn {config.LOCAL_NETWORK} 2>/dev/null",
                timeout=60
            )

        if code != 0 or not stdout:
            return devices

        # Parsear salida nmap
        current_ip = None
        current_mac = None
        current_vendor = None
        current_os = None

        for line in stdout.split('\n'):
            # Nmap scan report for hostname (IP)
            if 'Nmap scan report for' in line:
                if current_ip and current_mac:
                    devices.append(NetworkDevice(
                        ip=current_ip,
                        mac=current_mac,
                        vendor=current_vendor or "",
                        os_guess=current_os or "",
                        source="nmap"
                    ))
                current_ip = current_mac = current_vendor = current_os = None

                match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                if match:
                    current_ip = match.group(1)

            elif 'MAC Address:' in line:
                match = re.search(r'MAC Address: ([0-9A-F:]+)\s*\(([^)]+)\)?', line, re.I)
                if match:
                    current_mac = match.group(1)
                    current_vendor = match.group(2) if match.lastindex >= 2 else ""

            elif 'OS details:' in line or 'Running:' in line:
                current_os = line.split(':', 1)[1].strip()[:50]

        # Último dispositivo
        if current_ip and current_mac:
            devices.append(NetworkDevice(
                ip=current_ip,
                mac=current_mac,
                vendor=current_vendor or "",
                os_guess=current_os or "",
                source="nmap"
            ))

        return devices

    async def scan_device_ports(self, ip: str) -> List[Tuple[int, str]]:
        """
        Escanea puertos abiertos de un dispositivo.

        Returns:
            Lista de (puerto, servicio)
        """
        ports = []
        stdout, _, code = await run_async(
            f"sudo nmap -sT -F --open {ip} 2>/dev/null",
            timeout=60
        )

        if code != 0 or not stdout:
            return ports

        for line in stdout.split('\n'):
            match = re.match(r'^(\d+)/tcp\s+open\s+(\S+)', line)
            if match:
                ports.append((int(match.group(1)), match.group(2)))

        return ports

    async def check_connectivity(self) -> Dict[str, dict]:
        """Verifica conectividad."""
        targets = [
            ("Router", "192.168.0.1"),
            ("Pi-hole DNS", "PI_IP_REDACTED"),
            ("Google DNS", "8.8.8.8"),
            ("Cloudflare", "1.1.1.1"),
            ("Google", "google.com"),
        ]

        async def ping_target(name: str, target: str) -> tuple:
            stdout, _, code = await run_async(
                f"ping -c 1 -W 2 {target} 2>/dev/null | grep -oP 'time=\\K[0-9.]+'",
                timeout=5
            )
            if code == 0 and stdout:
                return name, {"ok": True, "latency": f"{float(stdout):.1f}ms"}
            return name, {"ok": False, "latency": None}

        results = await asyncio.gather(
            *[ping_target(name, target) for name, target in targets]
        )

        return dict(results)

    async def traceroute(self, target: str) -> List[Dict[str, any]]:
        """
        Ejecuta traceroute.

        Returns:
            Lista de dicts {'hop': int, 'ip': str, 'rtt': float|None}
        """
        stdout, _, code = await run_async(
            f"traceroute -n -m 15 -w 2 {target} 2>/dev/null",
            timeout=60
        )

        hops = []
        if code != 0 or not stdout:
            return hops

        for line in stdout.split('\n')[1:]:  # Skip header
            line = line.strip()
            if not line:
                continue

            parts = line.split()
            if not parts:
                continue

            try:
                hop_num = int(parts[0])
            except ValueError:
                continue

            # Check for timeout (* * *)
            if '*' in parts[1]:
                hops.append({'hop': hop_num, 'ip': '*', 'rtt': None})
            else:
                ip = parts[1]
                # Find RTT (first numeric value after IP)
                rtt = None
                for part in parts[2:]:
                    try:
                        rtt = float(part.replace('ms', ''))
                        break
                    except ValueError:
                        continue
                hops.append({'hop': hop_num, 'ip': ip, 'rtt': rtt})

        return hops

    async def dns_lookup(self, domain: str) -> Dict[str, List[str]]:
        """
        Lookup DNS completo.

        Returns:
            Dict con keys 'A', 'AAAA', 'MX', 'NS', 'CNAME', 'TXT'
        """
        result = {}

        # A record
        stdout, _, _ = await run_async(f"dig +short A {domain} 2>/dev/null", timeout=10)
        if stdout and not stdout.startswith(';'):
            result["A"] = [ip for ip in stdout.split('\n') if ip and '.' in ip]

        # AAAA record
        stdout, _, _ = await run_async(f"dig +short AAAA {domain} 2>/dev/null", timeout=10)
        if stdout and not stdout.startswith(';'):
            result["AAAA"] = [ip for ip in stdout.split('\n') if ip and ':' in ip]

        # MX record
        stdout, _, _ = await run_async(f"dig +short MX {domain} 2>/dev/null", timeout=10)
        if stdout and not stdout.startswith(';'):
            result["MX"] = [mx.split()[-1].rstrip('.') for mx in stdout.split('\n') if mx]

        # NS record
        stdout, _, _ = await run_async(f"dig +short NS {domain} 2>/dev/null", timeout=10)
        if stdout and not stdout.startswith(';'):
            result["NS"] = [ns.rstrip('.') for ns in stdout.split('\n') if ns]

        # CNAME record
        stdout, _, _ = await run_async(f"dig +short CNAME {domain} 2>/dev/null", timeout=10)
        if stdout and not stdout.startswith(';'):
            result["CNAME"] = [cn.rstrip('.') for cn in stdout.split('\n') if cn]

        # TXT record
        stdout, _, _ = await run_async(f"dig +short TXT {domain} 2>/dev/null", timeout=10)
        if stdout and not stdout.startswith(';'):
            result["TXT"] = [txt.strip('"') for txt in stdout.split('\n') if txt]

        return result

    async def check_port(self, host: str, port: int) -> Tuple[bool, float]:
        """
        Verifica si un puerto está abierto.

        Returns:
            Tuple (is_open, latency_ms)
        """
        import time
        start = time.time()
        stdout, _, code = await run_async(
            f"nc -zv -w 2 {host} {port} 2>&1",
            timeout=5
        )
        latency = (time.time() - start) * 1000
        return code == 0, latency

    def get_device_by_ip(self, ip: str) -> Optional[NetworkDevice]:
        """Busca dispositivo por IP."""
        for device in self._cache.values():
            if device.ip == ip:
                return device
        return None

    def get_device_by_mac(self, mac: str) -> Optional[NetworkDevice]:
        """Busca dispositivo por MAC."""
        mac = NetworkDevice._format_mac(mac)
        return self._cache.get(mac)

    def get_all_devices(self) -> List[NetworkDevice]:
        """Todos los dispositivos (online + offline)."""
        return list(self._cache.values())

    def get_cached_devices(self) -> List[NetworkDevice]:
        """Dispositivos en cache (online)."""
        return self.get_online_devices()

    def get_online_devices(self) -> List[NetworkDevice]:
        """Solo dispositivos online."""
        return [d for d in self._cache.values() if d.is_online]

    def get_offline_devices(self) -> List[NetworkDevice]:
        """Dispositivos vistos antes pero ahora offline."""
        return [d for d in self._cache.values() if not d.is_online]

    def get_new_devices(self, since_hours: int = 24) -> List[NetworkDevice]:
        """Dispositivos vistos por primera vez en las últimas N horas."""
        cutoff = datetime.now() - timedelta(hours=since_hours)
        return [d for d in self._cache.values() if d.first_seen > cutoff]

    def get_statistics(self) -> Dict[str, any]:
        """Estadísticas de red."""
        devices = list(self._cache.values())
        online = [d for d in devices if d.is_online]

        # Contar por tipo
        by_type = {}
        for d in online:
            t = d.device_type
            by_type[t] = by_type.get(t, 0) + 1

        # Contar por fabricante
        by_vendor = {}
        for d in online:
            v = d.vendor or "Unknown"
            by_vendor[v] = by_vendor.get(v, 0) + 1

        return {
            "total_known": len(devices),
            "online": len(online),
            "offline": len(devices) - len(online),
            "by_type": by_type,
            "by_vendor": by_vendor,
            "last_scan": self._last_scan.isoformat() if self._last_scan else None
        }

    @staticmethod
    def _ip_sort_key(ip: str) -> tuple:
        try:
            return tuple(int(x) for x in ip.split('.'))
        except:
            return (999, 999, 999, 999)
