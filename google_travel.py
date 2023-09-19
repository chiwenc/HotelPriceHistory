import base64
import re
import requests
import pymysql
import time
from config import DatabaseConfig
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent

# connection = pymysql.connect(**DatabaseConfig().db_config)
# cursor = connection.cursor()

def crawl_hotel(hotel_name, checkin_date, checkout_date):
    chrome_options = Options()
    # chrome_options.add_experimental_option("detach", True) # 不自動關閉瀏覽器
    chrome_options.add_argument(f'user-agent={UserAgent().random}')
    chrome_service = Service(ChromeDriverManager().install())
    chrome_driver = webdriver.Chrome(service=chrome_service, options=chrome_options) # 開啟瀏覽器視窗(Chrome)
    url = "https://www.google.com/travel/search"
    chrome_driver.get(url)
    chrome_driver.maximize_window()

    checkin = chrome_driver.find_element(By.CSS_SELECTOR,'input[jsname="yrriRe"][aria-label="登機報到頁面"]')
    # checkin.click()
    # complete_button = WebDriverWait(chrome_driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//button[@jsname='iib5kc']")))
    # complete_button.click()
    chrome_driver.execute_script(f"arguments[0].value = '{checkin_date}';", checkin)
    checkin.send_keys(Keys.ENTER)
    time.sleep(3)

    checkout = WebDriverWait(chrome_driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR,'input[jsname="yrriRe"][aria-label="退房"]')))
    # checkout.click()
    # complete_button = WebDriverWait(chrome_driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//button[@jsname='iib5kc']")))
    # complete_button.click()
    chrome_driver.implicitly_wait(10)
    chrome_driver.execute_script(f"arguments[0].value = '{checkout_date}';", checkout)
    checkout.send_keys(Keys.ENTER)
    time.sleep(3)
    search_box = WebDriverWait(chrome_driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR,'input[jsname="yrriRe"][aria-label="搜尋地點、飯店和其他旅遊內容"]')))
    chrome_driver.execute_script(f"arguments[0].value = '{hotel_name}';", search_box)
    search_box.click()
    first_option = WebDriverWait(chrome_driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//ul[@role='listbox']/li[1]")))
    first_option.click()
    prices_button = WebDriverWait(chrome_driver, 10).until(EC.element_to_be_clickable((By.ID,"prices")))
    prices_button.click()

    soup = BeautifulSoup(chrome_driver.page_source, 'lxml')
    listings = soup.find_all("div",{"class":"zIL9xf xIAdxb"})
    result_list = []
    for listing in listings:
        title = listing.select("span.NiGhzc")[0].text.replace("\n", " ")
        price = listing.select("span.MW1oTb")[0].text.strip('$')
        result_list.append((title,price))
    print(list(set(result_list)))

crawl_hotel("APA酒店〈京成上野車站前","2023/9/26","2023/10/1")
crawl_hotel("上野御徙町相鐵FRESA INN","2023/9/30","2023/10/3")

# sql_insert_history_price = "INSERT INTO history_price (hotel_name, agency, twd_price, time) VALUES (%s,%s,%s,%s)"
# cursor.execute(sql_insert_history_price, )
