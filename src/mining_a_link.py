#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Time-stamp: <2013-12-16 16:50:41 Monday by zhangguhua>

# @version 1.0
# @author zhangguhua  zhangguhua@baidu.com  

import threading
import random
import urllib2
import logging
import url_process
import os
import global_val
import linecache
import socket
import re
import thread
from bs4 import *
from logger import *

path = os.path.dirname(os.path.abspath(__file__))
socket.setdefaulttimeout(100)

c_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.76 Safari/537.36","Accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding':"gzip,deflate,sdch"}
i_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko", "Accept":"text/html, application/xhtml+xml, */*", "Referer":"http://www.baidu.com/s?word=ecom&tn=12092018_15_hao_pg&ie=utf-8" }
o_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36 OPR/17.0.1241.53", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8", "Referer":"http://www.baidu.com/s?wd=ecom&rsv_bp=0&ch=&tn=baidu&bar=&rsv_spt=3&ie=utf-8&rsv_sug3=4&rsv_sug1=4&rsv_sug4=92&oq=ces"}
f_headers = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "Accept-Language":"zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3", "Accept-Encoding":"gzip, deflate"}


headerslist = [c_headers, i_headers, o_headers, f_headers]

class mining_a_link(threading.Thread):
    def __init__(self, queue, out_queue, thread_id):
        threading.Thread.__init__(self)
        print thread.get_ident()
        self.queue = queue
        self.out_queue = out_queue
        self.thread_id = thread_id
        proxy_handle = urllib2.ProxyHandler({'http': 'http://127.0.0.1:28510'})

        opener =  urllib2.build_opener(proxy_handle)
        urllib2.install_opener(opener)

        info("%s class init success!" % self.thread_id)
        
        
    def run(self):
        while True:
            #logging.debug('start run')
            line = self.queue.get()
            logging.debug("%s get_item!" % self.thread_id)
            items = line.split('\t')
            if self.crawl_the_url(items[0], line):
                #self.get_the_page_struct_info()
                info(self.thread_id + " start mining "+ items[0])
            self.queue.task_done()
            
            
    def crawl_the_url(self, url, line):
        if global_val.ANALYTICAL_ENGINE == 1:
            try:
                page_content = urllib.urlopen(global_val.url_prefix + url)
                if page_content.getcode() == 503:
                    warning("minig the %s failld ,maybe PA not started!" % url)
                    #self.queue.put(line)
                else:
                    info("%s mining the %s succeed" % (self.thread_id, url))
                    page_content.close()

            except:
                logging.debug('%s urllib2, error timeout:%s' % (self.thread_id, url))
        else:
            try:
                global headerslist
                length = 0
                test = 0
                refresh_url = ''
                while(length == 0 and test <=4 and refresh_url == ''):
                    req = urllib2.Request(url, headers=headerslist[random.randint(0, 3)])
                    page_content = urllib2.urlopen(req)
                    test += 1
                    if page_content.getcode() == 503:
                        warning("%s minig the %s failld ,get 503 error!" % (self.thread_id,  url))
                        page_content.close()
                    else:
                        page_soup = BeautifulSoup(page_content)
                        length = len(page_soup.find_all('a'))
                        if length == 0:
                            refresh_url = self.detect_self_refresh(page_soup)
                            continue
                        for link in page_soup.find_all('a'):
                            get_url = link.get('href')
                            get_url = unicode(get_url)
                            get_url = get_url.encode('utf-8')
                            self.out_queue.put(get_url)
                        info("%s mining the %s succeed use in_engine" % (self.thread_id, url))
                    page_content.close()
                if refresh_url != '':
                    self.out_queue.put(refresh_url)
            except:
                logging.debug('%s urllib, some error mining:%s' % (self.thread_id, url))





    def detect_self_refresh(self, page_soup):
        for i in range(0, len(page_soup('meta'))):
            if page_soup('meta')[i]['http-equiv'] == 'refresh':
                content = page_soup('meta')[i]['content']
                pos = content.find('url=')
                url = content[pos+4:]
                return url
        return ''
    def get_the_page_struct_info(self):
        while True:
            mutex.acquire()
            global_val.lineno += 1
            mutex.release()
            linecache.checkcache(global_val.input_file_name)
            line_info = linecache.getline(global_val.input_file_name, global_val.lineno)
            if not self.process_line(line_info):
                break
            

    def process_line(self, line_info):
        line_info = line_info.strip()
        
        if line_info == '':
            return True
        items = line_info.split('\t')
        if len(items) >= 3:
            if items[-3] == 'COMMLINK' or items[-3] == 'NAVLINK' or items[-3] == 'MYPOSLINK' or items[-3] == 'TURNLINK':
                link = url_process.get_real_url(items[-2], global_val.host)
                if link is not None and url_process.is_in_the_host(link, global_val.host) and link not in global_val.url_filter:
                    filter_mutex.acquire()
                    global_val.url_filter.add(link)
                    filter_mutex.release()
                    link_info = "%s\t%s\t%s\t%s" % (link, global_val.level, items[-3], items[-2])
                    file_mutex.acquire()
                    global_val.output_file.write(link_info +'\n')
                    file_mutex.release()
                    self.out_queue.put(link_info)
                else:
                    return True
            else:
                return True
        elif items[-1] == 'End Crawler...':
            return False
        else:
            return True








