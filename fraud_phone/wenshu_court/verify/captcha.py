#encoding:utf-8
from PIL import Image
import requests
import json
import time
#下载验证码图片
def get_pic(jpg_path):
    url = 'http://wenshu.court.gov.cn/waf_captcha/'
    req = requests.get(url,stream=True)
    if req.status_code == 200:
        with open(jpg_path,'wb') as f:
            for chunk in req.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    f.flush()
            f.close()
        wafcookie = req.cookies['wafcookie']
        return wafcookie
    else:
        time.sleep(20)
        get_pic(jpg_path)

#获取图片像素的哈希值
def get_pixelsHash(img_src):
    im = Image.open(img_src)
    width,height = im.size
    pixels = im.load()
    pixels_list = []
    for col in range(width):
        for row in range(height):
            pixels_list.append(pixels[col,row])
    return hash(hash(str(pixels_list)))

#读取图片像素哈希值数据库
def get_hash_dict(json_src):
    with open(json_src,'r') as f:
        hash_dict = json.load(f)
    return hash_dict

def get_keys(d, value):
    return [k for k,v in d.items() if v == value]

#根据图片判断其值
def get_key(img_src):
    pixels_hash = get_pixelsHash(img_src)
    hash_dict = get_hash_dict("YzmHash.json")
    keys = get_keys(hash_dict,pixels_hash)
    if not keys:
        return None
    else:
        return keys[0]

def verify():
    jpg_path = 'yzm.jpg'
    wafcookie = get_pic(jpg_path)
    key = get_key(jpg_path)
    url = 'http://wenshu.court.gov.cn/waf_verify.htm?captcha=%s'%key
    req = requests.get(url,cookies={'wafcookie':wafcookie})


