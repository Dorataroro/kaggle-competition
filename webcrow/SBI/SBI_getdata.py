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


# In[2]:


def start(ACCOUNT, PASSWORD, name,DRIVER_PATH):
    option = Options()
    option.add_argument('--headless') 
    #driverの設定
    driver = webdriver.Chrome(executable_path=DRIVER_PATH, chrome_options=options)
    #サイトログイン
    driver = connect_sbi(ACCOUNT, PASSWORD, name,driver)
    return driver


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


# In[ ]:


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


# In[4]:


def set_stock_info(ACCOUNT, PASSWORD, name,DRIVER_PATH,target):
    driver = start(ACCOUNT, PASSWORD, name,DRIVER_PATH)
    result = pd.DataFrame()
    #空実行(これしないと最初の一回なぜか失敗する)
    response = get_stockinfo(driver,9531)

