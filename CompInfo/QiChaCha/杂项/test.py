#encoding:utf-8
import requests

url = 'https://www.qixin.com/api/enterprise/getTrademarkList'
data = {"eid":"4c8bd41b-2534-43c0-8643-5bf4dca1991e","page":8}
headers = {
    'Host': 'www.qixin.com',
    'Connection': 'keep-alive',
    'Accept': 'application/json, text/plain, */*',
    'Origin': 'https://www.qixin.com',
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
    'Content-Type': 'application/json;charset=UTF-8',
    'Referer': 'https://www.qixin.com/company-ability/4c8bd41b-2534-43c0-8643-5bf4dca1991e',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
    'Cookie':'Hm_lvt_52d64b8d3f6d42a2e416d59635df3f71=1518163416,1519711717,1519722512; cookieShowLoginTip=1; sid=s%3AD9mscBb2J84wqS4UeSIG6_-elUnbPsrU.Xmtki04%2BrcM5sv7iTJBMqGKuvfsl33OiyO3O3rS48Jo; Hm_lpvt_52d64b8d3f6d42a2e416d59635df3f71=1519722560; _zg=%7B%22uuid%22%3A%20%22161799750708d2-0cd9398d6033f5-393d5f0e-13c680-16179975071e7d%22%2C%22sid%22%3A%201519722511.32%2C%22updated%22%3A%201519722559.754%2C%22info%22%3A%201519711717175%2C%22cuid%22%3A%20%22e6ad9b42-7917-480e-ba12-e350885ba8d7%22%7D; responseTimeline=210'
    }
req = requests.post(url,params=data,headers=headers,verify=False)
print req.text
