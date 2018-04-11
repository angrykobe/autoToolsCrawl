#encoding:utf-8
import pymongo
import time
def write2txt(compInfo_list,file_obj):
    #compInfo_list = [str(ele).decode('utf-8').replace('^','').replace('\n','').replace('\r','') for ele in compInfo_list]
    for i in range(len(compInfo_list)):
        try:
            compInfo_list[i] = compInfo_list[i].replace('^','').replace('\n','').replace('\r','')
        except Exception,e:
            compInfo_list[i] = str(compInfo_list[i]).replace('^','').replace('\n','').replace('\r','')
    line = '^'.join(compInfo_list) + '\n'
    file_obj.write(line.encode('utf-8'))
def _parseData(compInfo):
    compInfo_list = []
    print compInfo['KeyNo']
    compInfo_list.append(compInfo['OperName'])
    compInfo_list.append(compInfo['No'])
    compInfo_list.append(compInfo['UpdatedDate'])
    compInfo_list.append(compInfo['RegistCapi'])
    try:
        compInfo_list.append(','.join(item['name'] for item in compInfo['OriginalName']))
    except Exception,e:
        compInfo_list.append('')
    compInfo_list.append(compInfo['Scope'])
    compInfo_list.append(compInfo['Type'])
    compInfo_list.append(compInfo['Email'])
    compInfo_list.append(compInfo['Status'])
    compInfo_list.append(compInfo['StartDate'])
    compInfo_list.append(compInfo['EndDate'])
    compInfo_list.append(compInfo['EconKind'])
    compInfo_list.append(compInfo['ContactNumber'])
    compInfo_list.append(compInfo['Address'])
    compInfo_list.append(compInfo['OrgNo'])
    compInfo_list.append(compInfo['Province'])
    compInfo_list.append(compInfo['Name'])
    try:
        compInfo_list.append(compInfo['Industry']['SubIndustry'])
    except Exception,e:
        compInfo_list.append('')
    compInfo_list.append(compInfo['CreditCode'])
    compInfo_list.append(compInfo['X'])
    compInfo_list.append(compInfo['Y'])
    try:
        compInfo_list.append(compInfo['EnglishName'])
    except Exception,e:
        compInfo_list.append('')
    compInfo_list.append(compInfo['BelongOrg'])
    return compInfo_list
def exportCompList():
    con = pymongo.MongoClient("mongodb://58.221.49.72:27017")
    db = con['QiChaCha']
    coll = db['compList']
    compList = coll.find({'ExportTime':{'$exists':False}})
    file_num = 20000 #每个文件条数
    first_file_index = 0
    file_index = first_file_index
    line_no = 0
    file_name = "d://data1//batch_qichacha//" + "qichacha_category_0.txt"
    file_obj = open(file_name,'a')
    for compInfo in compList:
        print line_no
        compInfo_list = _parseData(compInfo)
        if line_no>=file_num:
            file_obj.close()
            line_no = 0
            file_index += 1
            file_name = "d://data1//batch_qichacha//" + "qichacha_category_%d.txt"%file_index
            file_obj = open(file_name,'a')
        write2txt(compInfo_list,file_obj)
        line_no += 1
        #coll.update({'_id':compInfo['_id']},{'$set':{'ExportTime':time.time()}})
    try:
        file_obj.close()
    except Exception,e:
        print e


exportCompList()
