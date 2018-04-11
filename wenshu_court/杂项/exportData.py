#encoding:utf-8
import pymongo
import time
'''
.replace('^','').replace('\n','').replace('\r','')
'''
def ExportData():
    conn = pymongo.MongoClient('localhost',28019,socketKeepAlive=True)
    db = conn['WenShuCourt']
    coll = db['docids']
    file_dir = 'D:\\data1\\batch_wenshu\\'
    fileCount = 2000
    while True:
        file_name = file_dir + "wenshucourt_sumary_%d"%fileCount
        file_obj = open(file_name,'a+')
        docids = coll.find({'exported':{'$exists':False}}).limit(50000)
        if docids.count()==0:
            break
        for docid in docids:
            docid_list = []
            docid_list.append(docid[u'案件名称']).replace('^','').replace('\n','').replace('\r','')
            docid_list.append(docid[u'裁判日期']).replace('^','').replace('\n','').replace('\r','')
            docid_list.append(docid[u'裁判要旨段原文']).replace('^','').replace('\n','').replace('\r','')
            docid_list.append(docid[u'案号']).replace('^','').replace('\n','').replace('\r','')
            docid_list.append(docid[u'文书ID']).replace('^','').replace('\n','').replace('\r','')
            docid_list.append(docid[u'审判程序']).replace('^','').replace('\n','').replace('\r','')
            docid_list.append(docid[u'法院名称']).replace('^','').replace('\n','').replace('\r','')
            docid_list.append(docid[u'不公开理由']).replace('^','').replace('\n','').replace('\r','')
            docid_list.append(docid[u'案件类型']).replace('^','').replace('\n','').replace('\r','')
            line = '^'.join(docid_list) + "\n"
            file_obj.write(line)
        file_obj.close()
        fileCount += 1