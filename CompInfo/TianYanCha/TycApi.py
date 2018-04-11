# -*- coding: utf-8 -*-
# @Date    : 2018-03-23 15:03:43
# @Author  : jym
# @Description:获取天眼查信息的相关接口
# @Version : v0.0
import requests
import json
from bs4 import BeautifulSoup
from CookiesTyc import CookiesTyc
from util.util import merge_gen,retry,delCookies
from util.AdslCtl import AdslCtl
import time
class TianYanCha(object):
    def __init__(self):
        self.cookies_tyc = CookiesTyc()
        self.headers = {
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
        }
        self.adsl = AdslCtl()
    def reconnect(self):
        delCookies()
        self.adsl.reconnect()          
    def wait(self):
        time.sleep(15)
    #根据公司名获取该公司在天眼查中的id
    @retry(exceptions=(Exception,), max_retries=-1, interval=5,retry_func="reconnect")
    def _get_id_tyc(self,compName):
        id_tyc = None
        url = 'https://www.tianyancha.com/deepSearch.json?word=%s'%compName
        req = requests.get(url=url,headers=self.headers,verify=False)
        json_data = json.loads(req.text)
        if json_data['state'] == 'ok':
            for item in json_data['data']:
                comp_id,comp_name = str(item['id']),item['name'].replace('<em>','').replace('</em>','')
                if comp_name == compName:
                    id_tyc = comp_id
        return id_tyc    

    #获取图谱信息 
    def _get_dis(self,id_tyc,url): 
        cookies = self.cookies_tyc.cookies_dis(id_tyc)
        req = requests.get(url=url,headers=self.headers,cookies=cookies,verify=False)
        json_data = json.loads(req.text)
        if json_data['state'] == 'ok':
            return json_data['data']
        return None

    #获取历史沿革图
    def get_timeline(self,id_tyc):
        url = 'https://dis.tianyancha.com/dis/timeline.json?id=%s'%id_tyc
        return self._get_dis(id_tyc,url)

    #获取关系图
    def get_relationship(self,id_tyc):
        url = 'https://dis.tianyancha.com/dis/getInfoById/%s.json?'%id_tyc
        return self._get_dis(id_tyc,url)

    #获取工商信息
    #暂不考虑实现，具体信息从企查查地图部分接口获取
    def _get_compBaseInfo(self,id_tyc):
        pass


    #以table形式生成的表格解析
    def _parse_table_01(self,soup):
        head_tags = soup.find('thead').find('tr').findAll('th')
        data = []
        headers = []
        for item in head_tags:
            headers.append(item.text)
        tr_tags = soup.find('tbody').findAll('tr')
        for tr_tag in tr_tags:
            info = {}
            td_tags = tr_tag.findAll('td')
            for i in range(len(td_tags)):
                info[headers[i]] = {}
                info[headers[i]]['value'] = td_tags[i].text.split(u"他有")[0]
                for item in td_tags[i].descendants:
                    try:
                        if item.has_attr('href'):
                            info[headers[i]]['href'] = item['href']
                            break
                    except Exception,e:
                        pass
            data.append(info)
        try:
            total_page = int(soup.find('div',class_='total').text[1:-1])
        except Exception,e:
            total_page = 1
        return data,total_page

    #以div形式生成的表格解析
    def _parse_table_02(self,soup):
        data = []
        for item in soup.find('div',class_='clearfix').children:
            info = {}
            name = item.find('a').text
            header = item.find('a').previous_sibling.text
            info["header"] = header
            info["name"] = name
            try:
                href = item.find('a')['href']
                info["href"] = href
            except Exception,e:
                pass
            data.append(info)
        try:
            total_page = int(soup.find('div',class_='total').text[1:-1])
        except Exception,e:
            total_page = 1
        return data,total_page

    #网页表格解析
    def _parse_table(self,soup):
        if soup.find('thead'):
            data,total_page = self._parse_table_01(soup)
        else:
            data,total_page = self._parse_table_02(soup)
        return data,total_page


    #@retry(exceptions=(Exception,), max_retries=2, interval=5,retry_func="reconnect")
    @retry(exceptions=(Exception,), max_retries=3, interval=5,retry_func="wait")
    def _pagination_api(self,base_url,compName,id_tyc=None,ps=20,pn=1,):
        if id_tyc == None:
            id_tyc = self._get_id_tyc(compName)
        info_type = base_url.split('/')[-1].split('.')[0]
        if info_type in ['rongzi',  'jingpin','touzi',  'lawsuit','court',
                        'dishonest','punish', 'illegal','equity', 'mortgage',
                        'purchaseland','bond','recruit', 'taxCredit','check',
                        ]:
            url = base_url + 'ps=%d&pn=%d&name=%s'%(ps,pn,compName)
        else:
            url = base_url + 'ps=%d&pn=%d&id=%s'%(ps,pn,id_tyc)
        cookies = self.cookies_tyc.cookies_pagination(compName)
        req = requests.get(url=url,headers=self.headers,cookies=cookies,verify=False)
        if req.text in ['','<div></div>','Unauthorized']:
            return None,None
        soup = BeautifulSoup(req.text,'lxml')
        if soup.find('title') and soup.title.text in [u'访问禁止','403 Forbidden']:
            raise Exception
        return self._parse_table(soup)

    def _get_pagination(self,base_url,compName,id_tyc,ps=100,pn=1):
        data_list = []
        if id_tyc == None:
            id_tyc = self._get_id_tyc(compName)
        try:
            ret = self._pagination_api(base_url,compName,id_tyc,ps,pn)
            data,total_page = ret
        except Exception,e:
            return data_list
        if data == total_page == None:
            return []
        data_list.extend(data)

        for pn in range(2,total_page+1):
            try:
                ret = self._pagination_api(base_url,compName,id_tyc,ps,pn)
                data,total_page = ret
                data_list.extend(data)
            except Exception,e:
                break            
        return data_list
    #获取对外投资信息
    def get_invest(self,compName,id_tyc=None,ps=100,pn=1):
        base_url = 'https://www.tianyancha.com/pagination/invest.xhtml?'
        return self._get_pagination(base_url,compName,id_tyc,ps,pn)
    #获取主要人员
    def get_staff(self,compName,id_tyc=None,ps=100,pn=1):
        base_url = 'https://www.tianyancha.com/pagination/staff.xhtml?'
        return self._get_pagination(base_url,compName,id_tyc,ps,pn)

    #获取股东信息
    def get_holders(self,compName,id_tyc=None,ps=100,pn=1):
        base_url = 'https://www.tianyancha.com/pagination/holder.xhtml?'
        return self._get_pagination(base_url,compName,id_tyc,ps,pn)
    #获取变更信息
    def get_changeinfo(self,compName,id_tyc=None,ps=100,pn=1):
        base_url = 'https://www.tianyancha.com/pagination/changeinfo.xhtml?'
        return self._get_pagination(base_url,compName,id_tyc,ps,pn)
    #获取分支信息
    def get_branch(self,compName,id_tyc=None,ps=100,pn=1):
        base_url = 'https://www.tianyancha.com/pagination/branch.xhtml?'
        return self._get_pagination(base_url,compName,id_tyc,ps,pn)

    #获取融资信息
    def get_rongzi(self,compName,id_tyc=None,ps=100,pn=1):
        base_url = 'https://www.tianyancha.com/pagination/rongzi.xhtml?'
        return self._get_pagination(base_url,compName,id_tyc,ps,pn)

    #获取竞品信息
    def get_jingpin(self,compName,id_tyc=None,ps=100,pn=1):
        base_url = 'https://www.tianyancha.com/pagination/jingpin.xhtml?'
        return self._get_pagination(base_url,compName,id_tyc,ps,pn)

    #获取投资事件信息
    def get_touzi(self,compName,id_tyc=None,ps=100,pn=1):
        base_url = 'https://www.tianyancha.com/pagination/touzi.xhtml?'
        return self._get_pagination(base_url,compName,id_tyc,ps,pn)  

    #获取法律诉讼信息
    def get_lawsuit(self,compName,id_tyc=None,ps=100,pn=1):
        base_url = 'https://www.tianyancha.com/pagination/lawsuit.xhtml?'
        return self._get_pagination(base_url,compName,id_tyc,ps,pn)  

    #获取法院公告信息
    def get_court(self,compName,id_tyc=None,ps=100,pn=1):
        base_url = 'https://www.tianyancha.com/pagination/court.xhtml?'
        return self._get_pagination(base_url,compName,id_tyc,ps,pn)  

    #获取开庭公告信息
    def get_announcementcourt(self,compName,id_tyc=None,ps=100,pn=1):
        base_url = 'https://www.tianyancha.com/pagination/announcementcourt.xhtml?'
        return self._get_pagination(base_url,compName,id_tyc,ps,pn)  

    #获取失信人信息
    def get_dishonest(self,compName,id_tyc=None,ps=100,pn=1):
        base_url = 'https://www.tianyancha.com/pagination/dishonest.xhtml?'
        return self._get_pagination(base_url,compName,id_tyc,ps,pn)  

    #获取被执行人
    def get_zhixing(self,compName,id_tyc=None,ps=100,pn=1):
        base_url = 'https://www.tianyancha.com/pagination/zhixing.xhtml?'
        return self._get_pagination(base_url,compName,id_tyc,ps,pn)  

    #获取经营异常信息
    def get_abnormal(self,compName,id_tyc=None,ps=100,pn=1):
        base_url = 'https://www.tianyancha.com/pagination/abnormal.xhtml?'
        return self._get_pagination(base_url,compName,id_tyc,ps,pn) 

    #获取行政处罚信息
    def get_punish(self,compName,id_tyc=None,ps=100,pn=1):
        base_url = 'https://www.tianyancha.com/pagination/punish.xhtml?'
        return self._get_pagination(base_url,compName,id_tyc,ps,pn) 

    #获取严重违法信息
    def get_illegal(self,compName,id_tyc=None,ps=100,pn=1):
        base_url = 'https://www.tianyancha.com/pagination/illegal.xhtml?'
        return self._get_pagination(base_url,compName,id_tyc,ps,pn) 

    #获取股权出质信息
    def get_equity(self,compName,id_tyc=None,ps=100,pn=1):
        base_url = 'https://www.tianyancha.com/pagination/equity.xhtml?'
        return self._get_pagination(base_url,compName,id_tyc,ps,pn) 

    #获取动产抵押信息
    def get_mortgage(self,compName,id_tyc=None,ps=100,pn=1):
        base_url = 'https://www.tianyancha.com/pagination/mortgage.xhtml?'
        return self._get_pagination(base_url,compName,id_tyc,ps,pn) 

    #获取欠税公告信息
    def get_townTax(self,compName,id_tyc=None,ps=100,pn=1):
        base_url = 'https://www.tianyancha.com/pagination/towntax.xhtml?'
        return self._get_pagination(base_url,compName,id_tyc,ps,pn) 

    #获取司法拍卖信息
    def get_judicialSale(self,compName,id_tyc=None,ps=100,pn=1):
        base_url = 'https://www.tianyancha.com/pagination/judicialSale.xhtml?'
        return self._get_pagination(base_url,compName,id_tyc,ps,pn) 

    #获取招投标信息
    def get_bid(self,compName,id_tyc=None,ps=100,pn=1):
        base_url = 'https://www.tianyancha.com/pagination/bid.xhtml?'
        return self._get_pagination(base_url,compName,id_tyc,ps,pn) 
    
    #获取债券信息
    def get_bond(self,compName,id_tyc=None,ps=100,pn=1):
        base_url = 'https://www.tianyancha.com/pagination/bond.xhtml?'
        return self._get_pagination(base_url,compName,id_tyc,ps,pn) 

    #获取购地信息
    def get_purchaseland(self,compName,id_tyc=None,ps=100,pn=1):
        base_url = 'https://www.tianyancha.com/pagination/purchaseland.xhtml?'
        return self._get_pagination(base_url,compName,id_tyc,ps,pn) 
    
    #获取购地信息
    def get_recruit(self,compName,id_tyc=None,ps=100,pn=1):
        base_url = 'https://www.tianyancha.com/pagination/recruit.xhtml?'
        return self._get_pagination(base_url,compName,id_tyc,ps,pn) 

    #获取税务评级信息
    def get_taxCredit(self,compName,id_tyc=None,ps=100,pn=1):
        base_url = 'https://www.tianyancha.com/pagination/taxcredit.xhtml?'
        return self._get_pagination(base_url,compName,id_tyc,ps,pn) 

    #获取抽查检查信息
    def get_check(self,compName,id_tyc=None,ps=100,pn=1):
        base_url = 'https://www.tianyancha.com/pagination/check.xhtml?'
        return self._get_pagination(base_url,compName,id_tyc,ps,pn) 

    #获取产品信息
    def get_product(self,compName,id_tyc=None,ps=100,pn=1):
        base_url = 'https://www.tianyancha.com/pagination/product.xhtml?'
        return self._get_pagination(base_url,compName,id_tyc,ps,pn) 

    #获取进出口信用
    def get_importAndExport(self,compName,id_tyc=None,ps=100,pn=1):
        base_url = 'https://www.tianyancha.com/pagination/importAndExport.xhtml?'
        return self._get_pagination(base_url,compName,id_tyc,ps,pn) 

    #获取资质证书
    def get_certificate(self,compName,id_tyc=None,ps=100,pn=1):
        base_url = 'https://www.tianyancha.com/pagination/certificate.xhtml?'
        return self._get_pagination(base_url,compName,id_tyc,ps,pn) 

    #获取商标信息
    def get_tminfo(self,compName,id_tyc=None,ps=100,pn=1):
        base_url = 'https://www.tianyancha.com/pagination/tmInfo.xhtml?'
        return self._get_pagination(base_url,compName,id_tyc,ps,pn)    

    #获取专利信息
    def get_patent(self,compName,id_tyc=None,ps=100,pn=1):
        base_url = 'https://www.tianyancha.com/pagination/patent.xhtml?'
        return self._get_pagination(base_url,compName,id_tyc,ps,pn)    

    #获取软件著作权信息
    def get_copyright(self,compName,id_tyc=None,ps=100,pn=1):
        base_url = 'https://www.tianyancha.com/pagination/copyright.xhtml?'
        return self._get_pagination(base_url,compName,id_tyc,ps,pn)   

    #获取作品著作权
    def get_copyrightWorks(self,compName,id_tyc=None,ps=100,pn=1):
        base_url = 'https://www.tianyancha.com/pagination/copyrightWorks.xhtml?'
        return self._get_pagination(base_url,compName,id_tyc,ps,pn)   

    #获取网站备案信息
    def get_icp(self,compName,id_tyc=None,ps=100,pn=1):
        base_url = 'https://www.tianyancha.com/pagination/icp.xhtml?'
        return self._get_pagination(base_url,compName,id_tyc,ps,pn)   



    #获取微信公众号
    @retry(exceptions=(Exception,), max_retries=-1, interval=5,retry_func="reconnect")
    @retry(exceptions=(Exception,), max_retries=3, interval=5,retry_func="wait")
    def _get_wechat(self,compName,id_tyc=None,ps=100,pn=1):
        if id_tyc == None:
            id_tyc = self._get_id_tyc(compName)
        base_url = 'https://www.tianyancha.com/pagination/wechat.xhtml?'
        url = base_url + 'ps=%d&pn=%d&id=%s'%(ps,pn,id_tyc)
        cookies = self.cookies_tyc.cookies_pagination(compName)
        req = requests.get(url=url,headers=self.headers,cookies=cookies,verify=False)
        if req.text in ['','<div></div>','Unauthorized']:
           return [],0

        soup = BeautifulSoup(req.text,'lxml')
        if soup.find('title') and soup.title.text in [u'访问禁止','403 Forbidden']:
            raise Exception
        data = []
        for item in soup.find('div',attrs=['wechat', 'clearfix']):
            info = {}
            title_tag = item.find('span',text=u'微信号:')
            info["wechatNum"] = title_tag.next_sibling.text
            info["title"] = title_tag.parent.previous_sibling.text
            info["desc"] = title_tag.parent.next_sibling.text
            data.append(info)

        try:
            total_page = int(soup.find('div',class_='total').text[1:-1])
        except Exception,e:
            total_page = 1
        return data,total_page


    def get_wechat(self,compName,id_tyc=None,ps=100,pn=1):
        if id_tyc == None:
            id_tyc = self._get_id_tyc(compName)
        data_list = []
        try:
            ret = self._get_wechat(compName,id_tyc,ps,pn)
        except Exception,e:
            return data_list
        data,total_page = ret
        data_list.extend(data)
        if total_page>1:
            for pn in range(2,total_page+1):
                try:
                    ret = self._get_wechat(compName,id_tyc,ps,pn)
                    data,total_page = ret
                    data_list.extend(data)
                except Exception,e:
                    break
        return data_list


    #获取企业业务信息
    @retry(exceptions=(Exception,), max_retries=-1, interval=5,retry_func="reconnect")
    @retry(exceptions=(Exception,), max_retries=3, interval=5,retry_func="wait")
    def _get_firmProduct(self,compName,id_tyc=None,ps=100,pn=1):
        if id_tyc == None:
            id_tyc = self._get_id_tyc(compName)
        base_url = 'https://www.tianyancha.com/pagination/firmProduct.xhtml?'
        url = base_url + 'ps=%d&pn=%d&name=%s'%(ps,pn,compName)
        cookies = self.cookies_tyc.cookies_pagination(compName)
        req = requests.get(url=url,headers=self.headers,cookies=cookies,verify=False)
        if req.text in ['','<div></div>','Unauthorized']:
            return [],0
        soup = BeautifulSoup(req.text,'lxml')
        if soup.find('title') and soup.title.text in [u'访问禁止','403 Forbidden']:
            raise Exception
        data = []
        for item in soup.findAll('div',class_='product-item'):
            info = {}
            info["title"] = item.find('span',class_='title').text
            info["industry"] = item.find('div',class_='hangye').text
            info["desc"] = item.find('div',class_='yeweu overflow-width').text
            data.append(info)
        try:
            total_page = int(soup.find('div',class_='total').text[1:-1])
        except Exception,e:
            total_page = 1
        return data,total_page
    #获取企业业务信息
    def get_firmProduct(self,compName,id_tyc=None,ps=100,pn=1):
        if id_tyc == None:
            id_tyc = self._get_id_tyc(compName)
        data_list = []
        try:
            ret = self._get_firmProduct(compName,id_tyc,ps,pn)
        except Exception,e:
            return data_list 
        data,total_page = ret
        data_list.extend(data)
        if total_page>1:
            for pn in range(2,total_page+1):
                try:
                    ret = self._get_firmProduct(compName,id_tyc,ps,pn)
                    data,total_page = ret
                    data_list.extend(data)
                except Exception,e:
                    break
        return data_list     

    #获取核心团队信息
    @retry(exceptions=(Exception,), max_retries=-1, interval=5,retry_func="reconnect")
    @retry(exceptions=(Exception,), max_retries=3, interval=5,retry_func="wait")
    def _get_teamMember(self,compName,id_tyc=None,ps=100,pn=1):
        if id_tyc == None:
            id_tyc = self._get_id_tyc(compName)
        base_url = 'https://www.tianyancha.com/pagination/teamMember.xhtml?'
        url = base_url + 'ps=%d&pn=%d&name=%s'%(ps,pn,compName)
        cookies = self.cookies_tyc.cookies_pagination(compName)
        req = requests.get(url=url,headers=self.headers,cookies=cookies,verify=False)
        if req.text in ['','<div></div>','Unauthorized']:
            return [],0
        soup = BeautifulSoup(req.text,'lxml')
        if soup.find('title') and soup.title.text in [u'访问禁止','403 Forbidden']:
            raise Exception
        data = []
        for item in soup.findAll('div','team-item'):
            info = {}
            info["name"] = item.find('div','team-name').text
            info["title"] = item.find('div','team-title').text
            desc = []
            try:
                desc = []
                for li_tag in item.find('ul').findAll('li'):
                    desc.append(li_tag.text)
                info["desc"] = desc
            except Exception,e:
                info["desc"] = []
            data.append(info)

        try:
            total_page = int(soup.find('div',class_='total').text[1:-1])
        except Exception,e:
            total_page = 1
        return data,total_page

    def get_teamMember(self,compName,id_tyc=None,ps=100,pn=1):
        if id_tyc == None:
            id_tyc = self._get_id_tyc(compName)
        data_list = []
        try:
            ret = self._get_teamMember(compName,id_tyc,ps,pn)
        except Exception,e:
            return data_list
        data,total_page = ret
        data_list.extend(data)
        if total_page>1:
            for pn in range(2,total_page+1):
                try:
                    ret = self._get_teamMember(compName,id_tyc,ps,pn)
                    data,total_page = ret
                    data_list.extend(data)
                except Exception,e:
                    break
        return data_list  

    #获取所有信息
    def get_compInfo(self,compName,id_tyc=None):
        comp_info = {}
        if id_tyc == None:
            id_tyc = self._get_id_tyc(compName)
            if id_tyc == None:
                return None
        comp_info["comp_name"] = compName
        comp_info["id_tyc"] = id_tyc
        comp_info["timeline"] = self.get_timeline(id_tyc)
        comp_info["relationship"] = self.get_relationship(id_tyc)

        methods = [item for item in dir(self) if item.startswith('get')]
        for method in methods:
            if method not in ['get_timeline','get_relationship','get_compInfo']:
                method_name = method.split('_')[-1]
                comp_info[method_name] = getattr(self,method)(compName,id_tyc)
        return comp_info


if __name__ == '__main__':
    comp_name = u'华为技术有限公司'
    tyc = TianYanCha()
    comp_info = tyc.get_timeline('198158709')
    print comp_info
