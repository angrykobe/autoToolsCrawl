# -*- coding: utf-8 -*-
# @Date    : 2017-11-20 10:49:30
# @作者  : "jym"
# @说明    : 文书网数据获取
# @Version : $Id$
import requests
from util.get_vl5x import getKey
from util.AdslCtl import AdslCtl
import json
from verify.captcha import verify
from util.util import retry,showTime,delayTime
from config import master_ip
import time
import random
import calendar
import copy



class WenshuCourt(object):
    def __init__(self):
        self.headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36',
            'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Charset':'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
            'Referer':'http://wenshu.court.gov.cn',
            'Connection':'keep-alive',
            'Accept-Encoding':'gzip, deflate',
            }
        
        self.param_content ={
            'Param':'',
            'vl5x':'',
            'number':'',
            'guid':'',
            }
        self.param_court = {"Param":"","parval":""}
        self.cookie = {}
        self.adsl_ctl = AdslCtl()
        self.reconnect_only()
        self.mode = 0 #0:获取content，1:获取courtList
        self.Year = None
        self.courtinfo_url = 'http://' + master_ip + ':8000' + '/courtinfo'
        self.paraminfo_url = 'http://' + master_ip + ':8000' + '/paraminfo'
        self.docIdinfo_url = 'http://' + master_ip + ':8000' + '/docIdinfo'
        self.contentinfo_url = 'http://' + master_ip + ':8000' + '/content_info'
        self.session = requests.session()
    def reconnect_only(self):
        self.adsl_ctl.reconnect()

    def reconnect(self):
        self.adsl_ctl.reconnect()
        self.reset_cookies()
        if self.mode == 0:
            self.reset_param_content()
    
    @retry(exceptions=(requests.RequestException,), max_retries=-1, interval=10,success=lambda x: x!=None,retry_func="reconnect_only")
    def _get_vjkl5(self):
        url = "http://wenshu.court.gov.cn/List/List?sorttype=1&conditions=searchWord+1++%E6%B0%91%E4%BA%8B%E6%A1%88%E4%BB%B6+%E6%A1%88%E4%BB%B6%E7%B1%BB%E5%9E%8B:%E6%B0%91%E4%BA%8B%E6%A1%88%E4%BB%B6"
        self.vjkl5 = None
        req = requests.get(url,headers=self.headers,timeout=60)
        self.vjkl5 = req.cookies["vjkl5"]
        self.cookie['vjkl5'] = self.vjkl5
        return self.vjkl5
    
    @retry(exceptions=(Exception,), max_retries = -1, interval=3, success=lambda x:x!=None, retry_func="_get_vjkl5")
    def get_vl5x(self):
        if self.vjkl5 == None:
            self._get_vjkl5()
        self.vl5x = None
        self.vl5x = getKey(self.vjkl5)
        return self.vl5x

    def _createGuid(self):
        return hex(int((1 + random.random()) * 0x10000) | 0)[1:]

    def create_guid(self):
        guid = self._createGuid() + self._createGuid() + '-' +\
            self._createGuid() + '-' +\
            self._createGuid() + self._createGuid() + '-' + \
            self._createGuid() + self._createGuid() + self._createGuid()
        return guid

    @retry(exceptions=(requests.RequestException,Exception), max_retries=-1, interval=10,success=lambda x: x!='"remind key"',retry_func = "reconnect")
    def get_number(self):
        url = "http://wenshu.court.gov.cn/ValiCode/GetCode"
        data = { "guid": self.guid}
        req = requests.post(url,headers=self.headers,cookies=self.cookie,data=data)
        return req.text


    def reset_cookies(self):
        self._get_vjkl5()
        
        self.cookie["Hm_lpvt_3f1a54c5a86d62407544d433f6418ef5"] = str(int(time.time()))
        self.cookie["Hm_lvt_3f1a54c5a86d62407544d433f6418ef5"] = str(int(time.time()))
        self.cookie["_gscu_2116842793"] = "12630095dgl3kx18"
    def reset_param_content(self):
        self.get_vl5x()
        self.guid = self.create_guid()
        self.number = self.get_number()

        self.param_content['vl5x'] = self.vl5x        
        self.param_content['number'] = self.number
        self.param_content['guid'] = self.guid
    
    def reset_param_court(self,Param,parval):

        self.param_court['Param'] = Param
        self.param_court['parval'] = parval
        
    def reset_Hm_lpvt(self):
        self.cookie["Hm_lpvt_3f1a54c5a86d62407544d433f6418ef5"] = str(int(time.time()))

    def reset_params(self,Param,parval=""):
        if self.mode == 0:
            self.param_content['Param'] = Param
        else:
            self.param_court['Param'] = Param
            self.param_court['parval'] = parval

    @retry(exceptions=(requests.RequestException,Exception), max_retries=-1, interval=10,success=lambda x: x!='"remind key"',retry_func = "reconnect")
    def get_data(self,url):
        if url == "http://wenshu.court.gov.cn/List/CourtTreeContent":
            req = requests.post(url=url,headers=self.headers, data=self.param_court,cookies=self.cookie,timeout=60)
        elif url.startswith('http://wenshu.court.gov.cn/CreateContentJS/CreateContentJS.aspx?DocID='):
            req = requests.get(url=url,headers=self.headers)
            req.text = req.text.split("\n")[1].replace("var jsonHtmlData = ","")[0:-2]
        else:
            req = requests.post(url=url,headers=self.headers,data=self.param_content,cookies=self.cookie,timeout=60)
        self.reset_Hm_lpvt()
        if self.mode == 1 and req.text == '""':
            return req.text
        dic = eval(req.text)
        dic = eval(dic)
        data = json.dumps(dic,encoding='utf-8',ensure_ascii=False)
        data = json.loads(data)
        return data
        

    def get_courtTree(self,index = 0, Param = u"高级法院",parval = ""):
        court_level = [u"最高法院",u"高级法院",u"中级法院",u"基层法院"]
        if index == 0:
            self.mode = 0
            self.reset_params(u"")
            data = self.get_data("http://wenshu.court.gov.cn/List/TreeContent")
            for item in data[3]["Child"]:
                if item["Key"] != "":
                    print item["Key"]
                    if item["Key"] == u"最高人民法院":
                        court = {"court_name":u"最高人民法院",
                                 "court_level":u"最高法院",
                                 "court_parent":u""}
                        self.post_court(court)                    
                    else:
                        court = {"court_name":item["Key"],
                                 "court_level":u"高级法院",
                                 "court_parent":u"最高人民法院"}
                        self.post_court(court)
                        param = u"法院层级:中级法院," + u"法院地域:"+item["Key"]
                        self.get_courtTree(2,param,item["Key"])
        else:
            self.mode = 1
            self.reset_params(Param,parval)
            data = self.get_data("http://wenshu.court.gov.cn/List/CourtTreeContent")
            if data!='""':
                for item in data[0]["Child"]:
                    print item["Key"]
                    if item["Key"] !="":
                        court = {"court_name":item["Key"],
                                 "court_level":court_level[index],
                                 "court_parent":parval}
                        self.post_court(court)
                        param = u"法院层级:基层法院," + u"中级法院:"+item["Key"]
                        if index == 2:
                            self.get_courtTree(3,param,item["Key"])


    def checkEnded(self,text):
        if text == 'No Data':
            print u'本次作业结束'
            return True
        return False

    @retry(exceptions=(Exception,), max_retries = -1, interval=10,retry_func = "reconnect")
    def make_param(self,court,paramDic,yearFlag=False,monthFlag=False,dateFlag=False):
        court_name = court["court_name"]
        court_level = court["court_level"]
        if court_level == u"最高法院":
            paramDic[u"法院层级"] = u"最高法院"
        elif court_level == u"高级法院":
            paramDic[u"法院层级"] = u"高级法院"
            paramDic[u"法院地域"] = court_name
        else:
            paramDic[u"法院层级"] = court_level
            paramDic[court_level] = court_name
        param_list = [u"裁判年份:",u"审判程序:"]
        #date_list = ["-01-01","-03-31","-04-01","-06-30","-07-01","-09-30","-10-01","-12-31"]
        param = ",".join([k+":"+v for k,v in paramDic.items()])
        self.reset_params(param)
        print param
        while True:
            data = self.get_data("http://wenshu.court.gov.cn/List/TreeContent")
            if (data != [] and data != '"[]"'):
                break
            self.reconnect()
        if data[-1]["IntValue"]<=2000 or dateFlag==True:
            data = {
                    "param":param,
                    "count":data[-1]["IntValue"]
                    }
            self.post_param(data)
        else:
            if paramDic.has_key[u"案件类型"] == False:
                for docType in [u"民事案件",u"刑事案件",u"执行案件",u"赔偿案件",u"行政案件"]:
                    paramDic_New = copy.copy(paramDic)
                    paramDic_New[u"案件类型"] = docType
                    self.make_param(court,paramDic_New)
            elif yearFlag == False:
                for item in data[4]["Child"]:
                    year = item["Key"]
                    paramDic_New = copy.copy(paramDic)
                    paramDic_New[u"裁判年份"] = year
                    self.make_param(court,paramDic_New,yearFlag=True)
            elif monthFlag == False:
                for month in range(1,13):
                    year = int(paramDic[u"裁判年份"])
                    firstDate = "01"
                    lastDate = str(calendar.monthrange(year,month)[1])
                    year = str(year)
                    if month<10:
                        month = "0%d"%month
                    else:
                        month = str(month)
                    paramDic_New = copy.copy(paramDic)
                    paramDic_New[u"裁判日期"] = year + "-" + month + "-" + firstDate + " TO " + year + "-" + month + "-" + lastDate
                    self.make_param(court,paramDic_New,yearFlag=True,monthFlag=True)
            elif dateFlag == False:
                year,month = paramDic[u"裁判日期"].split("-")[0:2]
                firstDate = 1
                lastDate = calendar.monthrange(int(year),int(month))[1]
                for day in range(firstDate,lastDate+1):
                    if day<10:
                        day = "0%d"%day
                    else:
                        day = str(day)
                    paramDic_New = copy.copy(paramDic)
                    paramDic_New[u"裁判日期"] = year + "-" + month + "-" + day + " TO " + year + "-" + month + "-" + day
                    self.make_param(court,paramDic_New,yearFlag=True,monthFlag=True,dateFlag=True)
    
    def make_all_params(self):
        #court_list = get_court_list(self.mydb)
        while True:
            req = requests.get(self.paraminfo_url)
            if self.checkEnded(req.text):
                break
            court = json.loads(req.text)
            self.make_param(court,paramDic={u"上传日期":"1996-01-01 TO 2018-03-06"})
            self.updateCourtStatus(court)

    @retry(exceptions=(Exception,), max_retries = -1, interval=10,retry_func = "reconnect")
    def get_docIds(self,param,count):
        url = "http://wenshu.court.gov.cn/List/ListContent"
        self.reset_params(param)
        pageNum = lambda x:x/20 if x%20==0 else x/20+1
        for pageIndex in range(1,pageNum(count) + 1):
            self.param_content["Index"] = str(pageIndex)
            while True:
                data = self.get_data(url)
                if data!=[] and data !='"[]"':
                    break
            self.post_docids(data[1:])
            showTime()
    def get_all_docIds(self):
        self.param_content["Direction"] = "asc"
        self.param_content["Page"] = "20"
        self.param_content["Order"] = u"裁判日期"
        while True:
            req = requests.get(self.docIdinfo_url)
            if self.checkEnded(req.text):
                break
            data = json.loads(req.text)
            Param,count = data["param"],data["count"]
            if count>=2000:
                count = 2000
            self.get_docIds(Param,count)
            self.updateParamStatus(Param)
    def get_content(self,docId):
        url = 'http://wenshu.court.gov.cn/CreateContentJS/CreateContentJS.aspx?DocID=%s'%docId
        data = self.get_data(url)
        self.post_content(data)

    def get_all_contents(self):
        while True:
            req = requests.get(self.contentinfo_url)
            if self.checkEnded(req.text):
                break
            data = json.loads(req.text)
            docid = data[u"文书ID"]
            self.get_content(docid)
            self.updateDocidStatus(docid)
    
    def post_court(self,court):
        self.session.post(url=self.courtinfo_url, headers=self.headers, data={"type":"post_data","data":json.dumps(court)})
    def post_param(self,param):
        self.session.post(url=self.paraminfo_url, headers=self.headers, data={"type":"post_data","data":json.dumps(param)})
    def post_docids(self,docids):
        self.session.post(url=self.docIdinfo_url, headers=self.headers, data={"type":"post_data","data":str(docids)})
    def post_content(self,content):
        self.session.post(url=self.docIdinfo_url, headers=self.headers, data={"type":"post_data","data":json.dumps(content)})
    def updateCourtStatus(self,court):
        self.session.post(url=self.paraminfo_url, headers=self.headers, data={"type":"post_status","data":json.dumps(court)})
    def updateParamStatus(self,Param):
        self.session.post(url=self.docIdinfo_url, headers=self.headers, data={"type":"post_status","data":Param})
    def updateDocidStatus(self,docid):
        self.session.post(url=self.paraminfo_url, headers=self.headers, data={"type":"post_status","data":docid})
def main():
    wenshucourt = WenshuCourt()
    wenshucourt.get_courtTree()
    #wenshucourt.make_all_params()
    #wenshucourt.get_all_docIds()
    #wenshucourt.get_content('1')
if __name__ == '__main__':
    main()
