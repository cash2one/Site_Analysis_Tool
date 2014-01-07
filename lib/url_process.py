#!/usr/bin/env python     
# -*- coding: utf-8 -*-   
# Copyright (c) 2013 zhangguhua <zhangguhua@baidu.com> 

import os
import urlparse

class url_process():
    """
    所有关于url处理的函数
    """
    
    #所有资源链接的文件后缀名
    sorce_list = ['3GP', '7Z', 'AAC',' ACE', 'AIF', 'ARJ', 'ASF', 'AVI', 'BIN', 'BZ2', 'EXE', 'GZ', 'GZIP', 'IMG', 'ISO', 'LZH', 'M4A', 'M4V', 'MKV', 'MOV', 'MP3', 'MP4', 'MPA', 'MPE', 'MPEG', 'MPG', 'MSI', 'MSU', 'OGG', 'OGV', 'PDF', 'PLJ', 'PPS', 'PPT', 'QT', 'RAR', 'RM', 'RMVB', 'SEA', 'SIT', 'SITX', 'TAR', 'TIF', 'TIFF', 'WAV', 'WMA', 'WMV', 'ZIP', 'PPT', 'TXT', 'PPTX', 'DOC', 'DOCX', 'JPG', 'JPEG', 'BMP', 'PNG', 'GIF', 'XLS', 'XLSX' ]


    def get_real_url(self, url, base):
        """
        获取一个链接的完整形式，如果一个链接为资源链接，或者ftp下载链接，则不输出
        Args:
            url:需要进行处理的相对url地址
            base:基准地址
        Returns：
            返回链接的完整形式
            None：无法获取完整的链接可能是资源链接，可能是链接不合法
        Raises：
    
        """
        url = url.rstrip('/')
        items = url.split('#')
        url = items[0]
        if "javascript:" in url or "mailto:" in url or "tel:" in url:
            return None
        items = url.split('.')
        if items[-1].upper() in sorce_list:
            return None
            
        if (url.startswith("http://")) or (url.startswith('https://')):
            return url
        elif(url.startswith("ftp://")):
            return url
        elif(url.startswith('//')):
            return "http:"+ url
        else：
            return 'http://' + base + url
    
    
    def get_entrance_and_link(self, links):
        """
        获取程序需要的各种链接形式
        Args:
            url:需要进行处理的相对url地址
            base:基准地址
        Returns：
            返回tuple类型(entrance_link, link)
            entrance_link :代表页面的全连接，以http://开头
            link :是用户输入的链接去掉http://
        Raises：
    
        
        """
        if links.startswith("http://"):
            link = links
            entrance_link = links.lstrip("http://")
        else:
            entrance_link = links
            link = "http://" + links
    
        return entrance_link, link
            
    def is_in_host_str(self, url, host):
        """
        判断一个链接是否属于某一个host下的地址，支持ip地址的判断
        Args:
            url:需要进行处理url地址
            host:host地址
        Returns：
            返回bool型变量
            True: url是该host下的地址
            Flase：url不是该host下的地址
        Raises：
    
        """
        if url is None:
            return False
        if url.startswith("http://"):
            url = url[7:]
        if url.startswith("https://"):
            url = url[8:]
        host = host.lstrip('www.')
            
        items1 = host.split('.')
        
        items2 = url.split('/')
    
        if is_ip_addresss(host):
            if host == items2[0]:
                return True
            else:
                return False
        items3 = items2[0].split('.')
        if len(items3) < 2:
            return False
        if host.endswith('com.cn') and len(items3) >=3:
            if items3[-3] == items1[-3]:
                return True
            else:
                return False
        else:
            if items2[0].endswith(host):
                return True
            else:
                return False
    
    def is_ip_addresss(self, addr):
        """
            判断一个字符串是否是一个合法的ip地址
        Args：
            str：输入需要判断的url地址
        Returns：
            Bool型变量
            True：输入为一个ip地址
            False：输入不是一个ip地址
        Raises:
            无
        """
        url = addr.strip()
        url = url.lstrip("http://")
        items = str.split('.')
        if len(items) != 4:
            return False
        try:
            for item in items:
                if int(item) >= 0 and int(item) <= 255:
                    continue
                else:
                    return False
        except:
            return False
        
    def get_the_host(self, url):
        """
        返回一个url的host地址
        Args:
            url:需要进行处理的url链接
        Returns：
            返回链接的host地址
        Raises：
    
        """
        if url.startswith("http://"):
            url = url[7:]
        if url.startswith("https://"):
            url = url[8:]
        items = url.split('/')
        host = items[0].lstrip('www.')
        return host    
