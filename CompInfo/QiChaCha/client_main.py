# -*- coding: utf-8 -*-
# @Date    : 2018-01-15 16:24:27
# @Author  : jym
# @Description:
# @Version : v0.0
import requests
import json
import time
import re
from util.AdslCtl import AdslCtl
import json
from util.util import retry,showTime,delayTime,distance
from config import master_ip
from validate.loginAndValidate import LoginAndValidate
import browsercookie
import random
from config import master_ip
class QiChachaMap(object):
    def __init__(self):
        self.adsl = AdslCtl()
        self.adsl.reconnect()
        self.master_url = 'http://%s:8001/'%master_ip
        self.searchByLocation_url = 'http://www.qichacha.com/map'
        self.loginAndValidate = LoginAndValidate()
        self.userInfo = {}
        self.get_userinfo()
        self.cookies = {}
        self.loginQiChaCha()
        self.openMapSearch()
        
    def get_userinfo(self):
        req = requests.get(self.master_url + 'userInfo')
        if req.text != '':
            self.userInfo = json.loads(req.text)
        else:
            self.userInfo = {}
    def release_userinfo(self):
        if self.userInfo != {}:
            requests.post(self.master_url + 'userInfo',data = json.dumps(self.userInfo))

    def reconnect(self):
        #self.release_userinfo()
        self.adsl.reconnect()
        #self.get_userinfo()
        self.loginQiChaCha()
        self.openMapSearch()

    @retry(exceptions=(Exception,), max_retries=-1, interval=10,retry_func="reconnect")
    def loginQiChaCha(self):
        if self.userInfo not in [{},[]] and self.userInfo.has_key('user'):
            return self.loginAndValidate.login(self.userInfo)
        else:
            return True

    def openMapSearch(self):
        self.loginAndValidate.openChrome(self.searchByLocation_url)
        time.sleep(10)
    def refreshChrome(self):
        self.loginAndValidate.refreshChrome()
    
    @retry(exceptions=(Exception,), max_retries=-1, interval=10,retry_func="reconnect")
    def validate(self):
        return self.loginAndValidate.validate()
        
    @retry(exceptions=(Exception,), max_retries=-1, interval=10,retry_func="reconnect")
    @retry(exceptions=(Exception,), max_retries=3, interval=10)
    def get_cookies(self):
        while True:
            ret = self.loginAndValidate.drawCircle()
            if ret == False:
                self.loginAndValidate.closeChrome()
                self.openMapSearch()
                self.validate()
            else:
                break
        time.sleep(3)
        cookies = browsercookie.chrome()
        for item in cookies:
            if item.domain in ['www.qichacha.com','.qichacha.com']:
                self.cookies[item.name] = item.value

        

    @retry(exceptions=(Exception,), max_retries=-1, interval=10,retry_func="reconnect")
    @retry(exceptions=(Exception,), max_retries=2, interval=10,retry_func = "get_cookies")
    def searchByLocation(self,paramDict):
        url = 'http://www.qichacha.com/map_searchByLocation'
        headers = {
            'Host': 'http://www.qichacha.com',
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
            'Origin': 'http://www.qichacha.com',
            'Referer': 'http://www.qichacha.com/map'
        }
        data = {
            'registCapiBegin':paramDict['registCapiBegin'],
            'registCapiEnd':paramDict['registCapiEnd'], 
            'industryCode':paramDict['industryCode'],   
            'statusCode':paramDict['statusCode'],  
            'startDateEnd':paramDict['startDateEnd'],    
            'startDateBegin':paramDict['startDateBegin'],  
            'sortField':'',   
            'searchKey':'', 
            'isSortAsc':'',
            'subIndustryCode':paramDict['subIndustryCode'],
            'pageIndex':1,
            'pageSize':100,
            'longitude':paramDict['longitude'],
            'latitude':paramDict['latitude'],
            'distance':paramDict['distance'],
            'searchType':'multiple'
        }
        try:
            self._update_cookie()
        except Exception,e:
            pass
        req = requests.post(url=url,headers=headers,data=data,cookies=self.cookies)
        data = json.loads(req.text)
        listCount = data['listCount']
        return data

    def searchByKeyName(self):
        pass
    def _update_cookie(self):
        t = str((int(round(time.time() * 1000)))-100)
        self.cookies['zg_de1d1a35bfa24ce29bbf2c7eb17e6c4f'] = re.sub('%22updated%22%3A%201516094289665%2C%22info','%22updated%22%3A%'+t+'%2C%22info',self.cookies['zg_de1d1a35bfa24ce29bbf2c7eb17e6c4f'])


    def _split_loc(self,paramInfo):
        lat1,lng1,lat2,lng2 = paramInfo['loc_data']
        latitude = (lat1 + lat2)/2
        longitude = (lng1 + lng2)/2
        rectange_list =[[lat1,lng1,latitude,longitude],
                        [latitude,longitude,lat2,lng2],
                        [lat1,longitude,latitude,lng2],
                        [latitude,lng1,lat2,longitude]]

        for loc_data in rectange_list:
            paramInfo['param']['latitude'] = (loc_data[0]+loc_data[2])/2
            paramInfo['param']['longitude'] = (loc_data[1]+loc_data[3])/2
            paramInfo['param']['distance'] = distance(loc_data[0],loc_data[1],loc_data[2],loc_data[3])/2
            paramInfo['loc_data'] = loc_data
            self.post_paramInfo(paramInfo)
    def _split_registCapi(self,paramInfo,data):
        registCapiRange = range(0,10,2) + range(10,100,10) + range(100,1000,100) + range(1000,5000,200)
        registCapiRange = [str(item) if item>0 else "" for item in registCapiRange]
        for i in range(len(registCapiRange)):
            paramInfo['param']['registCapiBegin'] = registCapiRange[i]
            try:
                paramInfo['param']['registCapiEnd'] = registCapiRange[i+1]
            except Exception,e:
                paramInfo['param']['registCapiEnd'] = ""
            self.post_paramInfo(paramInfo)
    def _split_statusCode(self,paramInfo,data):
        for items in data['groupItems']:
            if items['Key'] == 'statuscode':
                for item in items['Items']:
                    statuscode = item['Value']
                    paramInfo['param']['statusCode'] = statuscode
                    self.post_paramInfo(paramInfo)
    def _split_industryCode(self,paramInfo,data):
        for items in data['groupItems']:
            if items['Key'] == 'industrycode':
                for item in items['Items']:
                    industrycode = item['Value']
                    if industrycode == '':
                        industrycode = '0'
                    paramInfo['param']['industryCode'] = industrycode
                    self.post_paramInfo(paramInfo)
    def _split_startday(self,paramInfo,data):
        for items in data['groupItems']:
            if items['Key'] == 'startdateyear':
                for item in items['Items']:
                    year = item['Value']
                    paramInfo['param']['startDateBegin'] = year +'0101'
                    paramInfo['param']['startDateEnd'] = str(int(year)+1) + '0101'
                    self.post_paramInfo(paramInfo)
    def updateparam(self,paramInfo,data):
        if paramInfo['param']['distance']>=1:
            self._split_loc(paramInfo)
        elif paramInfo['param']['startDateBegin']==paramInfo['param']['startDateEnd']=='':
            self._split_startday(paramInfo,data)
        elif paramInfo['param']['registCapiBegin']==paramInfo['param']['registCapiEnd']=='':
            self._split_registCapi(paramInfo,data)
        elif paramInfo['param']['statusCode'] == '':
            self._split_statusCode(paramInfo,data)
        elif paramInfo['param']['industryCode'] == '':
            self._split_industryCode(paramInfo,data)

    def get_compList(self):
        self.get_cookies()
        while True:
            random.randint(1,3)
            req = requests.get(self.master_url)
            paramInfo = json.loads(req.text)
            paramid = paramInfo['ParamId']
            param = paramInfo['param']
            loc_data = paramInfo['loc_data']
            if (paramInfo['param']['startDateBegin']!='' or paramInfo['param']['startDateEnd']!='') and self.userInfo=={}:
                continue
            data = self.searchByLocation(param)
            showTime()
            if data['listCount']:
                self.post_compInfos(paramid,data['list'])
                if data['listCount']>=100:
                    self.updateparam(paramInfo,data)
            else:
                self.post_status(paramid)          
    def post_compInfos(self,paramid,compInfos):
        requests.post(self.master_url,data={'ParamId':paramid,'compInfos':str(compInfos),'type':'post_compinfos'})
    def post_paramInfo(self,paramInfo):
        requests.post(self.master_url,data={'paramInfo':json.dumps(paramInfo),'type':'post_param'})
    def post_status(self,paramid):
        requests.post(self.master_url,data={'ParamId':paramid,'type':'post_status'})
qichacha = QiChachaMap()
qichacha.get_compList()
