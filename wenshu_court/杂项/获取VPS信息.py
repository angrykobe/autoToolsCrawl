#encoding:utf-8
import xlrd
vps_info_file_name = u'VPS清单.xlsx'
data = xlrd.open_workbook(vps_info_file_name)
file_obj = open('temp.txt','a')
table = data.sheets()[0]
for i in range(1,table.nrows):
    no = table.cell(i,0).value.encode('utf-8')
    account = table.cell(i,3).value.encode('utf-8')
    pwd = table.cell(i,4).value.encode('utf-8')
    line = '"vps_%s":{"adsl_name":u"宽带连接","adsl_account":"%s","adsl_pwd":"%s"},'%(no,account,pwd)
    print line