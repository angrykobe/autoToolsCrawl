#encoding:utf-8
import time
from PIL import ImageGrab,Image
import subprocess
import aircv as ac
import random
import pyautogui
import os
import requests
import sys
import json
sys.path.append("..")
from config import master_ip
class LoginAndValidate(object):
    """docstring for Login"""
    def __init__(self):
        self.login_url = 'http://www.qichacha.com/user_login'
        self.validate_url = 'www.qichacha.com/search?key=huawei'
        self.mapSearch_url = 'www.qichacha.com/map'
        self.chrome_path = '"C:\Program Files\Google\Chrome\Application\chrome.exe"'
        self.screenShot_path = 'validate\\1.jpg'
        self.userInfoShot_path_0 = 'validate\\2.jpg'
        self.userInfoShot_path_1 = 'validate\\2_1.jpg'
        self.slideLoginInitShot_path = 'validate\\3.jpg'
        self.slideLoginSucceedShot_path = 'validate\\4.jpg'
        self.slideValidateInitShot_path = 'validate\\7.jpg'
        self.slideValidateSucceedShot_path = 'validate\\8.jpg'
        self.submitLoginShot_path = 'validate\\5.jpg'
        self.submitLoginShot_path_01 = 'validate\\5_1.jpg'
        self.submitValidateShot_path = 'validate\\6.jpg' 
        self.dragBtnShot_path_01 = 'validate\\9.jpg'
        self.dragBtnShot_path_02 = 'validate\\10.jpg'
        self.mimaLoginShot_path = 'validate\\11.jpg'
        self.logoShot_path = 'validate\\12.jpg'
        self.checkValidateShot_path = 'validate\\13.jpg'
        self.checkValidateShot_path_01 = 'validate\\13_1.jpg'
    #最大化窗口
    def maxiChrome(self):
        time.sleep(2)
        pyautogui.hotkey('alt','space','x')

    #打开标签页
    def openChromeTab(self,url=None):
        pyautogui.hotkey('ctrl','d')
        if url:
            subprocess.Popen('%s %s'%(self.chrome_path,url))
        else:
            subprocess.Popen('%s'%(self.chrome_path))
    
    #关闭标签页
    def closeChromeTab(self):
        pyautogui.hotkey('ctrl','f4')
    
    #关闭整个chrome
    def closeChrome(self):
        pyautogui.hotkey('alt','f4')
    
    def refreshChrome(self):
        pyautogui.hotkey('f5')
    
    def shotScreen(self):
        im = pyautogui.screenshot(self.screenShot_path)
    
    def matchImg(self,imgsrc,imgobj,confidencevalue=0.5):#imgsrc=原始图像，imgobj=待查找的图片
        imsrc = ac.imread(imgsrc)
        imobj = ac.imread(imgobj)   
        match_result = ac.find_template(imsrc,imobj,confidencevalue)  # {'confidence': 0.5435812473297119, 'rectangle': ((394, 384), (394, 416), (450, 384), (450, 416)), 'result': (422.0, 400.0)}
        if not match_result:
            match_result['shape']=(imsrc.shape[1],imsrc.shape[0])#0为高，1为宽
            return match_result['rectangle']
        else:
            return None

    def _drawCircle(self):
        self.shotScreen()
        rect = self.matchImg(self.screenShot_path,self.dragBtnShot_path_01)
        pyautogui.moveTo((rect[0][0]+3*rect[2][0])/4,(rect[0][1]+rect[1][1])/2)
        pyautogui.click()
        pyautogui.moveRel(250,250,duration=1)
        pyautogui.dragRel(100,100,duration=3)

    def _checkDrawCircle(self):
        self.shotScreen()
        rect2 = self.matchImg(self.screenShot_path,self.logoShot_path)
        if rect2:
            return False
        else:
            return True

    def drawCircle(self):
        self._drawCircle()
        time.sleep(2)
        ret = self._checkDrawCircle()
        self.refreshChrome()
        return ret


    def _clickLoginStyle(self):
        rect = self.matchImg(self.screenShot_path,self.mimaLoginShot_path)
        pyautogui.click((rect[0][0]+rect[2][0])/2,(rect[0][1]+rect[1][1])/2) 

    def _typewrite(self,x,y,msg):
        pyautogui.click(x,y)
        pyautogui.hotkey('ctrl','a')
        pyautogui.press('backspace')
        pyautogui.typewrite(msg)        
    
    def typeUserInfo(self,userInfo):
        rect = self.matchImg(self.screenShot_path,self.userInfoShot_path_0)
        if rect == None:
            rect = self.matchImg(self.screenShot_path,self.userInfoShot_path_1)
        #输入用户名
        x, y = rect[2][0] - 20, rect[2][1] + 5
        self._typewrite(x, y, userInfo['user'])
        #输入密码
        x, y = rect[1][0] + 20, rect[1][1] + 5
        self._typewrite(x, y, userInfo['pwd'])

    def _dragCapture(self,captureShot_path):
        rect = self.matchImg(self.screenShot_path,captureShot_path)
        dis = rect[2][0] - rect[0][0] - 40 +10
        pyautogui.moveTo(rect[0][0] + 20, (rect[0][1] + rect[1][1])/2)
        pyautogui.dragRel(dis,1,3)

    #拖动登录验证码
    def dragCaptureLogin(self):
        self._dragCapture(self.slideLoginInitShot_path)
    
    #拖动验证验证码
    def dragCaptureValidate(self):
        self._dragCapture(self.slideValidateInitShot_path)
    
    #判断是否验证成功
    def checkValidate(self):
        self.shotScreen()
        rect1 = self.matchImg(self.screenShot_path,self.checkValidateShot_path,confidencevalue=0.8)
        rect2 = self.matchImg(self.screenShot_path,self.checkValidateShot_path_01,confidencevalue=0.8)
        if rect1:
            return 0 #验证成功
        if rect2:
            return 1 #拖动未完成，通过刷新页面重新开始
        return -1 #出现了验证码

    def checkLogoin(self):
        self.shotScreen()
        captureRec = self.matchImg(self.screenShot_path,self.logoShot_path,confidencevalue=0.8)
        if captureRec:
            return True
        else:
            return False

    #点击登录按钮
    def submitLogin(self):
        rect = self.matchImg(self.screenShot_path,self.submitLoginShot_path,confidencevalue=0.5)
        if rect:
            rect = self.matchImg(self.screenShot_path,self.submitLoginShot_path_01,confidencevalue=0.5)
        pyautogui.click((rect[0][0]+rect[2][0])/2,(rect[0][1]+rect[2][1])/2+5)

    #点击登录按钮
    def submitValidate(self):
        rect = self.matchImg(self.screenShot_path,self.submitValidateShot_path,confidencevalue=0.5)
        pyautogui.click((rect[0][0]+rect[2][0])/2,(rect[0][1]+rect[2][1])/2+5)

    #退出登录的状态的方法为直接删除chrome的cookies文件
    def logout(self):
        cookies_path = 'C:\Users\Administrator\AppData\Local\Google\Chrome\User Data\Default\Cookies'
        try:
            os.remove(cookies_path)
        except Exception,e:
            pass
    def login(self,userInfo):
        loginSucceed = False
        self.openChromeTab()
        time.sleep(1)
        self.maxiChrome()
        time.sleep(1)
        self.closeChrome()
        self.logout()
        self.openChromeTab(self.login_url)
        time.sleep(1)
        pyautogui.hotkey('esc')
        time.sleep(10)
        self.shotScreen()
        self._clickLoginStyle()
        self.typeUserInfo(userInfo)
        maxRetries = 5
        for _ in range(maxRetries):
            self.dragCaptureLogin()
            time.sleep(1)
            self.submitLogin()
            time.sleep(5)
            if self.checkLogoin():        
                loginSucceed = True
                break
        return loginSucceed
    def validate(self):
        validateSucceed = False
        self.openChromeTab(self.validate_url)
        time.sleep(5)
        self.shotScreen()
        maxRetries = 5
        for _ in range(maxRetries):
            try:
                self.dragCaptureValidate()
                self.submitValidate()
                ret = self.checkValidate()
                if ret == 0:
                    validateSucceed = True
                    break
                elif ret == 1:
                    validateSucceed = False
                    self.refreshChrome()
                    time.sleep(5)
                else:
                    validateSucceed = False
                    break
            except:
                validateSucceed = False
                break
                
        self.closeChromeTab()     
        return validateSucceed
