import base64
import re
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import threading
# import json

def get_cookie_and_ua():
    #先透過selenium，搜尋第一個item，拿回在這個過程中產生的user agent和cookie，讓之後爬的時候可以一直透過session帶著user agent和cookie偽裝
    chrome_options = Options()
    # chrome_options.add_experimental_option("detach", True) # 不自動關閉瀏覽器
    # chrome_options.add_argument(f'user-agent={UserAgent().random}') #操作第一筆時先用隨機生成的user agent來偽裝
    chrome_service = Service(ChromeDriverManager().install())
    chrome_driver = webdriver.Chrome(service=chrome_service, options=chrome_options) # 開啟瀏覽器視窗(Chrome)
    chrome_driver.maximize_window()
    chrome_driver.get(r"https://www.agoda.com/zh-hk/apa-hotel-asakusa-shin-okachimachi-ekimae/hotel/tokyo-jp.html?selectedproperty=31488562&checkIn=2023-09-18&los=1&rooms=1&adults=2&childs=0&cid=1844104&locale=zh-hk&ckuid=18e81307-e884-4f0f-9e13-54be008cea04&prid=0&currency=TWD&correlationId=a6d92fbe-898f-44e7-a91c-8b48e7cab1d7&analyticsSessionId=-2442055940668618202&pageTypeId=1&realLanguageId=7&languageId=7&origin=TW&userId=18e81307-e884-4f0f-9e13-54be008cea04&whitelabelid=1&loginLvl=0&storefrontId=3&currencyId=28&currencyCode=TWD&htmlLanguage=zh-hk&cultureInfoName=zh-hk&machineName=hk-pc-2g-acm-web-user-755cd67449-k7xqj&trafficGroupId=1&sessionId=j1ttncasbm53zofz52s5y5hg&trafficSubGroupId=84&aid=130589&useFullPageLogin=true&cttp=4&isRealUser=true&mode=production&browserFamily=Chrome&checkOut=2023-09-19&children=0&priceCur=TWD&textToSearch=%E6%B7%BA%E8%8D%89%E6%96%B0%E7%A6%A6%E5%BE%92%E7%94%BA%E7%AB%99%E5%89%8DAPA%E9%85%92%E5%BA%97&productType=-1&travellerType=1&familyMode=off")
    chrome_driver.implicitly_wait(20)
    selenium_user_agent = chrome_driver.execute_script("return navigator.userAgent;")
    selenium_cookies = chrome_driver.get_cookies() #這裡面會拿到很多cookie，形式[{cookie1},{cookie2}...]，每一個cookie中有很多訊息描述cookie的屬性
    cookie_dict = {cookie['name']: cookie['value'] for cookie in selenium_cookies}
    return selenium_user_agent, cookie_dict


def get_jjwxc_page(url):
    response = requests.get(url)
    # response.Encoding = 'utf-8'
    print(f'{response.status_code=}')
    if response.status_code == 503:
        print(response.content)
    return response.content

def crawler(html_content):
    soup = BeautifulSoup(html_content, 'lxml')
    print(soup)

    try:
        # 標題
        # title = soup.select('')[0].text.strip()
        price = soup.find('body')
        print(price)

    except Exception as e:
        print(e)
        return None


chrome_options = Options()
chrome_options.add_experimental_option("detach", True) # 不自動關閉瀏覽器
chrome_options.add_argument(f'user-agent={UserAgent().random}') #操作第一筆時先用隨機生成的user agent來偽裝
# user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.3 Safari/605.1.15"
# chrome_options.add_argument(f'user-agent={user_agent}') #操作第一筆時先用隨機生成的user agent來偽裝
chrome_service = Service(ChromeDriverManager().install())
chrome_driver = webdriver.Chrome(service=chrome_service, options=chrome_options) # 開啟瀏覽器視窗(Chrome)
chrome_driver.maximize_window()
# selenium_user_agent, cookie_dict = get_cookie_and_ua()
# session = requests.Session()
# session.headers.update({"user-agent": selenium_user_agent}) 
# session.cookies.update(cookie_dict)
url = "https://www.agoda.com/zh-tw/search?site_id=1731641&campaignid=&searchdatetype=default&lt=3&numberofchildren=0&childages=&gsite=localuniversal&partnercurrency=JPY&roomid=504913968&pricetax=305.75&pricetotal=1761.96&rateplan=&usercountry=TW&userdevice=desktop&verif=false&audience_list=&mcid=332&booking_source=cpc&adtype=0&push_id=CgYIgKaeqAYSBgiAyaOoBhgBILL0gQ8qCioIIgIIASoCCAQ=46e94cfd-c140-9af3-bcc8-0fc068291c33_20230915_16&los=1&adults=2&rooms=1&checkin=2023-09-18&checkout=2023-09-19&currency=TWD&selectedproperty=31488562&city=5085&pslc=1"
chrome_driver.get(url)
chrome_driver.implicitly_wait(60)
wait = WebDriverWait(chrome_driver, 10)
element = wait.until(EC.visibility_of_element_located((By.ID, "")))
html=chrome_driver.page_source
soup = BeautifulSoup(chrome_driver.page_source, 'lxml')
# test = soup.select("#contentContainer > div:nth-child(2) > ol")
test = soup.find("ol", {"class":"hotel-list-container"})
# test = soup.find("#contentContainer")
print(test)
# print(soup.prettify())
# response = session.get(url)



# soup = BeautifulSoup(response.content, "lxml")
# print(soup.prettify())
# test = soup.find("div", attrs={"class":"main-column"})
# # test1 = soup.find("")
# print(test)

# crawler(get_jjwxc_page("https://www.agoda.com/zh-tw/search?site_id=1731641&campaignid=&searchdatetype=default&lt=3&numberofchildren=0&childages=&gsite=localuniversal&partnercurrency=JPY&roomid=504913968&pricetax=305.75&pricetotal=1761.96&rateplan=&usercountry=TW&userdevice=desktop&verif=false&audience_list=&mcid=332&booking_source=cpc&adtype=0&push_id=CgYIgKaeqAYSBgiAyaOoBhgBILL0gQ8qCioIIgIIASoCCAQ=46e94cfd-c140-9af3-bcc8-0fc068291c33_20230915_16&los=1&adults=2&rooms=1&checkin=2023-09-18&checkout=2023-09-19&currency=TWD&selectedproperty=31488562&city=5085&pslc=1"))




        
 


def main():
    items_list = []
    items = crawl_products(get_item_ids())
    threads = []
    for item in items:
        t = threading.Thread(target = soup_item, args=(item, items_list))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    print(len(items_list))
    # insert_into_product(items_list) 



