#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Time-stamp: <2013-11-26 19:01:43 Tuesday by zhangguhua>

# @version 1.0
# @author zhangguhua  zhangguhua@baidu.com  


this_layer_list = []
next_layer_list = []
url_filter = set()
level = 0
EXPECT_LEVEL = 3
EXPECT_URL_NUMBER = 200000
EXPECT_RUNNING_THREALD = 4
host = ''
lineno = 1
#PA的log文件目录
input_file_name = "/home/work/zhangguhua/page-analyzer/page-analyzer/log/worker.log"
output_file_name = 'url.result'
#配置好的PA的访问环境
url_prefix = "http://dbl-tmpbos-mo284.dbl01.baidu.com:8863/webapp?structpage&siteappid=1&onlyspdebug=1&nocache=1&src="


#配置输出方式为单文件或是输出为每个站点一个文件
OUTPUT_SINGLE_FILE = 0
#输出方式是简单链接，还是加host，还是复杂的方式
#0代表输出 url
#1代表输出 host\turl
#2代表输出 url\tlevel\type\tpattern
#3代表输出 pattern\turl
OUTPUT_FORMAT = 0



#开启挖掘数目判定，当挖掘数目小于阈值的时候会自动挖掘下一层
INTELLIGENT_MINING = 0
INTELLIGENT_THREADHOLD = 15

# 所使用的挖掘网页解析引擎
# 1 为使用PA可以对网页中的js进行解析，速度比较慢需要配置input_filename，与url_prefix
# 2 使用自带的简单引擎解析网页，获取页面谅解
ANALYTICAL_ENGINE = 2
