#!/usr/bin/env python
# coding: utf-8

# In[1]:


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

import os
import time
import datetime
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
#
# Seleniumをあらゆる環境で起動させるオプション
#
options = Options()
options.add_argument('--disable-gpu');
options.add_argument('--disable-extensions');
options.add_argument('--proxy-server="direct://"');
options.add_argument('--proxy-bypass-list=*');
options.add_argument('--start-maximized');

#環境情報色々
DRIVER_PATH = '/Users/hayashiryuutarou/Desktop/study/webcrow/selenium/chromedriver'

#各種Keyの読み込み
import configparser
#config取得
config_ini = configparser.ConfigParser()
config_ini.read('../config.ini', encoding='utf-8')
ACCOUNT = config_ini["SBI"]["ACCOUNT"]
PASSWORD = config_ini["SBI"]["PASSWORD"]
name = config_ini["SBI"]["name"]


# In[2]:


#対象のデータ選定
import pandas as pd
stock_list = pd.read_csv("../../../stock/stocklist.csv")
#とりあえず東証JQGを対象とすることにする
JQG = stock_list.loc[stock_list["市場名"]=="マザーズ"]
#JQG = stock_list


# In[3]:


#ログイン関数
def connect_sbi(ACCOUNT, PASSWORD, name,driver):
    # SBI証券のトップ画面を開く
    driver.get('https://www.sbisec.co.jp/ETGate')
    

    # ユーザーIDとパスワード
    input_user_id = driver.find_element_by_name('user_id')
    input_user_id.send_keys(ACCOUNT)
    input_user_password = driver.find_element_by_name('user_password')
    input_user_password.send_keys(PASSWORD)
    
    # ログインボタンをクリック
    driver.find_element_by_name('ACT_login').click()
    time.sleep(5)

    return driver


# In[4]:


#国内株式全体情報取得関数
def get_stockinfo(driver,stock_code):
    # 検索ボックスに対象のコードを入力

    driver.find_element_by_name('i_stock_sec').send_keys(stock_code)
    #検索ボタンを押下
    driver.execute_script("avaScript:return stockcheck();")
    time.sleep(2)
    #htmlを取得
    html = driver.page_source.encode('utf-8')
    soup = BeautifulSoup(html, "html.parser")

    return soup


# In[5]:


def cl(text):
    text = text.split(u'\xa0')[0]
    if len(text)==0 or text.find("--") >=0: 
        text = 0
    else:
        text = float(text.replace(",",""))
    return text


# In[6]:


def cl2(text):
    text = text.split(u'\xa0')[0]
    if len(text)==0 or text.find("--") >=0: 
        text = 0
    else:
        text = float(text.replace(",",""))
    return text


# In[7]:


def cl3(text):
    text = text.split(u'\xa0')[1]
    if len(text)==0 or text.find("--") >=0: 
        text = 0
    else:
        text = float(text.replace(",","").split("↑")[0].split("↓")[0].replace(",",""))
    return text


# In[8]:


