#encoding:utf-8
from TycApi import TianYanCha
import requests
import time
from util.AdslCtl import AdslCtl
import json
from util.util import retry,showTime,delayTime,delCookies
from config import db_get_ip,db_save_ip


class CompInfo(object):
    """docstring for CompInfo"""
    def __init__(self):
        super(CompInfo, self).__init__()
        self.db_get_url = 'http://%s:8003/'%db_get_ip   
        self.db_save_url = 'http://%s:8001/'%db_save_ip   
        self.tycApi = TianYanCha()
        self.adsl = AdslCtl()
        self.adsl.reconnect()
    def reconnect(self):
        delCookies()
        self.adsl.reconnect()


    @retry(exceptions=(Exception,), max_retries=-1, interval=10,retry_func="reconnect")
    def get_compInfo(self,compName,id_tyc):
        compInfo = self.tycApi.get_compInfo(compName,id_tyc)
        print compName,":",showTime()
        return compInfo
    
    def post_status(self,id_qcc,id_tyc):
        requests.post(self.db_get_url,data = {'KeyNo':id_qcc,'id_tyc':id_tyc})
    def post_compInfo(self,compInfo):
        requests.post(self.db_save_url,data = {'compInfo':str(compInfo)})
    def get_all_compInfo(self):
        while True:
            req = requests.get(self.db_get_url)
            data = json.loads(req.text)
            id_qcc = data['KeyNo']
            compName = data['Name']
            id_tyc = self.tycApi._get_id_tyc(compName)
            if id_tyc:
                compInfo = self.get_compInfo(compName,id_tyc)
                self.post_status(id_qcc,id_tyc)
                self.post_compInfo(compInfo)
if __name__ == '__main__':
    get_info = CompInfo()
    get_info.get_all_compInfo()