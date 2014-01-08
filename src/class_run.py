#!/usr/bin/env python     
# -*- coding: utf-8 -*-   
# Copyright (c) 2013 zhangguhua <zhangguhua@baidu.com> 


import url_process
import mining_a_link
import sys 
import Queue
import global_val
import string
import os
import time
import commands
from logger import *

host = commands.getoutput("echo $HOSTNAME")
path = os.path.dirname(os.path.abspath(__file__))
error_file_name = path + '/../log/error.log.' + host

this_layer_queue = Queue.Queue()
next_layer_queue = Queue.Queue()
output_file_name = ''
entrance_link = ''

def set_output_file_name(entrance_link):
    """设置输出文件目录和输出文件名"""
    global output_file_name
    run_path = os.path.dirname(os.path.abspath(__file__))
    if global_val.OUTPUT_SINGLE_FILE == 1:
        output_file_name = run_path + '/../data/' + global_val.output_file_name
    else:
        output_file_name = run_path + '/../data/' + 'pattern_url_data_all_' + entrance_link



def test_the_entrance(entrance_link):
    global output_file_name
    code = commands.getoutput("curl -I -m 10 -o /dev/null -s -x 127.0.0.1:28510 -w %{http_code} '"+ entrance_link + "'")
    # code = commands.getoutput("curl -I -m 10 -o /dev/null -s -w %{http_code} '"+ entrance_link + "'")

    if  code.startswith('4') or code.startswith('5') or code == '000':
        error_file = open(error_file_name, 'a')
        error_file.write( entrance_link.lstrip('http://') + '\n')
        error_file.close()
        exit(1)
    else:
        output_file = open(output_file_name, 'a')
        output_file.write(entrance_link.lstrip('http://') + "\t" + "code:" + code  + "\n")
        output_file.close()

        info(entrance_link + "success")
        return code
def prepare_data():
    global entrance_link
    global output_file_name
    global this_layer_queue
    entrance_link = sys.argv[1]
    # link是以http开始的链接，用于挖掘
    # entrance_link是以去除"http://"开始的链接，用于保存文件
    entrance_link, link = url_process.get_entrance_and_link(entrance_link)
    global_val.host = url_process.get_the_host(entrance_link)
    entrance_info = link + "\t"+ link +"\t0\tENTRANCE\t"
    # 设置输出文件的文件名等
    set_output_file_name(entrance_link)
    test_the_entrance(link)

    # 如果使用pa作为页面链接解析，需要设置输入文件
    if global_val.ANALYTICAL_ENGINE == 1:
        read_file = open(global_val.input_file_name, 'w')
        read_file.truncate()
        read_file.close()
    
    this_layer_queue.put(entrance_info)
    global_val.url_filter.add(entrance_link)

def write_result(output_file, info):
    """设置输出文件的格式具体参见配置文档"""
    output_format = global_val.OUTPUT_FORMAT
    items = info.split('\t')
    if output_format == 0:
        output_file.write(items[1] + '\n')
    elif output_format == 1:
        output_file.write(items[0] + '\t' + items[1] + '\n')
    elif output_format == 2:
        output_file.write(items[1] + '\t' + items[4] + '\n')
    elif output_format == 3:
        output_file.write(items[1] + '\n')
    else:
        output_file.write(info)

def get_this_layer_result_in():
    """当使用内部的引擎解析网页时调用的获取下一层方法"""
    global output_file_name
    global next_layer_queue
    global this_layer_queue
    output_file = open(output_file_name, 'a')
    while not next_layer_queue.empty():
        link = next_layer_queue.get()
        if link is None:
            continue
        link = link.strip()
        link = url_process.get_real_url(link, global_val.host)
        if url_process.is_in_the_host(link, global_val.host) and link not in global_val.url_filter:
            global_val.url_filter.add(link)
            this_layer_queue.put(link)
            link_info = "%s\t%s\t%s" % (entrance_link ,link, global_val.level)
            write_result(output_file, link_info)
    output_file.close()
    
def get_this_layer_result_pa():
    """当使用pa作为页面解析的时候获取下一层链接的方法"""
    global output_file_name
    output_file = open(output_file_name, 'a')
    read_file = open(global_val.input_file_name, 'r')
    for line in read_file:
        line_info = line.strip()
        items = line_info.split('\t')
        if len(items) >= 3:
            if items[-3] == 'COMMLINK' or items[-3] == 'NAVLINK' or items[-3] == 'MYPOSLINK' or items[-3] == 'TURNLINK':
                link = url_process.get_real_url(items[-2], global_val.host)
                if link is not None and url_process.is_in_the_host(link, global_val.host) and link not in global_val.url_filter:
                    global_val.url_filter.add(link)
                    link_info = "%s\t%s\t%s\t%s\t%s" % (entrance_link ,link, global_val.level, items[-3], items[-1])
                    write_result(output_file, link_info)
                    next_layer_queue.put(link_info)
                    
    read_file.close()
    read_file = open(global_val.input_file_name, 'w')
    read_file.truncate()
    read_file.close()
    output_file.close()
    
def main():
    reload(sys)                      
    sys.setdefaultencoding('utf-8')     
    prepare_data()
    global this_layer_queue
    global next_layer_queue
    
    temp_queue = Queue.Queue()

    for i in range(global_val.EXPECT_RUNNING_THREALD):
        t = mining_a_link.mining_a_link(temp_queue, next_layer_queue, i)
        t.setDaemon(True)
        t.start()
    while global_val.level <= global_val.EXPECT_LEVEL:
        while this_layer_queue.qsize() != 0:
            for m in range(500):
                if this_layer_queue.qsize() != 0:
                    temp_queue.put(this_layer_queue.get())
                else:
                    break
            temp_queue.join()
            """当使用pa时需要及时获取本层结果"""
            if (global_val.ANALYTICAL_ENGINE == 1):
                get_this_layer_result_pa()
            """没进行一轮需要判断是否满足已挖取足够的链接"""
            if global_val.EXPECT_URL_NUMBER != 0 and len(global_val.url_filter) > global_val.EXPECT_URL_NUMBER:
                print "Mining  %s sucess!" % (global_val.host)
                return
            if global_val.EXPECT_URL_NUMBER != 0 and (len(global_val.url_filter) + next_layer_queue.qsize()*0.3) > global_val.EXPECT_URL_NUMBER:
                get_this_layer_result_in()
                print "Mining  %s sucess!" % (global_val.host)
                return
        if (global_val.ANALYTICAL_ENGINE == 2):
            get_this_layer_result_in()
        if next_layer_queue.qsize() > 0 or this_layer_queue.qsize() > 0:
            global_val.level += 1
            print "level : %d mining sucess!" % (global_val.level -1)
        else:
            break
    print "Mining  %s sucess!" % (global_val.host)
if __name__ == '__main__': 
   main()








