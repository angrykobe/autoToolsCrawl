#encoding:utf-8
#获取页面信息的cookie
import requests
import json
import re

def get_tongjidata(url):
    #https://www.tianyancha.com/tongji/北京红黄蓝儿童教育科技发展有限公司.json?
    cookies = {}

    req = requests.get(url,cookies=cookies,verify=False)
    cookies = {}
    for item in req.cookies:
        cookies[item.name] = item.value
    tongji_data = json.loads(req.text)
    return tongji_data,cookies
def get_cookie(tongji_data,cookies):
    data = tongji_data['data'].split(",")
    fnStr = ""
    for char in data:
        fnStr += chr(int(char))
    print fnStr
    matchObj = re.match(r".*?token=(.*?);path=/;';n\.wtf=function\(\){return'(.*?)'}}\(window\);",fnStr)
    token = matchObj.group(1)
    wtf_data = matchObj.group(2)
    chars = ""
    base64chars = "abcdefghijklmnopqrstuvwxyz1234567890-~!"
    rsid = ["18","31","7","35","15","6","28","13","12","24","11","3","23","4","0","10","25","20","5","29","17","1","36","32","14","2","8","33","21","27","26","34","16","22","19","9","30"]
    for i in range(len(rsid)):
        chars += base64chars[int(rsid[i])]
    fxckStr = ""
    fxck = wtf_data.split(",")
    for i in range(len(fxck)):
        fxckStr += chars[int(fxck[i])]
    utm = fxckStr
    cookies['_utm'] = utm
    cookies['token'] = token
    return cookies


def test():
    
    tongji_data ,cookies = get_tongjidata(u'https://www.tianyancha.com/tongji/北京红黄蓝儿童教育科技发展有限公司.json?')
    #tongji_data = json.loads('{"state":"ok","message":"","special":"","vipMessage":"","isLogin":0,"data":{"name":"13157554","uv":0,"pv":0,"v":"33,102,117,110,99,116,105,111,110,40,110,41,123,100,111,99,117,109,101,110,116,46,99,111,111,107,105,101,61,39,114,116,111,107,101,110,61,100,97,97,56,51,101,97,49,49,56,99,49,52,99,53,102,57,98,53,52,100,102,56,99,99,100,100,49,51,55,100,55,59,112,97,116,104,61,47,59,39,59,110,46,119,116,102,61,102,117,110,99,116,105,111,110,40,41,123,114,101,116,117,114,110,39,49,56,44,49,57,44,51,49,44,51,54,44,49,49,44,49,57,44,53,44,50,56,44,50,51,44,49,49,44,49,54,44,55,44,49,57,44,50,53,44,49,56,44,56,44,50,51,44,56,44,50,56,44,51,49,44,50,56,44,49,54,44,51,49,44,55,44,50,51,44,51,52,44,51,49,44,50,51,44,50,56,44,49,54,44,49,56,44,50,49,39,125,125,40,119,105,110,100,111,119,41,59"}}')
    #cookies = {'RTYCID':'9e96ac1c50e3479196986b6eb99b48aa'}
    cookies = get_cookie(tongji_data,cookies)
    url = 'https://www.tianyancha.com/pagination/holder.xhtml?ps=20&pn=2&id=13157554'
    headers = {
    "Accept":"application/json, text/plain, */*",
    "Accept-Encoding":"gzip, deflate, br",
    "Accept-Language":"zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7",
    "Connection":"keep-alive",
    "Host":"www.tianyancha.com",
    'Referer':'https://www.tianyancha.com/company/13157554',
    "User-Agent":"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36" 
    }
    req = requests.get(url=url,headers=headers,cookies=cookies,verify=False)
    print req.text   
test()