#!/usr/bin/env python
# coding: utf-8

# In[1]:


from __future__ import division, unicode_literals 
import os.path
from os import listdir
from os.path import isfile, join
from bs4 import BeautifulSoup
import pandas as pd
import requests
import sqlite3
import re
from user_agents import parse
from fake_useragent import UserAgent
import codecs
import datetime
import json


# In[2]:


with open('data.json') as json_data:
    d = json.load(json_data)
    json_data.close()


# In[3]:


def clean(text):
    return text.replace('\n','').replace(' ','')


# In[4]:


def div_up(myString):
    ll = []
    val = ''
    for ch in myString:
        if ch.isupper():
            ll.append(val)
            val = ''
        val += ch
    return ll[1:]


# In[5]:


def get_qm(qm):    
    general_qm,living_qm,kitchen_qm,floor,count_floors,year_build = None,None,None,None,None,None
    try:
        ch_list = [clean(i.text) for i in qm.findChildren()]
        if 'Общая' and 'м²' not in ch_list[0]:
            i = 4
        else: i =3
        if 'Общая' in ch_list:
            general_qm = ch_list[i][:-2]
            i = i+3
        if 'Жилая' in ch_list:
            living_qm = ch_list[i][:-2]
            i = i+3
        if 'Кухня' in ch_list:
            kitchen_qm = ch_list[i][:-2]
            i = i+3
        if 'Этаж' in ch_list:
            l_floor = ch_list[i].split('из')
            i = i+3
            floor = (l_floor[0])
            count_floors = l_floor[1]
        if 'Построен' in ch_list:
            year_build = ch_list[i]
            i = i+3
    except:pass
    return general_qm,living_qm,kitchen_qm,floor,count_floors,year_build


# In[6]:


def get_commit(qm):
    commit = None
    try:
        for el in [i.text for i in qm.findChildren()]:
            if len(clean(el)) > 10:
                commit = el.replace('\n','')
    except:pass
    return commit


# In[7]:


def get_left_right(document):
    left, right =None,None
    body = document.find('body')
    lev1_text_content = list(body.children)[13]#change 11#then change 9 ////13
    lev2_text_content = list(lev1_text_content.children)[3]
    left = list(lev2_text_content.children)[3]
    right = list(lev2_text_content.children)[5]
    return left, right

def get_ud_add_block(left):
    addr_ug_info,qm =None,None
    try:
        head = list(left.find_next())[1]
        qm = list(left.find_next())[5]
        if 'ЖК' in list(head.find_next().find_next().contents)[3].text:
            addr_ug_info = list(head.find_next().find_next().contents)[5]
        else:
            addr_ug_info = list(head.find_next().find_next().contents)[3]
    except:pass
    return addr_ug_info,qm

def get_address(addr_ug_info):
    addr=None
    try:
        addr = [i.text for i in (addr_ug_info.find_next()).find_next().findChildren()]
        addr = [clean(i) for i in addr]
        addr = addr[:-1]
        addr = ','.join(addr)
    except:pass
    return addr

def get_ug(addr_ug_info):
    walDistUG,nearestStation,timeToNearStation = None,None,None
    try:
        ug = (addr_ug_info.contents)[5].text
        undGrCont = ug.replace('\n','').replace(' ','')
        undGrCont_split = undGrCont.split('⋅') 
        nearestStation = undGrCont_split[0]
        timeToNearStation = int(re.findall('(\d+)', undGrCont_split[1])[0])

        if 'пешком' in undGrCont_split[1]:   
            nearestStation = undGrCont_split[0]
            walDistUG = True
        else:
            walDistUG = False
    except:pass
    return walDistUG,nearestStation,timeToNearStation


# In[8]:


