# -*- coding: utf-8 -*-
# @Date    : 2018-03-23 10:46:21
# @Author  : jym
# @Description:
# @Version : v0.0
import requests
url = 'https://www.tianyancha.com/search/suggest.json?key=%E5%8C%97%E4%BA%AC%E5%B0%8F%E7%B1%B3%E7%94%B5%E5%AD%90%E4%BA%A7%E5%93%81%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B8&_=1521772958224'
headers = {
"Accept":"application/json, text/plain, */*",
"Accept-Encoding":"gzip, deflate, br",
"Accept-Language":"zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7",
"Connection":"keep-alive",
"User-Agent":"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36" 
}
req = requests.get(url=url,headers=headers,verify=False)
print req.text