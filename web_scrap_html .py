#!/usr/bin/env python
# coding: utf-8

from bs4 import BeautifulSoup
import pandas as pd
import requests
import sqlite3
import re
from user_agents import parse
from fake_useragent import UserAgent
# from __future__ import division, unicode_literals 
import codecs
import os.path
# from tqdm import tqdm
from os import listdir
from os.path import isfile, join
import datetime
import json

with open('data.json') as json_data:
    d = json.load(json_data)
    json_data.close()

import urllib.request
import urllib.error
import time
def proxy_list():
    
    try:
        Pr_list = []
        time.sleep(1)
        url = "https://free-proxy-list.net/" # the source
        req = urllib.request.Request(url,headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'})
        open_url = urllib.request.urlopen(req)
        data = open_url.read()
        soup = BeautifulSoup(data,'html.parser')
        proxy_data = soup.find_all('tr')
        
        for i in proxy_data:
            Pr = "{0}:{1}".format(BeautifulSoup(str(list(i)[0]),'html.parser').text,BeautifulSoup(str(list(i)[1]),'html.parser').text)
            Pr_list.append(Pr)
        Pr_list.remove(Pr_list[0])
        Pr_list.remove(Pr_list[-1])
        
        print('Find ', len(Pr_list), 'proxies')
        
    except:
        pass
    
    return Pr_list

prxList = proxy_list()

def getPage(CheckPage, proxyDict, prxList):
    header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
      
    if (prxList==[]):
        prxList = proxy_list()
        prxList = list(reversed(prxList))
        prxList = prxList[0:100]
    
    r = ''
    try:
        r = requests.get(CheckPage, proxies=proxyDict, headers=header) 
    except:
         pass
    
    if (str(r)!='<Response [200]>'):
        prx = prxList.pop()
        proxyDict = {'http': prx, 'https': prx}
        soup, r, proxyDict, prxList = getPage(CheckPage, proxyDict, prxList)
    
    data = r.text
    soup = BeautifulSoup(data, 'html.parser') 
    return soup, r, proxyDict, prxList

def get_href_list(prxList):
    href_list = []
    for i in range(2,17):
        url = d['href_for_find_flats'] %str(i)
        s, r, proxyDict, prxList = getPage(url,None,prxList)

        container = s.find(class_= d['name_of_class'])

        for a in container.find_all('a',href=True):
            if d['site_with_hrefs'] in a['href']:
                href_list.append(a['href'])
    return href_list

def get_content(href_list,proxyList):
    pages_pattern = []
    for k in href_list:
        page  = getPage(k,None,prxList)[0]
        pages_pattern.append(page)
    return pages_pattern

def save_htmls(path,save_path=None):
    if save_path == None:
        save_path = d["storage_folder_for_htmls"]
    else: save_path = save_path
    dt = str(datetime.datetime.now())[5:-10]
    i = 0
    for html in pages_pattern:
        html = html.prettify("utf-8")
        href = list(href_list)[i][-10:-1]
        name = '%s_html_version%s_%s' %(i, dt, href) 
        path = save_path+'/'+name+'.html'
        
        with open(path, 'wb') as file:
            file.write(html)
            print(file, 'was saved')
        i = i + 1  

href_list = get_href_list(prxList)
pages = get_content(href_list, proxyList=prxList)
save_htmls(pages)

