#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-11-13 12:03:28
# @作者  : "jym"
# @说明    : adsl重拨
# @Version : $Id$
import time
import win32ras
import os
from util import retry
import requests,json
import sys
sys.path.append("..")
from config import vps_name,adsl_infos
def reboot():
    os.system("shutdown -r -t 0")

def get_ip():
    try:
        url = "https://tool.lu/netcard/ajax.html"
        req = requests.post(url,timeout=15,verify=False)
        req.encoding = "utf-8"
        text = req.text
        json_data = json.loads(text)
        ip = json_data["text"]["ip"]
        return ip
    except Exception,e:
        return 0
def check_internet():
    ip = get_ip()
    if ip==0 or ip.startswith("58"):
        return False
    return True 


class AdslCtl(object):
    def __init__(self):
        name = adsl_infos[vps_name]['adsl_name']
        account = adsl_infos[vps_name]['adsl_account']
        pwd = adsl_infos[vps_name]['adsl_pwd']
        self.dial_params = (name,'','',account,pwd)

    def connect(self):
        max_retries = 5
        for _ in range(max_retries):
            handler ,ret = win32ras.Dial(None, None, self.dial_params, None)
            time.sleep(5)
            ret = check_internet()
            if ret:
                return
            else:
                time.sleep(10)
        reboot()
    def disconnect(self):
        for _ in range(5):
            for handle, name, devtype, devname in win32ras.EnumConnections():
                win32ras.HangUp(handle)
            time.sleep(3)
            ret = check_internet()
            if not ret:
                return
        reboot()    
    def reconnect(self):
        self.disconnect()
        time.sleep(20)
        self.connect()
if __name__ == '__main__':
    adsl = AdslCtl()
    adsl.connect()
    time.sleep(5)
    adsl.disconnect()