def get_сommon_info(left):
    with_child,with_animal,lift,balcony,fridge =  None,None,None,None,None
    dishwasher,washer,furniture_room = None,None,None
    furniture_kitchen,conditioning,television =  None,None,None
    internet,phone,bath,parking,wc =  None,None,None,None, None
    try:
        try:
            parametres = (list(left.children)[3]).findChildren()[15].findChildren()
            metadate = [parametre.text for parametre in parametres]
            metadate = [clean(i) for i in metadate]

            if metadate[0] == 'Общаяинформация':
                with_child_i = 0
                if 'Можносдетьми' in metadate[1]:
                    with_child = True
                    with_child_i = 1
                else: 
                    with_child = False
                if 'Можносживотными' in metadate[1]:
                    with_animal = True
                    with_child_i = 2
                else: 
                    with_animal = False

            genetal_inf = metadate[1+with_child_i]
            list_general_inf = div_up(genetal_inf)  
        except:
            parametres = (list(left.children)[3]).findChildren()[18].findChildren()
            metadate = [parametre.text for parametre in parametres]
            metadate = [clean(i) for i in metadate]

            if metadate[0] == 'Общаяинформация':
                with_child_i = 0
                if 'Можносдетьми' in metadate[1]:
                    with_child = True
                    with_child_i = 1
                else: 
                    with_child = False
                if 'Можносживотными' in metadate[1]:
                    with_animal = True
                    with_child_i = 2
                else: 
                    with_animal = False

            genetal_inf = metadate[1+with_child_i]
            list_general_inf = div_up(genetal_inf)  
        if 'Пассажирскийлифт'or'Лифт'or'Грузовойлифт' in genetal_inf:
            lift = True
        else: lift = False
        if  'Балкон'or'Лоджия'  in genetal_inf:
            balcony = True
        else: balcony = False
        if  'Холодильник'  in genetal_inf:
            fridge = True
        else: fridge = False    
        if  'Посудомоечнаямашина'  in genetal_inf:
            dishwasher = True
        else: dishwasher = False    
        if  'Стиральнаямашина'  in genetal_inf:
            washer = True
        else: washer = False
        if  'Мебельвкомнатах' in genetal_inf:
            furniture_room = True
        else: furniture_room = False    
        if  'Мебельнакухне' in genetal_inf:
            furniture_kitchen = True
        else: furniture_kitchen = False
        if  'Кондиционер' in genetal_inf:
            conditioning = True
        else: conditioning = False
        if  'Телевизор' in genetal_inf:
            television = True
        else: television = False    
        if  'Интернет' in genetal_inf:
            internet = True
        else: internet = False    
        if  'Телефон' in genetal_inf:
            phone = True
        else: phone = False    
        if  'Ванна'or'Душеваякабина' in genetal_inf:
            bath = True
        else: bath = False
        if  'Паркинг' or'Надземнаяпарковка'or'Подземнаяпарковка' in genetal_inf:
            parking = True
        else: parking = False
        if  'Туалет' in genetal_inf:
            wc = True
        else: wc = False  
    except:pass
    return [with_child,with_animal,lift,balcony,fridge,dishwasher,washer,furniture_room,
            furniture_kitchen,conditioning,television,internet,phone,bath,parking,wc]


# In[9]:


def get_price(right):
    try:
        price = None
        price = clean(right.find('span').text.replace('\xa0',''))[:-6]
    except:pass
    return price


# In[10]:


def get_money_feature(right):
    try:
        is_deposit,is_commission,commission,is_prepay = None,None,None,None
        list_pr = []
        for i in [el for el in right.findChildren()]:
            if 'комиссия' or 'безкомиссии' in i.text:
                list_pr.append(clean(i.text))
        list_pr = list_pr[-1].replace('\xa0','')
        if 'Беззалога' in str_all_price:
            is_deposit = False
        else: 
            is_deposit = True
        if 'безкомиссии' in str_all_price:
            is_commission = False
        else: 
            is_commission = True
            commission = str_all_price.split(',')[1][8:-1]
        if 'безпредоплаты' in str_all_price:
            is_prepay = False
        else: 
            is_prepay = True
    except:pass
    return is_deposit,is_commission,commission,is_prepay


# In[11]:


