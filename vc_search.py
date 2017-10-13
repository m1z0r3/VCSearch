# -*- coding: utf-8 -*-

import os.path
import json
import logging
import time

from google.protobuf.message import DecodeError
from requests.exceptions import ConnectionError
from googleplay_api import googleplay
import config

# TODO
# Handle ip, account ban

class PackageError(Exception):
    def __init__(self, value):
        super(Exception, self).__init__()
        self.value = value

    def __str__(self):
        return repr(self.value)


class VersionCodeAPI(googleplay.GooglePlayAPI):
    MAX_VC = 40347
    INTERVAL_SECS = 2
    MAX_ERR_COUNT = 5

    def __init__(self, androidId, lang, log_path):
        super(VersionCodeAPI, self).__init__(androidId, lang)
        self.logger = create_logger(log_path)

    def purchase(self, pkg_name, vc, ot=1):
        """purchase
        Fetch download url and download cookie for an app (pkg_name).

        :param pkg_name: Package name of the app
        :param vc: versionCode
        :param ot: offerType
        """
        self.logger.debug("purchase(pkg_name={}, vc={}, ot={}".format(pkg_name, vc, ot))
        path = "purchase"
        data = "ot=%d&doc=%s&vc=%d" % (ot, pkg_name, vc)
        message = self.executeRequestApi2(path, data)
        return message.payload.buyResponse

    def __check_vc_exists(self, pkg_name, vc):
        decode_err_count = 0
        while True:
            try:
                buy_res = self.purchase(pkg_name, vc)
            except DecodeError as e:
                decode_err_count += 1
                if decode_err_count > VersionCodeAPI.MAX_ERR_COUNT:
                    self.logger.exception("DecodeError exceeds max error count")
                    raise e
            else:
                break

        vc_exists = len(buy_res.SerializeToString()) != 0
        self.logger.debug("check {}:{} exists, {}".format(pkg_name, vc, vc_exists))
        return vc_exists

    def __fetch_latest_vc(self, pkg_name):
        """__fetch_latest_vc
        Fetch the versionCode of the latest version of an app (pkg_name)

        :param pkg_name:
        """
        m = self.details(pkg_name)
        doc = m.docV2
        latest_vc = doc.details.appDetails.versionCode
        return latest_vc

    def fetch_existing_vcs(self, pkg_name):
        self.logger.info("fetch existing vcs, {}".format(pkg_name))
        latest_vc = self.__fetch_latest_vc(pkg_name)

        pkg_name_exists = latest_vc != 0
        if not pkg_name_exists:
            msg = "{} does not exist".format(pkg_name)
            self.logger.info(msg)
            raise PackageError(msg)

        if latest_vc > VersionCodeAPI.MAX_VC:
            msg = "{} exceeds max versionCode".format(latest_vc)
            self.logger.info(msg)
            raise PackageError(msg)

        # Test all the possible versionCodes to check if they exist or not
        existing_vcs = list()
        for vc in xrange(latest_vc, 0, -1):
            vc_exists = self.__check_vc_exists(pkg_name, vc)
            time.sleep(VersionCodeAPI.INTERVAL_SECS)
            if vc_exists:
                existing_vcs.append(vc)

        return existing_vcs


def dump_existing_vcs(api, pkg_name):
    # Give up if an error occors
    try:
        vcs = api.fetch_existing_vcs(pkg_name)
    except (ConnectionError, PackageError, DecodeError):
        return

    filename = config.VC_FILENAME_FORMAT.format(pkg_name)
    with open(filename,  "w") as f:
        f.write(json.dumps(vcs, indent=4))


def create_logger(log_path):
    logger = logging.getLogger(__name__)
    logger.setLevel(config.LOGGER_LEVEL)

    f_handler = logging.FileHandler(log_path)
    f_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(message)s")
    f_handler.setFormatter(formatter)
    logger.addHandler(f_handler)

    s_handler = logging.StreamHandler()
    s_handler.setLevel(logging.DEBUG)
    logger.addHandler(s_handler)

    return logger

def load_pkg_names_from_json(filename):
    with open(filename, "r") as f:
        return json.load(f)

def main():
    api = VersionCodeAPI(config.ANDROID_DEVICE_ID, config.LANG, config.LOG_PATH)
    api.login(config.GOOGLE_LOGIN, config.GOOGLE_PASSWORD)

    pkg_names = load_pkg_names_from_json(config.PKG_FILEPATH)
    for pkg_name in pkg_names:
        dump_existing_vcs(api, pkg_name)


if __name__ == "__main__":
    main()

