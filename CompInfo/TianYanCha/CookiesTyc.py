# -*- coding: utf-8 -*-
# @Date    : 2018-03-23 10:54:51
# @Author  : jym
# @Description:获取天眼查相关的cookie
# @Version : v0.0
import json
import re
import requests
import time
from util.util import retry,delCookies
from util.AdslCtl import AdslCtl
class CookiesTyc(object):
    def __init__(self):
        self.cookie_pagination = {}
        self.cookie_dis = {}
        self.adsl = AdslCtl()
    def reconnect(self):
        delCookies()
        self.adsl.reconnect()
    def get_rsid(self,compName):
        r = str(ord(compName[0]))
        if len(r)>1:
            r = int(r[1])
        else:
            r = int(r)
        _0x4fec = "f9D1x1Z2o1U2f5A1a1P1i7R1u2S1m1F1,o2A1x2F1u5~j1Y2z3!p2~r3G2m8S1c1,i3E5o1~d2!y2H1e2F1b6`g4v7,p1`t7D3x5#w2~l2Z1v4Y1k4M1n1,C2e3P1r7!s6U2n2~p5X1e3#,g4`b6W1x4R1r4#!u5!#D1f2,!z4U1f4`f2R2o3!l4I1v6F1h2F1x2!,b2~u9h2K1l3X2y9#B4t1,t5H1s7D1o2#p2#z1Q3v2`j6,r1#u5#f1Z2w7!r7#j3S1";
        i = self.rs_decode(r)
        o = _0x4fec.split(",")[r]
        a = []
        s = 0
        for u in range(len(o)):
            if "`" != o[u] and "!" != o[u] and "~" != o[u]:
                pass
            else:
                a.append(i[s])
                s += 1
            if "#" == o[u]:
                a.append(i[s])
                a.append(i[s+1:s+3])
                a.append(i[s+3:s+4])
                s += 4
            if ord(o[u]) > 96 and ord(o[u]) < 123:
                for c in range(int(o[u+1])):
                    a.append(i[s:s+2])
                    s += 2
            if ord(o[u]) > 64 and ord(o[u]) < 91:
                for c in range(int(o[u+1])):
                    a.append(i[s:s+1])
                    s += 1
        return a
    def rs_decode(self,e):
        P = "2633141825201321121345332721524273528936811101916293117022304236|1831735156281312241132340102520529171363214283321272634162219930|2332353860219720155312141629130102234183691124281413251227261733|2592811262018293062732141927100364232411333831161535317211222534|9715232833130331019112512913172124126035262343627321642220185148|3316362031032192529235212215274341412306269813312817111724201835|3293412148301016132183119242311021281920736172527353261533526224|3236623313013201625221912357142415851018341117262721294332103928|2619332514511302724163415617234183291312001227928218353622321031|3111952725113022716818421512203433241091723133635282932601432216"
        return P.split("|")[e]

    
    #获取详情页时用到的cookie
    @retry(exceptions=(Exception,), max_retries=2, interval=5,retry_func="reconnect")
    def cookies_pagination(self,compName):
        url = 'https://www.tianyancha.com/tongji/%s.json?'%(compName)
        req = requests.get(url,verify = False)
        for item in req.cookies:
            self.cookie_pagination[item.name] = item.value
        data = json.loads(req.text)['data'].split(",")
        fnStr = ""
        for char in data:
            fnStr += chr(int(char))
        matchObj = re.match(r".*?token=(.*?);path=/;';n\.wtf=function\(\){return'(.*?)'}}\(window\);",fnStr)
        token = matchObj.group(1)
        self.cookie_pagination['token'] = token
        
        wtf_data = matchObj.group(2)     
        chars = ""
        base64chars = "abcdefghijklmnopqrstuvwxyz1234567890-~!"
        rsid = self.get_rsid(compName)
        for i in range(len(rsid)):
            chars += base64chars[int(rsid[i])]
        fxckStr = ""
        fxck = wtf_data.split(",")
        for i in range(len(fxck)):
            fxckStr += chars[int(fxck[i])]
        utm = fxckStr
        self.cookie_pagination['_utm'] = utm
        return self.cookie_pagination

    #获取图谱时需要用到的cookie
    @retry(exceptions=(Exception,), max_retries=2, interval=5,retry_func="delCookies")
    def cookies_dis(self,compId):
        url = 'https://dis.tianyancha.com/qq/%s.json?'%compId
        req = requests.get(url,verify=False)
        cookies = {}
        for item in req.cookies:
            cookies[item.name] = item.value
        data = json.loads(req.text)['data']['v'].split(",")
        for item in req.cookies:
            self.cookie_dis[item.name] = item.value
        fnStr = ""
        for char in data:
            fnStr += chr(int(char))
        matchObj = re.match(r".*?token=(.*?);path=/;';n\.wtf=function\(\){return'(.*?)'}}\(window\);",fnStr)
        rtoken = matchObj.group(1)
        wtf_data = matchObj.group(2)
        wtf_data = wtf_data.split(",")
        chars = ""
        sgArr = [["6", "b", "t", "f", "2", "z", "l", "5", "w", "h", "q", "i", "s", "e", "c", "p", "m", "u", "9", "8", "y", "k", "j", "r", "x", "n", "-", "0", "3", "4", "d", "1", "a", "o", "7", "v", "g"],["1", "8", "o", "s", "z", "u", "n", "v", "m", "b", "9", "f", "d", "7", "h", "c", "p", "y", "2", "0", "3", "j", "-", "i", "l", "k", "t", "q", "4", "6", "r", "a", "w", "5", "e", "x", "g"],["s", "6", "h", "0", "p", "g", "3", "n", "m", "y", "l", "d", "x", "e", "a", "k", "z", "u", "f", "4", "r", "b", "-", "7", "o", "c", "i", "8", "v", "2", "1", "9", "q", "w", "t", "j", "5"],["x", "7", "0", "d", "i", "g", "a", "c", "t", "h", "u", "p", "f", "6", "v", "e", "q", "4", "b", "5", "k", "w", "9", "s", "-", "j", "l", "y", "3", "o", "n", "z", "m", "2", "1", "r", "8"],["z", "j", "3", "l", "1", "u", "s", "4", "5", "g", "c", "h", "7", "o", "t", "2", "k", "a", "-", "e", "x", "y", "b", "n", "8", "i", "6", "q", "p", "0", "d", "r", "v", "m", "w", "f", "9"],["j", "h", "p", "x", "3", "d", "6", "5", "8", "k", "t", "l", "z", "b", "4", "n", "r", "v", "y", "m", "g", "a", "0", "1", "c", "9", "-", "2", "7", "q", "e", "w", "u", "s", "f", "o", "i"],["8", "q", "-", "u", "d", "k", "7", "t", "z", "4", "x", "f", "v", "w", "p", "2", "e", "9", "o", "m", "5", "g", "1", "j", "i", "n", "6", "3", "r", "l", "b", "h", "y", "c", "a", "s", "0"],["d", "4", "9", "m", "o", "i", "5", "k", "q", "n", "c", "s", "6", "b", "j", "y", "x", "l", "a", "v", "3", "t", "u", "h", "-", "r", "z", "2", "0", "7", "g", "p", "8", "f", "1", "w", "e"],["7", "-", "g", "x", "6", "5", "n", "u", "q", "z", "w", "t", "m", "0", "h", "o", "y", "p", "i", "f", "k", "s", "9", "l", "r", "1", "2", "v", "4", "e", "8", "c", "b", "a", "d", "j", "3"]]
        r = str(ord((compId+"")[0]))
        if len(r)>1:
            r = r[0]
        r = int(r)
        chars = ""
        for char in wtf_data:
            char = int(char)
            chars += sgArr[r][char] 
        utm = chars
        self.cookie_dis['_rutm'] = utm
        self.cookie_dis['rtoken'] = rtoken
        return self.cookie_dis
if __name__ == '__main__':
    tyc_cookie = CookiesTyc()
    tyc_cookie.cookies_dis('198158709')