#詳細情報の取得
def get_currentprice(soup,code):
    #現在価格
    found1 = soup.find('div', class_='kabuNowStatus')
    current_price = cl3(found1.find("td",id="MTB0_0").text)
    #始値,前日終値,高値,出来高,安値,売買代金
    found2 = soup.find('table',class_='tbl690')
    open_price = cl(found2.find('td',id='MTB0_2').text)
    yesterday_price = cl(found2.find("td",id="MTB0_3").text)
    high_price = cl(found2.find("td",id="MTB0_4").text)
    volume = cl(found2.find("td",id="MTB0_5").text)
    low_price = cl(found2.find("td",id="MTB0_6").text)
    trading_volume = cl(found2.find("td",id="MTB0_7").text)
    
    #板情報
    found3 = soup.find('div',class_='itaTbl02')
    over = cl2(found3.find("td",id="MTB0_11").text)
    under = cl2(found3.find("td",id="MTB0_76").text)
    sellside_price = cl(found3.find("td",id="MTB0_42").text) 
    buyside_price = cl(found3.find("td",id="MTB0_45").text)
    sellside_atm = 0
    buyside_atm = 0

    #売り気配 ※なぜかギリギリの価格の株数が取得できない
    sellsidedict = {
        cl(found3.find("td",id="MTB0_15").text) :cl(found3.find("td",id="MTB0_14").text),
        cl(found3.find("td",id="MTB0_18").text) :cl(found3.find("td",id="MTB0_17").text),
        cl(found3.find("td",id="MTB0_21").text) :cl(found3.find("td",id="MTB0_20").text), 
        cl(found3.find("td",id="MTB0_24").text) :cl(found3.find("td",id="MTB0_23").text),
        cl(found3.find("td",id="MTB0_27").text) :cl(found3.find("td",id="MTB0_26").text), 
        cl(found3.find("td",id="MTB0_30").text) :cl(found3.find("td",id="MTB0_29").text),
        cl(found3.find("td",id="MTB0_33").text) :cl(found3.find("td",id="MTB0_32").text), 
        cl(found3.find("td",id="MTB0_36").text) :cl(found3.find("td",id="MTB0_35").text),
        cl(found3.find("td",id="MTB0_39").text) :cl(found3.find("td",id="MTB0_38").text)
#        float(found3.find("td",id="MTB0_42").text.split(u'\xa0')[0].replace(",","")) :float(found3.find("td",id="MTB0_43").text.split(u'\xa0')[0].replace(",",""))
    }
    #買い気配
    buysidedict = {
 #       float(found3.find("td",id="MTB0_45").text.split(u'\xa0')[0].replace(",","")) :float(found3.find("td",id="MTB0_46").text.split(u'\xa0')[0].replace(",","")), 
        cl(found3.find("td",id="MTB0_48").text) :cl(found3.find("td",id="MTB0_49").text), 
        cl(found3.find("td",id="MTB0_51").text) :cl(found3.find("td",id="MTB0_52").text), 
        cl(found3.find("td",id="MTB0_54").text) :cl(found3.find("td",id="MTB0_55").text), 
        cl(found3.find("td",id="MTB0_57").text) :cl(found3.find("td",id="MTB0_58").text), 
        cl(found3.find("td",id="MTB0_60").text) :cl(found3.find("td",id="MTB0_61").text), 
        cl(found3.find("td",id="MTB0_63").text) :cl(found3.find("td",id="MTB0_64").text), 
        cl(found3.find("td",id="MTB0_66").text) :cl(found3.find("td",id="MTB0_67").text), 
        cl(found3.find("td",id="MTB0_69").text) :cl(found3.find("td",id="MTB0_70").text), 
        cl(found3.find("td",id="MTB0_72").text) :cl(found3.find("td",id="MTB0_73").text),
    }
    #計算
    for k,v in sellsidedict.items():
        sellside_atm = sellside_atm + (current_price - k)*v
    
    for k,v in buysidedict.items():
        buyside_atm = buyside_atm + (current_price - k)*v
    
    #過去情報
    #found5 = soup.find('div',class_='mgt5')
    #yearly_high_price = int(found5.find('span',class_="fm01").text.split(u'\xa0')[0].replace(",",""))
    
    #投資指標情報
    #per = found2.find("td",id="MTB0_79").text
    
    #まとめたデータ
    now = datetime.datetime.now()
    current_time = str(now.strftime('%Y%m%d %H:%M:%S'))
    columns1 = ["銘柄コード" ,"現在値","始値" ,"前日終値","高値","出来高","安値","売買代金","over","under","sellside_price","buyside_price","板上売気配","板上買気配","現在時刻"]
    data1 = [[code,current_price,open_price,yesterday_price,high_price,volume,low_price,trading_volume,over,under,sellside_price,buyside_price,sellside_atm,buyside_atm,current_time]]
    stock_data = pd.DataFrame(data = data1,columns=columns1)
    return stock_data


# In[9]:


def start():
    option = Options()
    option.add_argument('--headless') 
    #driverの設定
    driver = webdriver.Chrome(executable_path=DRIVER_PATH, chrome_options=options)
    #サイトログイン
    driver = connect_sbi(ACCOUNT, PASSWORD, name,driver)
    return driver


# In[10]:


driver = start()


# In[11]:


result = pd.DataFrame()
#空実行(これしないと最初の一回なぜか失敗する)
response = get_stockinfo(driver,9531)
for i in range(len(JQG)):
    code = JQG["銘柄コード"].iloc[i].astype(str)
    response = get_stockinfo(driver,code)
    if str(response).find("対象銘柄はありません。または、表示できません。") < 0 :
        stock_info = get_currentprice(response,code)
        result = result.append(stock_info,ignore_index = True)


# In[12]:


result.to_csv("stock_result.csv",index=False)


# In[13]:


driver.close()


# In[14]:


#SQL insert
#Postgresqlへのコネクション
import psycopg2 as ps
import configparser

config_ini = configparser.ConfigParser()
config_ini.read('../../../public/psql_local_pass.ini', encoding='utf-8')

host = config_ini["DEFAULT"]["host"]
port = config_ini["DEFAULT"]["port"]
dbname = config_ini["DEFAULT"]["dbname"]
user = config_ini["DEFAULT"]["user"]
password = config_ini["DEFAULT"]["password"]

con = ps.connect("host="+host+" port="+port+" dbname="+dbname+" user="+user+" password="+password)
con.set_client_encoding('utf-8')
#con.cursor_factory=ps.extras.DictCursor
cur = con.cursor()


# In[16]:


import csv
colms = "stock_code,current_price,open_price,yesterday_price,high_price,volume,low_price,trading_volume,over,under,sellside_price,buyside_price,sellside_atm,buyside_atm,get_datetime"
#vals = "1400,161,163,164,163,6400,159,1033,49900,17400,162,161,-57900,46100,'2015'"

with open('stock_result.csv', newline='') as csvfile:
    read = csv.reader(csvfile)
    header = next(read)
    
    for row in read:
        vals = ""
        count = 0
        length = len(row)
        for cell in row:
            if count == (length-1):
                vals = vals + "'"+ str(cell) +"'"
                break
            else:
                count = count +1
                vals = vals + str(cell) + ","
        sql = "INSERT INTO stock_detail ("  + colms +  ") VALUES(" + vals + ")"
        cur.execute(sql)
con.commit()


# In[17]:


cur.close()
con.close()