def get_count_room(left):
    count_room=None
    try:
        for_search_count_room = [el.text for el in left.findChildren()]
        count_list = []
        for i in for_search_count_room:
            if 'Количество комнат' in i:
                count_list.append(i)
        count_room = clean(count_list[-2]).replace('Количествокомнат','')
    except:pass
    return count_room


# In[21]:


def get_df():
    mypath=d['way_storage_folder_for_htmls']
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

    # Готовое выкачивание
    df_new = pd.DataFrame(columns = ['count_room','general_qm', 'living_qm', 
                                    'kitchen_qm' ,
                            'commit', 'year_build', 'floor','count_floors', 'address', 
                            'metro',
                            'is_walking_metro',
                            'minutes_to_underground',
                            'is_deposit', 'is_commission' ,
                            'commission' , 'is_prepay' ,
                            'lift',
                             'balcony',
                             'fridge',
                             'dishwasher',
                             'washer',
                             'furniture_room',
                             'furniture_kitchen',
                             'conditioning',
                             'television',
                             'internet',
                             'phone',
                             'bath',
                             'parking',
                              'wc',
                             'price','with_child','with_animal' ])
    df_temp = df_new
    # i = 0
    for file_name in onlyfiles:
        try:
            #open html
            name = d['way_storage_folder_for_htmls']+ '/' + file_name
            f=codecs.open(name, 'r', 'utf-8')
            document= BeautifulSoup(f.read())
            f.close()
            if 'Captcha ' in str(document): 
                os.remove(name)
                print(file_name,'delete')
                onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
            else:
                left, right = get_left_right(document)
                addr_ug_info,qm = get_ud_add_block(left)
                addr = get_address(addr_ug_info)
                walDistUG,nearestStation,timeToNearStation = get_ug(addr_ug_info)
                with_child,with_animal,lift,balcony,fridge,dishwasher,washer,furniture_room,furniture_kitchen,conditioning,television,internet,phone,bath,parking,wc = get_сommon_info(left)
                general_qm,living_qm,kitchen_qm,floor,count_floors,year_build = get_qm(qm)
                commit = get_commit(qm)
                is_deposit,is_commission,commission,is_prepay = get_money_feature(right)
                price = get_price(right)
                count_room = get_count_room(left)
                df_new = df_new.append({'count_room':count_room,'general_qm':general_qm,
                                        'living_qm':living_qm, 
                                        'kitchen_qm' :kitchen_qm,
                                        'commit' : commit, 'year_build':year_build, 
                                        'floor':floor,'count_floors':count_floors,'address':addr,
                                        'metro':nearestStation,
                                        'is_walking_metro':walDistUG,
                                        'minutes_to_underground':timeToNearStation,
                                        'is_deposit' : is_deposit, 'is_commission' : is_commission,
                                        'commission' : commission, 'is_prepay' : is_prepay,
                                        'lift':lift,
                                         'balcony':balcony,
                                         'fridge':fridge,
                                         'dishwasher':dishwasher,
                                         'washer':washer,
                                         'furniture_room':furniture_room,
                                         'furniture_kitchen':furniture_kitchen,
                                         'conditioning':conditioning,
                                         'television':television,
                                         'internet':internet,
                                         'phone':phone,
                                         'bath':bath,
                                         'parking':parking,
                                          'wc':wc,'with_child':with_child,'with_animal':with_animal,
                                         'price' : price}, ignore_index = True)
        except:pass
    return df_new


# In[26]:


def save_df(df_new,path=None,name=None):
    if path == None:
        folder = d['folder_csv']
        if name == None:
            dt = str(datetime.datetime.now()).replace(' ','_')[5:-10]
            folder = d['folder_csv']
            name = '/df_version%s.csv' %dt
            path = folder + name 
            df_new.to_csv(name)
        else:
            folder = d['folder_csv']
            name = name 
            path = folder + '/'+ name 
            df_new.to_csv(path)
    else: df_new.to_csv(path)
        name = path
    print(name,'saved')


# In[22]:


df_new = get_df()


# In[27]:


save_df(df_new)

