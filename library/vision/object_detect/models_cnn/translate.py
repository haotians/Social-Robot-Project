#!/usr/bin/python
#-*- coding:utf-8 -*-
import sys, time
reload(sys)
sys.setdefaultencoding("utf8")

import json                                                                     #导入json模块
import urllib                                                                   #导入urllib模块
from urllib2 import Request, urlopen, URLError, HTTPError                       #导入urllib2模块
import urllib2
import re

API_KEY = '******'
KEYFORM = '******'

def translate_new(inputfile, outputfile, checkfile):
    fin = open(inputfile,'r')
    fcheck = open(checkfile,'r')
    fout = open(outputfile,'w')

    i = 0
    for eachLine in fin:
        i=i+1
        if i < 673:
            continue
        print "processing: ", i, "th item"
        id = eachLine.strip()[0:8]
        line = eachLine.strip()[10:]

        quoteStr = urllib.quote(line)                                   #将读入的每行内容转换成特定的格式进行翻译
        url = 'http://openapi.baidu.com/public/2.0/bmt/translate?client_id=WtzfFYTtXyTocv7wjUrfGR9W&q=' \
              + quoteStr + '&from=en&to=zh'
        try:
            resultPage = urlopen(url)                               #调用百度翻译API进行批量翻译
        except HTTPError as e:
            print('The server couldn\'t fulfill the request.')
            print('Error code: ', e.code)
        except URLError as e:
            print('We failed to reach a server.')
            print('Reason: ', e.reason)
        except Exception, e:
            print 'translate error.'
            print e
            continue
        print "url opened"

        resultJason = resultPage.read().decode('utf-8')                #取得翻译的结果，翻译的结果是json格式
        js = None
        try:
            js = json.loads(resultJason)                           #将json格式的结果转换成Python的字典结构
        except Exception, e:
            print 'loads Json error.'
            print e
            continue

        key = u"trans_result"
        if key in js:
            dst = js["trans_result"][0]["dst"]                     #取得翻译后的文本结果
            outStr = dst
        else:
            outStr = line                                          #如果翻译出错，则输出原来的文本
        print "out: ", outStr
        fout.write(outStr.strip().encode('utf-8') + '\n')          #将结果输出
        time.sleep(0.01)


    fin.close()
    fcheck.close()
    fout.close()

def make_look_up_table(file_in, file_out):
    fin = open(file_in,'r')
    fout = open(file_out,'w')

    i = 0
    for eachLine in fin:

        line = eachLine.strip()

        i = i + 1
        if 11 <= i <= 25:
            outStr = '鸟'
        elif 26 <= i <= 30:
            outStr = '蝾螈'
        elif 31 <= i <= 33:
            outStr = '青蛙'
        elif 34 <= i <= 38:
            outStr = '乌龟'
        elif 39 <= i <= 49:
            outStr = '蜥蜴'
        elif 50 <= i <= 52:
            outStr = '鳄鱼'
        elif 53 <= i <= 69:
            outStr = '蛇'
        elif 73 <= i <= 78:
            outStr = '蜘蛛'
        elif 81 <= i <= 101:
            outStr = '鸟'
        elif 128 <= i <= 147:
            outStr = '鸟'
        elif 152 <= i <= 269:
            outStr = '狗'
        elif 270 <= i <= 273:
            outStr = '狼'
        elif 278 <= i <= 281:
            outStr = '狐狸'
        elif 282 <= i <= 288:
            outStr = '猫'
        else:
            outStr = line

        fout.write(outStr.strip().encode('utf-8') + '\n')          #将结果输出
        time.sleep(0.01)


    fin.close()
    fout.close()


if __name__ == '__main__':
    # translate_new("synset_words.txt", "translation.txt", "test.txt")
    # print GetTranslate("hello").strip("'")
    make_look_up_table('translation.txt',"translation_update.txt")

