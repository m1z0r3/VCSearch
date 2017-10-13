# -*- coding: utf-8 -*-

import os
import logging

# input setting
PKG_FILEPATH = os.path.normpath("packages.json")

# output setting
VC_FILENAME_FORMAT = os.path.join(os.path.dirname(__file__), "vc/{}.json")
LOGGER_LEVEL = logging.DEBUG
LOG_PATH = os.path.normpath("versionCode.log")

# api credentials
ANDROID_DEVICE_ID = ""
GOOGLE_LOGIN = ""
GOOGLE_PASSWORD = ""
LANG = "en_US"
