#encoding:utf-8
#获取关系图的cookie
import requests
import json
import re

def get_disdata(compId):
    #https://dis.tianyancha.com/qq/13157554.json?
    url = 'https://dis.tianyancha.com/qq/%s.json?'%compId
    req = requests.get(url,verify=False)
    cookies = {}
    for item in req.cookies:
        cookies[item.name] = item.value
    dis_data = json.loads(req.text)
    return dis_data,cookies
def get_cookie(dis_data,cookies,compId):
    data = dis_data['data']['v'].split(",")
    fnStr = ""
    for char in data:
        fnStr += chr(int(char))
    print fnStr
    matchObj = re.match(r".*?token=(.*?);path=/;';n\.wtf=function\(\){return'(.*?)'}}\(window\);",fnStr)
    rtoken = matchObj.group(1)
    wtf_data = matchObj.group(2)
    wtf_data = wtf_data.split(",")
    chars = ""
    sgArr = [["6", "b", "t", "f", "2", "z", "l", "5", "w", "h", "q", "i", "s", "e", "c", "p", "m", "u", "9", "8", "y", "k", "j", "r", "x", "n", "-", "0", "3", "4", "d", "1", "a", "o", "7", "v", "g"],["1", "8", "o", "s", "z", "u", "n", "v", "m", "b", "9", "f", "d", "7", "h", "c", "p", "y", "2", "0", "3", "j", "-", "i", "l", "k", "t", "q", "4", "6", "r", "a", "w", "5", "e", "x", "g"],["s", "6", "h", "0", "p", "g", "3", "n", "m", "y", "l", "d", "x", "e", "a", "k", "z", "u", "f", "4", "r", "b", "-", "7", "o", "c", "i", "8", "v", "2", "1", "9", "q", "w", "t", "j", "5"],["x", "7", "0", "d", "i", "g", "a", "c", "t", "h", "u", "p", "f", "6", "v", "e", "q", "4", "b", "5", "k", "w", "9", "s", "-", "j", "l", "y", "3", "o", "n", "z", "m", "2", "1", "r", "8"],["z", "j", "3", "l", "1", "u", "s", "4", "5", "g", "c", "h", "7", "o", "t", "2", "k", "a", "-", "e", "x", "y", "b", "n", "8", "i", "6", "q", "p", "0", "d", "r", "v", "m", "w", "f", "9"],["j", "h", "p", "x", "3", "d", "6", "5", "8", "k", "t", "l", "z", "b", "4", "n", "r", "v", "y", "m", "g", "a", "0", "1", "c", "9", "-", "2", "7", "q", "e", "w", "u", "s", "f", "o", "i"],["8", "q", "-", "u", "d", "k", "7", "t", "z", "4", "x", "f", "v", "w", "p", "2", "e", "9", "o", "m", "5", "g", "1", "j", "i", "n", "6", "3", "r", "l", "b", "h", "y", "c", "a", "s", "0"],["d", "4", "9", "m", "o", "i", "5", "k", "q", "n", "c", "s", "6", "b", "j", "y", "x", "l", "a", "v", "3", "t", "u", "h", "-", "r", "z", "2", "0", "7", "g", "p", "8", "f", "1", "w", "e"],["7", "-", "g", "x", "6", "5", "n", "u", "q", "z", "w", "t", "m", "0", "h", "o", "y", "p", "i", "f", "k", "s", "9", "l", "r", "1", "2", "v", "4", "e", "8", "c", "b", "a", "d", "j", "3"]]
    r = str(ord((compId+"")[0]))
    if len(r)>1:
        r = r[1]
    r = int(r)
    print r
    chars = ""
    for char in wtf_data:
        char = int(char)
        #if char>=9 and char<=15:
        #    char = char - 3
        chars += sgArr[r][char] 
    utm = chars
    cookies['_rutm'] = utm
    cookies['rtoken'] = rtoken
    return cookies


def test():
    compId = "2353819702"
    dis_data,cookies = get_disdata(compId)
    #dis_data = {"state":"ok","message":"","special":"","vipMessage":"","isLogin":0,"data":{"name":"5517711","uv":0,"pv":0,"v":"33,102,117,110,99,116,105,111,110,40,110,41,123,100,111,99,117,109,101,110,116,46,99,111,111,107,105,101,61,39,114,116,111,107,101,110,61,99,100,97,55,98,55,55,48,56,53,102,57,52,48,98,53,97,55,100,51,50,101,100,56,49,52,49,97,99,52,101,53,59,112,97,116,104,61,47,59,39,59,110,46,119,116,102,61,102,117,110,99,116,105,111,110,40,41,123,114,101,116,117,114,110,39,49,57,44,50,50,44,51,44,51,52,44,55,44,49,51,44,49,57,44,50,56,44,49,51,44,55,44,49,50,44,49,55,44,49,55,44,50,44,51,54,44,49,50,44,50,50,44,50,44,49,53,44,49,56,44,49,55,44,51,44,50,56,44,49,56,44,54,44,49,55,44,49,51,44,49,50,44,50,56,44,51,51,44,49,50,44,51,52,39,125,125,40,119,105,110,100,111,119,41,59"}}
    #cookies = {}
    cookies = get_cookie(dis_data,cookies,compId)
    
    #print cookies
    url = 'https://dis.tianyancha.com/dis/getInfoById/%s.json?'%compId
    headers = {
    "Accept":"application/json, text/plain, */*",
    "Accept-Encoding":"gzip, deflate, br",
    "Accept-Language":"zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7",
    "Connection":"keep-alive",
    "User-Agent":"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36" 
    }
    req = requests.get(url=url,headers=headers,cookies=cookies,verify=False)
    print req.text
test()