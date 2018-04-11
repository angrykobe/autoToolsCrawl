#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-01-08 15:33:20
# @作者  : "jym"
# @说明    :获取vl5x参数值
# @Version : $Id$
import hashlib
import base64
def hex_sha1(str_tmp):
    return hashlib.sha1(str_tmp).hexdigest()
def hex_md5(str_tmp):
    return hashlib.md5(str_tmp).hexdigest()
def getKey(cookie):
    def strToLong(str_tmp):
        long = 0
        for i in range(len(str_tmp)):
            long += (ord(str_tmp[i]) << (i % 16))
        
        return long
    
    def strToLongEn(str_tmp):
        long = 0
        for i in range(len(str_tmp)):
            long += (ord(str_tmp[i]) << (i % 16)) + i
        
        return long
    
    def strToLongEn2(str_tmp, step):
        long = 0
        for i in range(len(str_tmp)):
            long += (ord(str_tmp[i]) << (i % 16)) + (i * step)
        
        return long
    
    def strToLongEn3(str_tmp, step):
        long = 0
        for i in range(len(str_tmp)):
            long += (ord(str_tmp[i]) << (i % 16)) + (i + step - ord(str_tmp[i]))
        
        return long
    
    def makeKey_0(str_tmp):
        str_tmp = str_tmp[5:5+5*5] + str_tmp[(5 + 1) * (5 + 1):(5 + 1) * (5 + 1)+3]
        a = str_tmp[5:] + str_tmp[-4:]
        b = str_tmp[4:] + a[-6:]
        return hex_md5(str_tmp)[4:4+24]
    
    def makeKey_1(str_tmp):
        str_tmp = str_tmp[5:5+5*5] + '5' + str_tmp[1:1+2] + '1' + str_tmp[(5 + 1) * (5 + 1):(5 + 1) * (5 + 1)+3]
        a = str_tmp[5:] + str_tmp[4:]
        b = str_tmp[12:] + a[-6:]
        c = str_tmp[4:] + a[6:]
        return hex_md5(c)[4:4+24]
    
    def makeKey_2(str_tmp):
        str_tmp = str_tmp[5:5+5*5] + '15' + str_tmp[1:1+2] + str_tmp[(5 + 1) * (5 + 1):(5 + 1) * (5 + 1)+3]
        a = str(strToLong(str_tmp[5:])) + str_tmp[4:]
        b = str(strToLong(str_tmp[5:])) + str_tmp[4:]
        c = str_tmp[4:] + b[5:]
        return hex_md5(c)[1:1+24]
    
    def makeKey_3(str_tmp):
        str_tmp = str_tmp[5:5+5*5] + '15' + str_tmp[1:1+2] + str_tmp[(5 + 1) * (5 + 1):(5 + 1) * (5 + 1)+3]
        a = str(strToLongEn(str_tmp[5:])) + str_tmp[4:]
        b = str_tmp[4:] + a[5:]
        c = str(strToLong(str_tmp[5:])) + str_tmp[4:]
        return hex_md5(b)[3:3+24]
    
    def makeKey_4(str_tmp):
        str_tmp = str_tmp[5:5+5*5] + '2' + str_tmp[1:1+2] + str_tmp[(5 + 1) * (5 + 1):(5 + 1) * (5 + 1)+3]
        long = 0
        for i in range(len(str_tmp[1:])):
            long += (ord(str_tmp[i]) << (i % 16))
        
        aa = str(long) + str_tmp[4:]
        long = 0
        a = str_tmp[5:]
        for i in range(len(a)):
            long += (ord(a[i]) << (i % 16)) + i
        
        a = str(long) + '' + str_tmp[4:]
        b = hex_md5(str_tmp[1:]) + str(strToLong(a[5:]))
        return hex_md5(b)[3:3+24]
    
    def makeKey_5(str_tmp):
        
        str_tmp = base64.b64encode(str_tmp[5:5+5*5] + str_tmp[1:1+2] + '1') + str_tmp[(5 + 1) * (5 + 1):(5 + 1) * (5 + 1)+3]
        a = str(strToLongEn(str_tmp[4:4+10])) + str_tmp[-4:]
        b = hex_md5(str_tmp[4:]) + a[2:]
        a = str_tmp[3:]
        c = str(strToLong(str_tmp[5:])) + str_tmp[4:]
        aa = str(long) + str_tmp[4:]
        long = 0
        for i in range(len(a)):
            long += (ord(a[i]) << (i % 12)) + i
        
        a = str(long) + '' + str_tmp[4:]
        return hex_md5(str_tmp)[4:4+24]
    
    def makeKey_6(str_tmp):
        
        str_tmp = str_tmp[5:5+5*5] + str_tmp[(5 + 1) * (5 + 1):(5 + 1) * (5 + 1)+3]
        a = base64.b64encode(str_tmp[4:4+10]) + str_tmp[2:]
        b = str_tmp[6:] + a[2:]
        c = str(strToLong(str_tmp[5:])) + str_tmp[4:]
        aa = str(long) + str_tmp[4:]
        long = 0
        a = str_tmp[5:]
        for i in range(len(a)):
            long += (ord(a[i]) << (i % 16)) + i
        
        a = str(long) + '' + str_tmp[4:]
        return hex_md5(b)[2:2+24]
    
    def makeKey_7(str_tmp):
        
        str_tmp = base64.b64encode(str_tmp[5:5+5 * 4] + '55' + str_tmp[1:1+2]) + str_tmp[(5 + 1) * (5 + 1):(5 + 1) * (5 + 1)+3]
        long = 0
        for i in range(len(str_tmp[1:])):
            long += (ord(str_tmp[i]) << (i % 16 + 5)) + 3 + 5
        
        aa = str(long) + str_tmp[4:]
        long = 0
        a = str_tmp[5:]
        for i in range(len(a)):
            long += (ord(a[i]) << (i % 16))
        
        a = str(long) + '' + str_tmp[4:]
        b = hex_md5(str_tmp[1:]) + str(strToLong(a[5:]))
        return hex_md5(b)[3:3+24]
    
    def makeKey_8(str_tmp):
        
        str_tmp = base64.b64encode(str_tmp[5:5+5 * 5 - 1] + '5' + '-' + '5') + str_tmp[1:1+2] + str_tmp[(5 + 1) * (5 + 1):(5 + 1) * (5 + 1)+3]
        long = 0
        for i in range(len(str_tmp[1:])):
            long += (ord(str_tmp[i]) << (i % 16))
        
        aa = str(long) + str_tmp[4:]
        long = 0
        a = str_tmp[5:]
        for i in range(len(a)):
            long += (ord(a[i]) << (i % 16))
        
        a = str(long) + '' + str_tmp[4:]
        b = hex_md5(str_tmp[1:]) + str(strToLongEn(a[5:]))
        return hex_md5(b)[4:4+24]
    
    def makeKey_17(str_tmp):
        
        str_tmp = str_tmp[5:5+5 * 5 - 1] + '7' + str_tmp[1:1+2] + '-' + '5'
        long = 0
        for i in range(len(str_tmp[1:])):
            long += (ord(str_tmp[i]) << (i % 11))
        
        aa = str(long) + str_tmp[4:]
        long = 0
        a = str_tmp[5:]
        for i in range(len(a)):
            long += (ord(a[i]) << (i % 16)) + i
        
        a = str(long) + '' + str_tmp[2:]
        b = base64.b64encode(a[1:]) + str(strToLongEn2(str_tmp[5:], 5 + 1)) + str_tmp[2+5:2+5+3]
        return hex_md5(b)[0:0+24]
    
    def makeKey_18(str_tmp):
        
        str_tmp = str_tmp[5:5+5 * 5 - 1] + '7' + str_tmp[1:1+2] + '5' + str_tmp[2+5:2+5+3]
        long = 0
        for i in range(len(str_tmp[1:])):
            long += (ord(str_tmp[i]) << (i % 11))
        
        aa = str(long) + str_tmp[4:]
        long = 0
        a = str_tmp[5:]
        for i in range(len(a)):
            long += (ord(a[i]) << (i % 16)) + i
        
        a = str(long) + '' + str_tmp[2:]
        b = a[1:] + str(strToLongEn2(str_tmp[5:], 5 + 1)) + str_tmp[2+5:2+5+3]
        return hex_md5(b)[0:0+24]
    
    def makeKey_19(str_tmp):
        
        str_tmp = str_tmp[5:5+5 * 5 - 1] + '7' + str_tmp[5:5+2] + '5' + str_tmp[2+5:2+5+3]
        long = 0
        for i in range(len(str_tmp[1:])):
            long += (ord(str_tmp[i]) << (i % 11))
        
        aa = str(long) + str_tmp[4:]
        long = 0
        a = str_tmp[5:]
        for i in range(len(a)):
            long += (ord(a[i]) << (i % 16)) + i
        
        a = str(long) + '' + str_tmp[2:]
        b = a[1:] + str(strToLongEn3(str_tmp[5:], 5 - 1)) + str_tmp[2+5:2+5+3]
        return hex_md5(b)[0:0+24]
    
    def makeKey_245(str_tmp):
        return hex_md5(makeKey_4(str_tmp) + makeKey_14(str_tmp) + 'c5a30')[3:3+24]
    
    def makeKey_246(str_tmp):
        return hex_md5(makeKey_19(str_tmp) + makeKey_15(str_tmp) + 'c5a31')[4:4+24]
    
    def makeKey_23(str_tmp):
        return hex_md5(makeKey_15(str_tmp) + makeKey_0(str_tmp) + 'vr6')[4:4+24]
    
    def makeKey_24(str_tmp):
        return hex_md5(makeKey_16(str_tmp) + makeKey_1(str_tmp) + 'vr7')[1:1+24]
    
    def makeKey_25(str_tmp):
        return hex_md5(makeKey_9(str_tmp) + makeKey_4(str_tmp) + 'vr8')[2:2+24]
    
    def makeKey_26(str_tmp):
        return hex_md5(makeKey_10(str_tmp) + makeKey_5(str_tmp) + 'vr9')[3:3+24]
    
    def makeKey_27(str_tmp):
        return hex_md5(makeKey_17(str_tmp) + makeKey_3(str_tmp) + 'vr10')[4:4+24]
    
    def makeKey_28(str_tmp):
        return hex_md5(makeKey_18(str_tmp) + makeKey_7(str_tmp) + 'vr11')[1:1+24]
    
    def makeKey_29(str_tmp):
        return hex_md5(makeKey_19(str_tmp) + makeKey_3(str_tmp) + 'vr12')[2:2+24]
    
    def makeKey_30(str_tmp):
        return hex_md5(makeKey_0(str_tmp) + makeKey_7(str_tmp) + 'vr13')[3:3+24]
    
    def makeKey_31(str_tmp):
        return hex_md5(makeKey_1(str_tmp) + makeKey_8(str_tmp) + 'vr14')[4:4+24]
    
    def makeKey_32(str_tmp):
        return hex_md5(makeKey_4(str_tmp) + makeKey_14(str_tmp) + 'vr15')[3:3+24]
    
    def makeKey_33(str_tmp):
        return hex_md5(makeKey_5(str_tmp) + makeKey_15(str_tmp) + 'vr16')[4:4+24]
    
    def makeKey_34(str_tmp):
        return hex_md5(makeKey_3(str_tmp) + makeKey_16(str_tmp) + 'vr17')[1:1+24]
    
    def makeKey_35(str_tmp):
        return hex_md5(makeKey_7(str_tmp) + makeKey_9(str_tmp) + 'vr18')[2:2+24]
    
    def makeKey_36(str_tmp):
        return hex_md5(makeKey_8(str_tmp) + makeKey_10(str_tmp) + 'vr19')[3:3+24]
    
    def makeKey_57(str_tmp):
        return hex_md5(makeKey_9(str_tmp) + makeKey_17(str_tmp) + 'l68a')[1:1+24]
    
    def makeKey_58(str_tmp):
        return hex_md5(makeKey_10(str_tmp) + makeKey_18(str_tmp) + 'l69a')[2:2+24]
    
    def makeKey_59(str_tmp):
        return hex_md5(makeKey_17(str_tmp) + makeKey_19(str_tmp) + 'l70a')[3:3+24]
    
    def makeKey_60(str_tmp):
        return hex_md5(makeKey_18(str_tmp) + makeKey_0(str_tmp) + 'l71a')[1:1+24]
    
    def makeKey_61(str_tmp):
        return hex_md5(makeKey_19(str_tmp) + makeKey_1(str_tmp) + 'l72a')[2:2+24]
    
    def makeKey_62(str_tmp):
        return hex_md5(makeKey_0(str_tmp) + makeKey_4(str_tmp) + 'l73a')[3:3+24]
    
    def makeKey_63(str_tmp):
        return hex_md5(makeKey_1(str_tmp) + makeKey_19(str_tmp) + 'vr46')[4:4+24]
    
    def makeKey_64(str_tmp):
        return hex_md5(makeKey_4(str_tmp) + makeKey_0(str_tmp) + 'vr47')[3:3+24]
    
    def makeKey_65(str_tmp):
        return hex_md5(makeKey_14(str_tmp) + makeKey_1(str_tmp) + 'vr48')[1:1+24]
    
    def makeKey_66(str_tmp):
        return hex_md5(makeKey_15(str_tmp) + makeKey_4(str_tmp) + 'vr49')[2:2+24]
    
    def makeKey_67(str_tmp):
        return hex_md5(makeKey_16(str_tmp) + makeKey_5(str_tmp) + 'vr50')[3:3+24]
    
    def makeKey_68(str_tmp):
        return hex_md5(makeKey_9(str_tmp) + makeKey_3(str_tmp) + 'at4')[4:4+24]
    
    def makeKey_69(str_tmp):
        return hex_md5(makeKey_10(str_tmp) + makeKey_7(str_tmp) + 'at5')[1:1+24]
    
    def makeKey_70(str_tmp):
        return hex_md5(makeKey_17(str_tmp) + makeKey_0(str_tmp) + 'at6')[2:2+24]
    
    def makeKey_71(str_tmp):
        return hex_md5(makeKey_18(str_tmp) + makeKey_1(str_tmp) + 'at7')[3:3+24]
    
    def makeKey_168(str_tmp):
        return hex_md5(makeKey_0(str_tmp) + makeKey_0(str_tmp) + 'ff85')[1:1+24]
    
    def makeKey_169(str_tmp):
        return hex_md5(makeKey_1(str_tmp) + makeKey_1(str_tmp) + 'ff105')[2:2+24]
    
    def makeKey_170(str_tmp):
        return hex_md5(makeKey_4(str_tmp) + makeKey_4(str_tmp) + 'ff106')[3:3+24]
    
    def makeKey_171(str_tmp):
        return hex_md5(makeKey_17(str_tmp) + makeKey_5(str_tmp) + 'ff107')[1:1+24]
    
    def makeKey_172(str_tmp):
        return hex_md5(makeKey_18(str_tmp) + makeKey_3(str_tmp) + 'ff108')[2:2+24]
    
    def makeKey_173(str_tmp):
        return hex_md5(makeKey_19(str_tmp) + makeKey_7(str_tmp) + 'ff109')[3:3+24]
    
    def makeKey_174(str_tmp):
        return hex_md5(makeKey_0(str_tmp) + makeKey_17(str_tmp) + 'aa0')[4:4+24]
    
    def makeKey_175(str_tmp):
        return hex_md5(makeKey_1(str_tmp) + makeKey_18(str_tmp) + 'aa1')[1:1+24]
    
    def makeKey_176(str_tmp):
        return hex_md5(makeKey_4(str_tmp) + makeKey_19(str_tmp) + 'aa2')[2:2+24]
    
    def makeKey_177(str_tmp):
        return hex_md5(makeKey_9(str_tmp) + makeKey_0(str_tmp) + 'aa3')[3:3+24]
    
    def makeKey_178(str_tmp):
        return hex_md5(makeKey_10(str_tmp) + makeKey_1(str_tmp) + 'aa4')[4:4+24]
    
    def makeKey_179(str_tmp):
        return hex_md5(makeKey_17(str_tmp) + makeKey_4(str_tmp) + 'aa5')[1:1+24]
    
    def makeKey_180(str_tmp):
        return hex_md5(makeKey_18(str_tmp) + makeKey_14(str_tmp) + 'aa6')[3:3+24]
    
    def makeKey_181(str_tmp):
        return hex_md5(makeKey_19(str_tmp) + makeKey_15(str_tmp) + 'ff98')[1:1+24]
    
    def makeKey_182(str_tmp):
        return hex_md5(makeKey_0(str_tmp) + makeKey_16(str_tmp) + 'ff99')[2:2+24]
    
    def makeKey_183(str_tmp):
        return hex_md5(makeKey_1(str_tmp) + makeKey_9(str_tmp) + 'ff100')[3:3+24]
    
    def makeKey_184(str_tmp):
        return hex_md5(makeKey_4(str_tmp) + makeKey_10(str_tmp) + 'ff101')[4:4+24]
    
    def makeKey_185(str_tmp):
        return hex_md5(makeKey_14(str_tmp) + makeKey_17(str_tmp) + 'ff102')[3:3+24]
    
    def makeKey_186(str_tmp):
        return hex_md5(makeKey_15(str_tmp) + makeKey_18(str_tmp) + 'ff103')[4:4+24]
    
    def makeKey_187(str_tmp):
        return hex_md5(makeKey_16(str_tmp) + makeKey_19(str_tmp) + 'ff104')[4:4+24]
    
    def makeKey_188(str_tmp):
        return hex_md5(makeKey_9(str_tmp) + makeKey_0(str_tmp) + 'ff105')[1:1+24]
    
    def makeKey_189(str_tmp):
        return hex_md5(makeKey_10(str_tmp) + makeKey_1(str_tmp) + 'ff106')[2:2+24]
    
    def makeKey_190(str_tmp):
        return hex_md5(makeKey_17(str_tmp) + makeKey_4(str_tmp) + 'ff107')[3:3+24]
    
    def makeKey_191(str_tmp):
        return hex_md5(makeKey_18(str_tmp) + makeKey_19(str_tmp) + 'ff108')[4:4+24]
    
    def makeKey_192(str_tmp):
        return hex_md5(makeKey_19(str_tmp) + makeKey_0(str_tmp) + 'ff109')[1:1+24]
    
    def makeKey_193(str_tmp):
        return hex_md5(makeKey_0(str_tmp) + makeKey_1(str_tmp) + 'aa0')[2:2+24]
    
    def makeKey_194(str_tmp):
        return hex_md5(makeKey_1(str_tmp) + makeKey_4(str_tmp) + 'aa1')[3:3+24]
    
    def makeKey_195(str_tmp):
        return hex_md5(makeKey_4(str_tmp) + makeKey_14(str_tmp) + 'aa2')[4:4+24]
    
    def makeKey_196(str_tmp):
        return hex_md5(makeKey_5(str_tmp) + makeKey_15(str_tmp) + 'aa3')[3:3+24]
    
    def makeKey_197(str_tmp):
        return hex_md5(makeKey_3(str_tmp) + makeKey_16(str_tmp) + 'aa4')[4:4+24]
    
    def makeKey_72(str_tmp):
        return hex_md5(makeKey_19(str_tmp) + makeKey_4(str_tmp) + 'at8')[4:4+24]
    
    def makeKey_73(str_tmp):
        return hex_md5(makeKey_0(str_tmp) + makeKey_17(str_tmp) + 'at9')[1:1+24]
    
    def makeKey_74(str_tmp):
        return hex_md5(makeKey_1(str_tmp) + makeKey_18(str_tmp) + 'at10')[2:2+24]
    
    def makeKey_75(str_tmp):
        return hex_md5(makeKey_14(str_tmp) + makeKey_19(str_tmp) + 'at11')[3:3+24]
    
    def makeKey_76(str_tmp):
        return hex_md5(makeKey_15(str_tmp) + makeKey_0(str_tmp) + 'at12')[4:4+24]
    
    def makeKey_77(str_tmp):
        return hex_md5(makeKey_16(str_tmp) + makeKey_1(str_tmp) + 'at13')[3:3+24]
    
    def makeKey_78(str_tmp):
        return hex_md5(makeKey_9(str_tmp) + makeKey_4(str_tmp) + 'at14')[4:4+24]
    
    def makeKey_79(str_tmp):
        return hex_md5(makeKey_10(str_tmp) + makeKey_9(str_tmp) + 'at15')[1:1+24]
    
    def makeKey_80(str_tmp):
        return hex_md5(makeKey_17(str_tmp) + makeKey_10(str_tmp) + 'at16')[2:2+24]
    
    def makeKey_81(str_tmp):
        return hex_md5(makeKey_18(str_tmp) + makeKey_17(str_tmp) + 'at17')[3:3+24]
    
    def makeKey_82(str_tmp):
        return hex_md5(makeKey_14(str_tmp) + makeKey_18(str_tmp) + 'at18')[1:1+24]
    
    def makeKey_83(str_tmp):
        return hex_md5(makeKey_15(str_tmp) + makeKey_19(str_tmp) + 'at19')[4:4+24]
    
    def makeKey_84(str_tmp):
        return hex_md5(makeKey_16(str_tmp) + makeKey_0(str_tmp) + 'at20')[1:1+24]
    
    def makeKey_85(str_tmp):
        return hex_md5(makeKey_9(str_tmp) + makeKey_1(str_tmp) + 'at21')[2:2+24]
    
    def makeKey_86(str_tmp):
        return hex_md5(makeKey_10(str_tmp) + makeKey_4(str_tmp) + 'at22')[3:3+24]
    
    def makeKey_87(str_tmp):
        return hex_md5(makeKey_14(str_tmp) + makeKey_14(str_tmp) + 'at23')[4:4+24]
    
    def makeKey_88(str_tmp):
        return hex_md5(makeKey_15(str_tmp) + makeKey_15(str_tmp) + 'at24')[1:1+24]
    
    def makeKey_37(str_tmp):
        return hex_md5(makeKey_6(str_tmp) + makeKey_17(str_tmp) + 'vr20')[1:1+24]
    
    def makeKey_38(str_tmp):
        return hex_md5(makeKey_12(str_tmp) + makeKey_18(str_tmp) + 'vr21')[2:2+24]
    
    def makeKey_39(str_tmp):
        return hex_md5(makeKey_14(str_tmp) + makeKey_19(str_tmp) + 'vr22')[3:3+24]
    
    def makeKey_40(str_tmp):
        return hex_md5(makeKey_15(str_tmp) + makeKey_0(str_tmp) + 'vr23')[4:4+24]
    
    def makeKey_41(str_tmp):
        return hex_md5(makeKey_16(str_tmp) + makeKey_1(str_tmp) + 'vr24')[3:3+24]
    
    def makeKey_42(str_tmp):
        return hex_md5(makeKey_9(str_tmp) + makeKey_4(str_tmp) + 'vr25')[4:4+24]
    
    def makeKey_43(str_tmp):
        return hex_md5(makeKey_10(str_tmp) + makeKey_5(str_tmp) + 'vr26')[1:1+24]
    
    def makeKey_44(str_tmp):
        return hex_md5(makeKey_17(str_tmp) + makeKey_3(str_tmp) + 'vr27')[2:2+24]
    
    def makeKey_45(str_tmp):
        return hex_md5(makeKey_18(str_tmp) + makeKey_7(str_tmp) + 'vr28')[3:3+24]
    
    def makeKey_285(str_tmp):
        return hex_md5(makeKey_1(str_tmp) + makeKey_19(str_tmp) + 'f10b')[3:3+24]
    
    def makeKey_286(str_tmp):
        return hex_md5(makeKey_4(str_tmp) + makeKey_0(str_tmp) + 'f11b')[4:4+24]
    
    def makeKey_287(str_tmp):
        return hex_md5(makeKey_19(str_tmp) + makeKey_1(str_tmp) + 'f12b')[1:1+24]
    
    def makeKey_288(str_tmp):
        return hex_md5(makeKey_0(str_tmp) + makeKey_4(str_tmp) + 'f13b')[2:2+24]
    
    def makeKey_289(str_tmp):
        return hex_md5(makeKey_1(str_tmp) + makeKey_19(str_tmp) + 'f14b')[1:1+24]
    
    def makeKey_290(str_tmp):
        return hex_md5(makeKey_10(str_tmp) + makeKey_0(str_tmp) + 'f15b')[2:2+24]
    
    def makeKey_291(str_tmp):
        return hex_md5(makeKey_17(str_tmp) + makeKey_1(str_tmp) + 'f16b')[3:3+24]
    
    def makeKey_292(str_tmp):
        return hex_md5(makeKey_18(str_tmp) + makeKey_10(str_tmp) + 'f17b')[4:4+24]
    
    def makeKey_293(str_tmp):
        return hex_md5(makeKey_19(str_tmp) + makeKey_17(str_tmp) + 'f18b')[1:1+24]
    
    def makeKey_294(str_tmp):
        return hex_md5(makeKey_0(str_tmp) + makeKey_18(str_tmp) + 'f19b')[2:2+24]
    
    def makeKey_20(str_tmp):
        return hex_md5(makeKey_10(str_tmp) + makeKey_5(str_tmp) + 'saf')[1:1+24]
    
    def makeKey_21(str_tmp):
        return hex_md5(makeKey_11(str_tmp) + makeKey_3(str_tmp) + 'vr4')[2:2+24]
    
    def makeKey_22(str_tmp):
        return hex_md5(makeKey_14(str_tmp) + makeKey_19(str_tmp) + 'e')[3:3+24]
    
    def makeKey_205(str_tmp):
        return hex_md5(makeKey_14(str_tmp) + makeKey_19(str_tmp) + 'aa12')[2:2+24]
    
    def makeKey_206(str_tmp):
        return hex_md5(makeKey_15(str_tmp) + makeKey_0(str_tmp) + 'aa13')[2:2+24]
    
    def makeKey_207(str_tmp):
        return hex_md5(makeKey_16(str_tmp) + makeKey_1(str_tmp) + 'aa14')[3:3+24]
    
    def makeKey_231(str_tmp):
        return hex_md5(makeKey_19(str_tmp) + makeKey_1(str_tmp) + 'wsn55')[2:2+24]
    
    def makeKey_232(str_tmp):
        return hex_md5(makeKey_0(str_tmp) + makeKey_4(str_tmp) + 'wsn56')[3:3+24]
    
    def makeKey_233(str_tmp):
        return hex_md5(makeKey_1(str_tmp) + makeKey_5(str_tmp) + 'wsn57')[4:4+24]
    
    def makeKey_234(str_tmp):
        return hex_md5(makeKey_4(str_tmp) + makeKey_3(str_tmp) + 'wsn58')[1:1+24]
    
    def makeKey_235(str_tmp):
        return hex_md5(makeKey_14(str_tmp) + makeKey_19(str_tmp) + 'wsn59')[2:2+24]
    
    def makeKey_236(str_tmp):
        return hex_md5(makeKey_15(str_tmp) + makeKey_0(str_tmp) + 'wsn60')[3:3+24]
    
    def makeKey_237(str_tmp):
        return hex_md5(makeKey_16(str_tmp) + makeKey_1(str_tmp) + 'c5a22')[2:2+24]
    
    def makeKey_295(str_tmp):
        return hex_md5(makeKey_1(str_tmp) + makeKey_19(str_tmp) + 'f20b')[3:3+24]
    
    def makeKey_296(str_tmp):
        return hex_md5(makeKey_4(str_tmp) + makeKey_0(str_tmp) + 'f21b')[4:4+24]
    
    def makeKey_297(str_tmp):
        return hex_md5(makeKey_5(str_tmp) + makeKey_1(str_tmp) + 'f22b')[3:3+24]
    
    def makeKey_298(str_tmp):
        return hex_md5(makeKey_3(str_tmp) + makeKey_4(str_tmp) + 'f23b')[4:4+24]
    
    def makeKey_46(str_tmp):
        return hex_md5(makeKey_19(str_tmp) + makeKey_17(str_tmp) + 'vr29')[4:4+24]
    
    def makeKey_47(str_tmp):
        return hex_md5(makeKey_0(str_tmp) + makeKey_18(str_tmp) + 'vr30')[1:1+24]
    
    def makeKey_48(str_tmp):
        return hex_md5(makeKey_1(str_tmp) + makeKey_19(str_tmp) + 'vr31')[2:2+24]
    
    def makeKey_49(str_tmp):
        return hex_md5(makeKey_4(str_tmp) + makeKey_0(str_tmp) + 'vr32')[3:3+24]
    
    def makeKey_50(str_tmp):
        return hex_md5(makeKey_5(str_tmp) + makeKey_1(str_tmp) + 'vr33')[4:4+24]
    
    def makeKey_51(str_tmp):
        return hex_md5(makeKey_3(str_tmp) + makeKey_4(str_tmp) + 'saf')[1:1+24]
    
    def makeKey_52(str_tmp):
        return hex_md5(makeKey_7(str_tmp) + makeKey_14(str_tmp) + 'vr4')[2:2+24]
    
    def makeKey_53(str_tmp):
        return hex_md5(makeKey_12(str_tmp) + makeKey_15(str_tmp) + 'e')[3:3+24]
    
    def makeKey_54(str_tmp):
        return hex_md5(makeKey_14(str_tmp) + makeKey_16(str_tmp) + 'l65a')[4:4+24]
    
    def makeKey_55(str_tmp):
        return hex_md5(makeKey_15(str_tmp) + makeKey_9(str_tmp) + 'l66a')[3:3+24]
    
    def makeKey_56(str_tmp):
        return hex_md5(makeKey_16(str_tmp) + makeKey_10(str_tmp) + 'l67a')[4:4+24]
    
    def makeKey_89(str_tmp):
        return hex_md5(makeKey_16(str_tmp) + makeKey_16(str_tmp) + 'at25')[2:2+24]
    
    def makeKey_90(str_tmp):
        return hex_md5(makeKey_9(str_tmp) + makeKey_9(str_tmp) + 'at26')[3:3+24]
    
    def makeKey_91(str_tmp):
        return hex_md5(makeKey_10(str_tmp) + makeKey_10(str_tmp) + 'at27')[4:4+24]
    
    def makeKey_92(str_tmp):
        return hex_md5(makeKey_17(str_tmp) + makeKey_17(str_tmp) + 'at28')[3:3+24]
    
    def makeKey_93(str_tmp):
        return hex_md5(makeKey_18(str_tmp) + makeKey_18(str_tmp) + 'at29')[4:4+24]
    
    def makeKey_94(str_tmp):
        return hex_md5(makeKey_19(str_tmp) + makeKey_19(str_tmp) + 'at30')[1:1+24]
    
    def makeKey_95(str_tmp):
        return hex_md5(makeKey_0(str_tmp) + makeKey_0(str_tmp) + 'at31')[2:2+24]
    
    def makeKey_96(str_tmp):
        return hex_md5(makeKey_1(str_tmp) + makeKey_1(str_tmp) + 'at32')[3:3+24]
    
    def makeKey_97(str_tmp):
        return hex_md5(makeKey_4(str_tmp) + makeKey_4(str_tmp) + 'lb73a')[4:4+24]
    
    def makeKey_98(str_tmp):
        return hex_md5(makeKey_5(str_tmp) + makeKey_5(str_tmp) + 'lb74a')[3:3+24]
    
    def makeKey_99(str_tmp):
        return hex_md5(makeKey_3(str_tmp) + makeKey_3(str_tmp) + 'lb75a')[4:4+24]
    
    def makeKey_125(str_tmp):
        return hex_md5(makeKey_3(str_tmp) + makeKey_0(str_tmp) + 'ssa36')[2:2+24]
    
    def makeKey_126(str_tmp):
        return hex_md5(makeKey_7(str_tmp) + makeKey_1(str_tmp) + 'ff43')[3:3+24]
    
    def makeKey_127(str_tmp):
        return hex_md5(makeKey_3(str_tmp) + makeKey_4(str_tmp) + 'ff44')[4:4+24]
    
    def makeKey_128(str_tmp):
        return hex_md5(makeKey_7(str_tmp) + makeKey_5(str_tmp) + 'ff45')[1:1+24]
    
    def makeKey_129(str_tmp):
        return hex_md5(makeKey_8(str_tmp) + makeKey_3(str_tmp) + 'ff46')[2:2+24]
    
    def makeKey_130(str_tmp):
        return hex_md5(makeKey_14(str_tmp) + makeKey_7(str_tmp) + 'at45')[3:3+24]
    
    def makeKey_131(str_tmp):
        return hex_md5(makeKey_15(str_tmp) + makeKey_10(str_tmp) + 'at46')[4:4+24]
    
    def makeKey_132(str_tmp):
        return hex_md5(makeKey_16(str_tmp) + makeKey_17(str_tmp) + 'at47')[3:3+24]
    
    def makeKey_133(str_tmp):
        return hex_md5(makeKey_9(str_tmp) + makeKey_18(str_tmp) + 'at48')[4:4+24]
    
    def makeKey_134(str_tmp):
        return hex_md5(makeKey_10(str_tmp) + makeKey_19(str_tmp) + 'at49')[1:1+24]
    
    def makeKey_135(str_tmp):
        return hex_md5(makeKey_17(str_tmp) + makeKey_0(str_tmp) + 'ff31')[2:2+24]
    
    def makeKey_136(str_tmp):
        return hex_md5(makeKey_18(str_tmp) + makeKey_1(str_tmp) + 'ff32')[1:1+24]
    
    def makeKey_137(str_tmp):
        return hex_md5(makeKey_19(str_tmp) + makeKey_14(str_tmp) + 'ff33')[2:2+24]
    
    def makeKey_138(str_tmp):
        return hex_md5(makeKey_0(str_tmp) + makeKey_15(str_tmp) + 'ff55')[3:3+24]
    
    def makeKey_139(str_tmp):
        return hex_md5(makeKey_1(str_tmp) + makeKey_16(str_tmp) + 'ff56')[4:4+24]
    
    def makeKey_140(str_tmp):
        return hex_md5(makeKey_4(str_tmp) + makeKey_9(str_tmp) + 'ff57')[1:1+24]
    
    def makeKey_141(str_tmp):
        return hex_md5(makeKey_5(str_tmp) + makeKey_10(str_tmp) + 'ff58')[2:2+24]
    
    def makeKey_142(str_tmp):
        return hex_md5(makeKey_3(str_tmp) + makeKey_17(str_tmp) + 'ff59')[3:3+24]
    
    def makeKey_143(str_tmp):
        return hex_md5(makeKey_7(str_tmp) + makeKey_18(str_tmp) + 'ff60')[4:4+24]
    
    def makeKey_144(str_tmp):
        return hex_md5(makeKey_17(str_tmp) + makeKey_19(str_tmp) + 'ff61')[1:1+24]
    
    def makeKey_145(str_tmp):
        return hex_md5(makeKey_18(str_tmp) + makeKey_0(str_tmp) + 'ff62')[2:2+24]
    
    def makeKey_146(str_tmp):
        return hex_md5(makeKey_19(str_tmp) + makeKey_1(str_tmp) + 'ff63')[3:3+24]
    
    def makeKey_147(str_tmp):
        return hex_md5(makeKey_0(str_tmp) + makeKey_4(str_tmp) + 'ff64')[4:4+24]
    
    def makeKey_148(str_tmp):
        return hex_md5(makeKey_1(str_tmp) + makeKey_5(str_tmp) + 'ff65')[3:3+24]
    
    def makeKey_149(str_tmp):
        return hex_md5(makeKey_4(str_tmp) + makeKey_3(str_tmp) + 'ff66')[4:4+24]
    
    def makeKey_150(str_tmp):
        return hex_md5(makeKey_14(str_tmp) + makeKey_19(str_tmp) + 'ff67')[1:1+24]
    
    def makeKey_151(str_tmp):
        return hex_md5(makeKey_15(str_tmp) + makeKey_0(str_tmp) + 'ff68')[2:2+24]
    
    def makeKey_9(str_tmp):
        str_tmp = str_tmp[5:5+5*5] + '5' + str_tmp[1:1+2] + '1' + str_tmp[(5 + 1) * (5 + 1):(5 + 1) * (5 + 1)+3]
        a = str_tmp[5:] + str_tmp[4:]
        b = str_tmp[12:] + a[-6:]
        c = hex_sha1(str_tmp[4:]) + a[6:]
        return hex_md5(c)[4:4+24]
    
    def makeKey_10(str_tmp):
        
        str_tmp = base64.b64encode(str_tmp[5:5+5 * 5 - 1] + '5') + str_tmp[1:1+2] + str_tmp[(5 + 1) * (5 + 1):(5 + 1) * (5 + 1)+3]
        long = 0
        for i in range(len(str_tmp[1:])):
            long += (ord(str_tmp[i]) << (i % 16))
        
        aa = str(long) + str_tmp[4:]
        long = 0
        a = str_tmp[5:]
        for i in range(len(a)):
            long += (ord(a[i]) << (i % 16))
        
        a = str(long) + '' + str_tmp[4:]
        b = hex_md5(str_tmp[1:]) + hex_sha1(a[5:])
        return hex_md5(b)[4:4+24]
    
    def makeKey_11(str_tmp):
        
        str_tmp = str_tmp[5:5+5 * 5 - 1] + '2' + str_tmp[1:1+2] + str_tmp[(5 + 1) * (5 + 1):(5 + 1) * (5 + 1)+3]
        long = 0
        for i in range(len(str_tmp[1:])):
            long += (ord(str_tmp[i]) << (i % 16))
        
        aa = str(long) + str_tmp[4:]
        long = 0
        a = str_tmp[5:]
        for i in range(len(a)):
            long += (ord(a[i]) << (i % 16))
        
        a = str(long) + '' + str_tmp[2:]
        b = str_tmp[1:] + hex_sha1(a[5:])
        return hex_md5(b)[2:2+24]
    
    def makeKey_12(str_tmp):
        
        str_tmp = str_tmp[5:5+5 * 5 - 1] + str_tmp[(5 + 1) * (5 + 1):(5 + 1) * (5 + 1)+3] + '2' + str_tmp[1:1+2]
        long = 0
        for i in range(len(str_tmp[1:])):
            long += (ord(str_tmp[i]) << (i % 16))
        
        aa = str(long) + str_tmp[4:]
        long = 0
        a = str_tmp[5:]
        for i in range(len(a)):
            long += (ord(a[i]) << (i % 16))
        
        a = str(long) + '' + str_tmp[2:]
        b = str_tmp[1:] + hex_sha1(str_tmp[5:])
        return hex_md5(b)[1:1+24]
    
    def makeKey_13(str_tmp):
        
        str_tmp = str_tmp[5:5+5 * 5 - 1] + '2' + str_tmp[1:1+2]
        long = 0
        for i in range(len(str_tmp[1:])):
            long += (ord(str_tmp[i]) << (i % 16))
        
        aa = str(long) + str_tmp[4:]
        long = 0
        a = str_tmp[5:]
        for i in range(len(a)):
            long += (ord(a[i]) << (i % 16))
        
        a = str(long) + '' + str_tmp[2:]
        b = base64.b64encode(str_tmp[1:] + hex_sha1(str_tmp[5:]))
        return hex_md5(b)[1:1+24]
    
    def makeKey_14(str_tmp):
        
        str_tmp = str_tmp[5:5+5 * 5 - 1] + '2' + str_tmp[1:1+2]
        long = 0
        for i in range(len(str_tmp[1:])):
            long += (ord(str_tmp[i]) << (i % 16))
        
        aa = str(long) + str_tmp[4:]
        long = 0
        a = str_tmp[5:]
        for i in range(len(a)):
            long += (ord(a[i]) << (i % 16))
        
        a = str(long) + '' + str_tmp[2:]
        b = base64.b64encode(str_tmp[1:] + str_tmp[5:] + str_tmp[1:1+3])
        return hex_sha1(b)[1:1+24]
    
    def makeKey_15(str_tmp):
        
        str_tmp = str_tmp[5:5+5 * 5 - 1] + '2' + str_tmp[1:1+2]
        long = 0
        for i in range(len(str_tmp[1:])):
            long += (ord(str_tmp[i]) << (i % 16))
        
        aa = str(long) + str_tmp[4:]
        long = 0
        a = str_tmp[5:]
        for i in range(len(a)):
            long += (ord(a[i]) << (i % 16))
        
        a = str(long) + '' + str_tmp[2:]
        b = base64.b64encode(a[1:] + str_tmp[5:] + str_tmp[2:2+3])
        return hex_sha1(b)[1:1+24]
    
    def makeKey_16(str_tmp):
        
        str_tmp = str_tmp[5:5+5 * 5 - 1] + '2' + str_tmp[1:1+2] + '-' + '5'
        long = 0
        for i in range(len(str_tmp[1:])):
            long += (ord(str_tmp[i]) << (i % 11))
        
        aa = str(long) + str_tmp[4:]
        long = 0
        a = str_tmp[5:]
        for i in range(len(a)):
            long += (ord(a[i]) << (i % 16)) + i
        
        a = str(long) + '' + str_tmp[2:]
        b = base64.b64encode(a[1:]) + str(strToLongEn2(str_tmp[5:], 5)) + str_tmp[2:2+3]
        return hex_md5(b)[2:2+24]
    
    def makeKey_152(str_tmp):
        return hex_md5(makeKey_16(str_tmp) + makeKey_1(str_tmp) + 'ff69')[3:3+24]
    
    def makeKey_153(str_tmp):
        return hex_md5(makeKey_9(str_tmp) + makeKey_4(str_tmp) + 'ff70')[1:1+24]
    
    def makeKey_154(str_tmp):
        return hex_md5(makeKey_10(str_tmp) + makeKey_5(str_tmp) + 'ff71')[1:1+24]
    
    def makeKey_155(str_tmp):
        return hex_md5(makeKey_17(str_tmp) + makeKey_3(str_tmp) + 'ff72')[2:2+24]
    
    def makeKey_156(str_tmp):
        return hex_md5(makeKey_18(str_tmp) + makeKey_7(str_tmp) + 'ff73')[3:3+24]
    
    def makeKey_157(str_tmp):
        return hex_md5(makeKey_19(str_tmp) + makeKey_3(str_tmp) + 'ff74')[4:4+24]
    
    def makeKey_158(str_tmp):
        return hex_md5(makeKey_0(str_tmp) + makeKey_7(str_tmp) + 'ff75')[1:1+24]
    
    def makeKey_159(str_tmp):
        return hex_md5(makeKey_1(str_tmp) + makeKey_8(str_tmp) + 'ff76')[2:2+24]
    
    def makeKey_160(str_tmp):
        return hex_md5(makeKey_4(str_tmp) + makeKey_14(str_tmp) + 'ff77')[3:3+24]
    
    def makeKey_161(str_tmp):
        return hex_md5(makeKey_19(str_tmp) + makeKey_15(str_tmp) + 'ff78')[4:4+24]
    
    def makeKey_162(str_tmp):
        return hex_md5(makeKey_0(str_tmp) + makeKey_16(str_tmp) + 'ff79')[1:1+24]
    
    def makeKey_163(str_tmp):
        return hex_md5(makeKey_1(str_tmp) + makeKey_9(str_tmp) + 'ff80')[2:2+24]
    
    def makeKey_164(str_tmp):
        return hex_md5(makeKey_4(str_tmp) + makeKey_10(str_tmp) + 'ff81')[3:3+24]
    
    def makeKey_165(str_tmp):
        return hex_md5(makeKey_5(str_tmp) + makeKey_17(str_tmp) + 'ff82')[4:4+24]
    
    def makeKey_166(str_tmp):
        return hex_md5(makeKey_3(str_tmp) + makeKey_18(str_tmp) + 'ff83')[3:3+24]
    
    def makeKey_167(str_tmp):
        return hex_md5(makeKey_7(str_tmp) + makeKey_19(str_tmp) + 'ff84')[4:4+24]
    
    def makeKey_100(str_tmp):
        return hex_md5(makeKey_7(str_tmp) + makeKey_3(str_tmp) + 'lb76a')[1:1+24]
    
    def makeKey_101(str_tmp):
        return hex_md5(makeKey_10(str_tmp) + makeKey_7(str_tmp) + 'lb77a')[2:2+24]
    
    def makeKey_102(str_tmp):
        return hex_md5(makeKey_17(str_tmp) + makeKey_18(str_tmp) + 'lb78a')[1:1+24]
    
    def makeKey_103(str_tmp):
        return hex_md5(makeKey_18(str_tmp) + makeKey_19(str_tmp) + 'lb79a')[2:2+24]
    
    def makeKey_104(str_tmp):
        return hex_md5(makeKey_19(str_tmp) + makeKey_0(str_tmp) + 'lb80a')[3:3+24]
    
    def makeKey_105(str_tmp):
        return hex_md5(makeKey_0(str_tmp) + makeKey_0(str_tmp) + 'lb81a')[4:4+24]
    
    def makeKey_106(str_tmp):
        return hex_md5(makeKey_1(str_tmp) + makeKey_1(str_tmp) + 'l82a')[1:1+24]
    
    def makeKey_107(str_tmp):
        return hex_md5(makeKey_14(str_tmp) + makeKey_14(str_tmp) + 'at43')[2:2+24]
    
    def makeKey_108(str_tmp):
        return hex_md5(makeKey_15(str_tmp) + makeKey_15(str_tmp) + 'at44')[3:3+24]
    
    def makeKey_109(str_tmp):
        return hex_md5(makeKey_16(str_tmp) + makeKey_16(str_tmp) + 'at45')[4:4+24]
    
    def makeKey_110(str_tmp):
        return hex_md5(makeKey_9(str_tmp) + makeKey_9(str_tmp) + 'at46')[1:1+24]
    
    def makeKey_111(str_tmp):
        return hex_md5(makeKey_10(str_tmp) + makeKey_10(str_tmp) + 'at47')[2:2+24]
    
    def makeKey_112(str_tmp):
        return hex_md5(makeKey_17(str_tmp) + makeKey_17(str_tmp) + 'at48')[3:3+24]
    
    def makeKey_113(str_tmp):
        return hex_md5(makeKey_18(str_tmp) + makeKey_18(str_tmp) + 'at49')[4:4+24]
    
    def makeKey_114(str_tmp):
        return hex_md5(makeKey_19(str_tmp) + makeKey_19(str_tmp) + 'ff31')[3:3+24]
    
    def makeKey_115(str_tmp):
        return hex_md5(makeKey_0(str_tmp) + makeKey_0(str_tmp) + 'ff32')[4:4+24]
    
    def makeKey_116(str_tmp):
        return hex_md5(makeKey_1(str_tmp) + makeKey_1(str_tmp) + 'ff33')[1:1+24]
    
    def makeKey_117(str_tmp):
        return hex_md5(makeKey_4(str_tmp) + makeKey_4(str_tmp) + 'ff34')[2:2+24]
    
    def makeKey_118(str_tmp):
        return hex_md5(makeKey_5(str_tmp) + makeKey_15(str_tmp) + 'ff35')[3:3+24]
    
    def makeKey_119(str_tmp):
        return hex_md5(makeKey_3(str_tmp) + makeKey_16(str_tmp) + 'ff36')[1:1+24]
    
    def makeKey_120(str_tmp):
        return hex_md5(makeKey_19(str_tmp) + makeKey_9(str_tmp) + 'ff37')[1:1+24]
    
    def makeKey_121(str_tmp):
        return hex_md5(makeKey_0(str_tmp) + makeKey_10(str_tmp) + 'ssa32')[2:2+24]
    
    def makeKey_252(str_tmp):
        return hex_md5(makeKey_18(str_tmp) + makeKey_2(str_tmp) + 'f2b')[4:4+24]
    
    def makeKey_253(str_tmp):
        return hex_md5(makeKey_19(str_tmp) + makeKey_3(str_tmp) + 'f3b')[1:1+24]
    
    def makeKey_254(str_tmp):
        return hex_md5(makeKey_0(str_tmp) + makeKey_4(str_tmp) + 'f4b')[2:2+24]
    
    def makeKey_255(str_tmp):
        return hex_md5(makeKey_1(str_tmp) + makeKey_5(str_tmp) + 'f5b')[1:1+24]
    
    def makeKey_256(str_tmp):
        return hex_md5(makeKey_4(str_tmp) + makeKey_6(str_tmp) + 'f6b')[2:2+24]
    
    def makeKey_257(str_tmp):
        return hex_md5(makeKey_14(str_tmp) + makeKey_7(str_tmp) + 'c5a17')[3:3+24]
    
    def makeKey_258(str_tmp):
        return hex_md5(makeKey_15(str_tmp) + makeKey_8(str_tmp) + 'c5a18')[4:4+24]
    
    def makeKey_259(str_tmp):
        return hex_md5(makeKey_16(str_tmp) + makeKey_9(str_tmp) + 'c5a19')[1:1+24]
    
    def makeKey_260(str_tmp):
        return hex_md5(makeKey_9(str_tmp) + makeKey_10(str_tmp) + 'c5a20')[2:2+24]
    
    def makeKey_261(str_tmp):
        return hex_md5(makeKey_10(str_tmp) + makeKey_11(str_tmp) + 'c5a21')[3:3+24]
    
    def makeKey_262(str_tmp):
        return hex_md5(makeKey_17(str_tmp) + makeKey_12(str_tmp) + 'c5a22')[2:2+24]
    
    def makeKey_208(str_tmp):
        return hex_md5(makeKey_9(str_tmp) + makeKey_4(str_tmp) + 'xx32')[4:4+24]
    
    def makeKey_209(str_tmp):
        return hex_md5(makeKey_10(str_tmp) + makeKey_5(str_tmp) + 'xx33')[3:3+24]
    
    def makeKey_210(str_tmp):
        return hex_md5(makeKey_17(str_tmp) + makeKey_3(str_tmp) + 'xx34')[4:4+24]
    
    def makeKey_211(str_tmp):
        return hex_md5(makeKey_18(str_tmp) + makeKey_7(str_tmp) + 'xx35')[1:1+24]
    
    def makeKey_212(str_tmp):
        return hex_md5(makeKey_19(str_tmp) + makeKey_3(str_tmp) + 'xx36')[4:4+24]
    
    def makeKey_213(str_tmp):
        return hex_md5(makeKey_0(str_tmp) + makeKey_7(str_tmp) + 'xx37')[1:1+24]
    
    def makeKey_214(str_tmp):
        return hex_md5(makeKey_1(str_tmp) + makeKey_8(str_tmp) + 'xx38')[3:3+24]
    
    def makeKey_215(str_tmp):
        return hex_md5(makeKey_4(str_tmp) + makeKey_14(str_tmp) + 'xx39')[4:4+24]
    
    def makeKey_216(str_tmp):
        return hex_md5(makeKey_19(str_tmp) + makeKey_15(str_tmp) + 'xx40')[1:1+24]
    
    def makeKey_217(str_tmp):
        return hex_md5(makeKey_0(str_tmp) + makeKey_16(str_tmp) + 'xx41')[4:4+24]
    
    def makeKey_218(str_tmp):
        return hex_md5(makeKey_1(str_tmp) + makeKey_9(str_tmp) + 'xx42')[1:1+24]
    
    def makeKey_219(str_tmp):
        return hex_md5(makeKey_4(str_tmp) + makeKey_10(str_tmp) + 'xx43')[2:2+24]
    
    def makeKey_220(str_tmp):
        return hex_md5(makeKey_5(str_tmp) + makeKey_17(str_tmp) + 'xx44')[3:3+24]
    
    def makeKey_221(str_tmp):
        return hex_md5(makeKey_10(str_tmp) + makeKey_1(str_tmp) + 'xx45')[4:4+24]
    
    def makeKey_222(str_tmp):
        return hex_md5(makeKey_17(str_tmp) + makeKey_4(str_tmp) + 'xx46')[3:3+24]
    
    def makeKey_223(str_tmp):
        return hex_md5(makeKey_18(str_tmp) + makeKey_19(str_tmp) + 'xx47')[4:4+24]
    
    def makeKey_224(str_tmp):
        return hex_md5(makeKey_19(str_tmp) + makeKey_0(str_tmp) + 'xx48')[3:3+24]
    
    def makeKey_225(str_tmp):
        return hex_md5(makeKey_0(str_tmp) + makeKey_1(str_tmp) + 'xx49')[4:4+24]
    
    def makeKey_226(str_tmp):
        return hex_md5(makeKey_1(str_tmp) + makeKey_4(str_tmp) + 'xx50')[3:3+24]
    
    def makeKey_227(str_tmp):
        return hex_md5(makeKey_4(str_tmp) + makeKey_14(str_tmp) + 'xx51')[4:4+24]
    
    def makeKey_228(str_tmp):
        return hex_md5(makeKey_5(str_tmp) + makeKey_15(str_tmp) + 'xx52')[1:1+24]
    
    def makeKey_229(str_tmp):
        return hex_md5(makeKey_3(str_tmp) + makeKey_16(str_tmp) + 'wsn53')[2:2+24]
    
    def makeKey_230(str_tmp):
        return hex_md5(makeKey_18(str_tmp) + makeKey_0(str_tmp) + 'wsn54')[1:1+24]
    
    def makeKey_263(str_tmp):
        return hex_md5(makeKey_18(str_tmp) + makeKey_13(str_tmp) + 'c5a23')[3:3+24]
    
    def makeKey_264(str_tmp):
        return hex_md5(makeKey_19(str_tmp) + makeKey_14(str_tmp) + 'c5a24')[4:4+24]
    
    def makeKey_265(str_tmp):
        return hex_md5(makeKey_0(str_tmp) + makeKey_15(str_tmp) + 'c5a25')[1:1+24]
    
    def makeKey_266(str_tmp):
        return hex_md5(makeKey_1(str_tmp) + makeKey_16(str_tmp) + 'c5a28')[2:2+24]
    
    def makeKey_267(str_tmp):
        return hex_md5(makeKey_4(str_tmp) + makeKey_17(str_tmp) + 'c5a29')[3:3+24]
    
    def makeKey_268(str_tmp):
        return hex_md5(makeKey_19(str_tmp) + makeKey_18(str_tmp) + 'c5a30')[4:4+24]
    
    def makeKey_269(str_tmp):
        return hex_md5(makeKey_0(str_tmp) + makeKey_19(str_tmp) + 'c5a31')[1:1+24]
    
    def makeKey_270(str_tmp):
        return hex_md5(makeKey_1(str_tmp) + makeKey_1(str_tmp) + 'c5a32')[2:2+24]
    
    def makeKey_271(str_tmp):
        return hex_md5(makeKey_4(str_tmp) + makeKey_4(str_tmp) + 'c5a33')[3:3+24]
    
    def makeKey_272(str_tmp):
        return hex_md5(makeKey_5(str_tmp) + makeKey_19(str_tmp) + 'c5a34')[4:4+24]
    
    def makeKey_273(str_tmp):
        return hex_md5(makeKey_5(str_tmp) + makeKey_0(str_tmp) + 'c5a35')[3:3+24]
    
    def makeKey_274(str_tmp):
        return hex_md5(makeKey_3(str_tmp) + makeKey_1(str_tmp) + 'f1b')[4:4+24]
    
    def makeKey_275(str_tmp):
        return hex_md5(makeKey_3(str_tmp) + makeKey_4(str_tmp) + 'f2b')[1:1+24]
    
    def makeKey_276(str_tmp):
        return hex_md5(makeKey_7(str_tmp) + makeKey_5(str_tmp) + 'f3b')[2:2+24]
    
    def makeKey_277(str_tmp):
        return hex_md5(makeKey_16(str_tmp) + makeKey_5(str_tmp) + 'f2b')[1:1+24]
    
    def makeKey_278(str_tmp):
        return hex_md5(makeKey_17(str_tmp) + makeKey_3(str_tmp) + 'f3b')[2:2+24]
    
    def makeKey_279(str_tmp):
        return hex_md5(makeKey_18(str_tmp) + makeKey_3(str_tmp) + 'f4b')[3:3+24]
    
    def makeKey_280(str_tmp):
        return hex_md5(makeKey_19(str_tmp) + makeKey_17(str_tmp) + 'f5b')[4:4+24]
    
    def makeKey_122(str_tmp):
        return hex_md5(makeKey_1(str_tmp) + makeKey_17(str_tmp) + 'ssa33')[3:3+24]
    
    def makeKey_123(str_tmp):
        return hex_md5(makeKey_4(str_tmp) + makeKey_18(str_tmp) + 'ssa34')[4:4+24]
    
    def makeKey_124(str_tmp):
        return hex_md5(makeKey_5(str_tmp) + makeKey_19(str_tmp) + 'ssa35')[1:1+24]
    
    def makeKey_198(str_tmp):
        return hex_md5(makeKey_3(str_tmp) + makeKey_9(str_tmp) + 'aa5')[1:1+24]
    
    def makeKey_199(str_tmp):
        return hex_md5(makeKey_7(str_tmp) + makeKey_1(str_tmp) + 'aa6')[2:2+24]
    
    def makeKey_200(str_tmp):
        return hex_md5(makeKey_18(str_tmp) + makeKey_0(str_tmp) + 'aa7')[2:2+24]
    
    def makeKey_201(str_tmp):
        return hex_md5(makeKey_19(str_tmp) + makeKey_1(str_tmp) + 'aa8')[3:3+24]
    
    def makeKey_202(str_tmp):
        return hex_md5(makeKey_0(str_tmp) + makeKey_4(str_tmp) + 'aa9')[4:4+24]
    
    def makeKey_203(str_tmp):
        return hex_md5(makeKey_1(str_tmp) + makeKey_5(str_tmp) + 'aa10')[4:4+24]
    
    def makeKey_204(str_tmp):
        return hex_md5(makeKey_4(str_tmp) + makeKey_3(str_tmp) + 'aa11')[1:1+24]
    
    def makeKey_247(str_tmp):
        return hex_md5(makeKey_0(str_tmp) + makeKey_16(str_tmp) + 'c5a32')[1:1+24]
    
    def makeKey_248(str_tmp):
        return hex_md5(makeKey_1(str_tmp) + makeKey_9(str_tmp) + 'c5a33')[2:2+24]
    
    def makeKey_249(str_tmp):
        return hex_md5(makeKey_4(str_tmp) + makeKey_10(str_tmp) + 'c5a34')[3:3+24]
    
    def makeKey_250(str_tmp):
        return hex_md5(makeKey_5(str_tmp) + makeKey_17(str_tmp) + 'c5a35')[4:4+24]
    
    def makeKey_251(str_tmp):
        return hex_md5(makeKey_3(str_tmp) + makeKey_1(str_tmp) + 'f1b')[3:3+24]
    
    def makeKey_281(str_tmp):
        return hex_md5(makeKey_1(str_tmp) + makeKey_18(str_tmp) + 'f6b')[1:1+24]
    
    def makeKey_282(str_tmp):
        return hex_md5(makeKey_4(str_tmp) + makeKey_19(str_tmp) + 'f7b')[2:2+24]
    
    def makeKey_283(str_tmp):
        return hex_md5(makeKey_19(str_tmp) + makeKey_1(str_tmp) + 'f8b')[3:3+24]
    
    def makeKey_284(str_tmp):
        return hex_md5(makeKey_0(str_tmp) + makeKey_4(str_tmp) + 'f9b')[4:4+24]
    
    def makeKey_299(str_tmp):
        return hex_md5(makeKey_3(str_tmp) + makeKey_5(str_tmp) + 'f24b')[1:1+24]
    
    def makeKey_238(str_tmp):
        return hex_md5(makeKey_9(str_tmp) + makeKey_4(str_tmp) + 'c5a23')[3:3+24]
    
    def makeKey_239(str_tmp):
        return hex_md5(makeKey_10(str_tmp) + makeKey_5(str_tmp) + 'c5a24')[1:1+24]
    
    def makeKey_240(str_tmp):
        return hex_md5(makeKey_17(str_tmp) + makeKey_3(str_tmp) + 'c5a25')[2:2+24]
    
    def makeKey_241(str_tmp):
        return hex_md5(makeKey_18(str_tmp) + makeKey_7(str_tmp) + 'c5a26')[3:3+24]
    
    def makeKey_242(str_tmp):
        return hex_md5(makeKey_19(str_tmp) + makeKey_3(str_tmp) + 'c5a27')[4:4+24]
    
    def makeKey_243(str_tmp):
        return hex_md5(makeKey_0(str_tmp) + makeKey_7(str_tmp) + 'c5a28')[1:1+24]
    
    def makeKey_244(str_tmp):
        return hex_md5(makeKey_1(str_tmp) + makeKey_8(str_tmp) + 'c5a29')[2:2+24]
    
    #var cookie = getCookie('vjkl5');
    arrFun = [makeKey_0, makeKey_1, makeKey_2, makeKey_3, makeKey_4, makeKey_5, makeKey_6, makeKey_7, makeKey_8, makeKey_9, makeKey_10, makeKey_11, makeKey_12, makeKey_13, makeKey_14, makeKey_15, makeKey_16, makeKey_17, makeKey_18, makeKey_19, makeKey_20, makeKey_21, makeKey_22, makeKey_23, makeKey_24, makeKey_25, makeKey_26, makeKey_27, makeKey_28, makeKey_29, makeKey_30, makeKey_31, makeKey_32, makeKey_33, makeKey_34, makeKey_35, makeKey_36, makeKey_37, makeKey_38, makeKey_39, makeKey_40, makeKey_41, makeKey_42, makeKey_43, makeKey_44, makeKey_45, makeKey_46, makeKey_47, makeKey_48, makeKey_49, makeKey_50, makeKey_51, makeKey_52, makeKey_53, makeKey_54, makeKey_55, makeKey_56, makeKey_57, makeKey_58, makeKey_59, makeKey_60, makeKey_61, makeKey_62, makeKey_63, makeKey_64, makeKey_65, makeKey_66, makeKey_67, makeKey_68, makeKey_69, makeKey_70, makeKey_71, makeKey_72, makeKey_73, makeKey_74, makeKey_75, makeKey_76, makeKey_77, makeKey_78, makeKey_79, makeKey_80, makeKey_81, makeKey_82, makeKey_83, makeKey_84, makeKey_85, makeKey_86, makeKey_87, makeKey_88, makeKey_89, makeKey_90, makeKey_91, makeKey_92, makeKey_93, makeKey_94, makeKey_95, makeKey_96, makeKey_97, makeKey_98, makeKey_99, makeKey_100, makeKey_101, makeKey_102, makeKey_103, makeKey_104, makeKey_105, makeKey_106, makeKey_107, makeKey_108, makeKey_109, makeKey_110, makeKey_111, makeKey_112, makeKey_113, makeKey_114, makeKey_115, makeKey_116, makeKey_117, makeKey_118, makeKey_119, makeKey_120, makeKey_121, makeKey_122, makeKey_123, makeKey_124, makeKey_125, makeKey_126, makeKey_127, makeKey_128, makeKey_129, makeKey_130, makeKey_131, makeKey_132, makeKey_133, makeKey_134, makeKey_135, makeKey_136, makeKey_137, makeKey_138, makeKey_139, makeKey_140, makeKey_141, makeKey_142, makeKey_143, makeKey_144, makeKey_145, makeKey_146, makeKey_147, makeKey_148, makeKey_149, makeKey_150, makeKey_151, makeKey_152, makeKey_153, makeKey_154, makeKey_155, makeKey_156, makeKey_157, makeKey_158, makeKey_159, makeKey_160, makeKey_161, makeKey_162, makeKey_163, makeKey_164, makeKey_165, makeKey_166, makeKey_167, makeKey_168, makeKey_169, makeKey_170, makeKey_171, makeKey_172, makeKey_173, makeKey_174, makeKey_175, makeKey_176, makeKey_177, makeKey_178, makeKey_179, makeKey_180, makeKey_181, makeKey_182, makeKey_183, makeKey_184, makeKey_185, makeKey_186, makeKey_187, makeKey_188, makeKey_189, makeKey_190, makeKey_191, makeKey_192, makeKey_193, makeKey_194, makeKey_195, makeKey_196, makeKey_197, makeKey_198, makeKey_199, makeKey_200, makeKey_201, makeKey_202, makeKey_203, makeKey_204, makeKey_205, makeKey_206, makeKey_207, makeKey_208, makeKey_209, makeKey_210, makeKey_211, makeKey_212, makeKey_213, makeKey_214, makeKey_215, makeKey_216, makeKey_217, makeKey_218, makeKey_219, makeKey_220, makeKey_221, makeKey_222, makeKey_223, makeKey_224, makeKey_225, makeKey_226, makeKey_227, makeKey_228, makeKey_229, makeKey_230, makeKey_231, makeKey_232, makeKey_233, makeKey_234, makeKey_235, makeKey_236, makeKey_237, makeKey_238, makeKey_239, makeKey_240, makeKey_241, makeKey_242, makeKey_243, makeKey_244, makeKey_245, makeKey_246, makeKey_247, makeKey_248, makeKey_249, makeKey_250, makeKey_251, makeKey_252, makeKey_253, makeKey_254, makeKey_255, makeKey_256, makeKey_257, makeKey_258, makeKey_259, makeKey_260, makeKey_261, makeKey_262, makeKey_263, makeKey_264, makeKey_265, makeKey_266, makeKey_267, makeKey_268, makeKey_269, makeKey_270, makeKey_271, makeKey_272, makeKey_273, makeKey_274, makeKey_275, makeKey_276, makeKey_277, makeKey_278, makeKey_279, makeKey_280, makeKey_281, makeKey_282, makeKey_283, makeKey_284, makeKey_285, makeKey_286, makeKey_287, makeKey_288, makeKey_289, makeKey_290, makeKey_291, makeKey_292, makeKey_293, makeKey_294, makeKey_295, makeKey_296, makeKey_297, makeKey_298, makeKey_299];
    funIndex = strToLong(cookie) % len(arrFun)
    fun = arrFun[funIndex]
    result = fun(cookie)
    return result

