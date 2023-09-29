import sys, pymysql, datetime, pytz, time, threading, queue
# sys.path.append("..")
from config import DatabaseConfig
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent

connection = pymysql.connect(**DatabaseConfig().db_config)

def get_tracking_request():
    connection = pymysql.connect(**DatabaseConfig().db_config)
    cursor = connection.cursor()
    sql_get_tracking_request = """
        SELECT hotel_name, checkin_date, checkout_date FROM user_request
        WHERE checkin_date >= DATE(CONVERT_TZ(NOW(), 'UTC', '+8:00'))
        GROUP BY hotel_name, checkin_date, checkout_date """
    cursor.execute(sql_get_tracking_request)
    result = cursor.fetchall()
    result_list = [tuple(item.values()) for item in result]
    return result_list

def crawl_single_hotel(hotel_name, checkin_date, checkout_date):
    current_utc_time = datetime.datetime.utcnow()
    crawl_time_utc_8 = current_utc_time.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Taipei'))
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--headless=new")
    # chrome_options.add_experimental_option("detach", True) # 不自動關閉瀏覽器
    chrome_options.add_argument(f'user-agent={UserAgent().random}')
    chrome_options.add_argument('blink-settings=imagesEnabled=false') # 不要載圖片
    # chrome_service = Service(ChromeDriverManager().install())
    chrome_service = Service()
    chrome_driver = webdriver.Chrome(service=chrome_service, options=chrome_options) # 開啟瀏覽器視窗(Chrome)
    url = "https://www.google.com/travel/search"
    chrome_driver.get(url)
    # chrome_driver.maximize_window()

    checkin = chrome_driver.find_element(By.CSS_SELECTOR,'input[jsname="yrriRe"][aria-label="登機報到頁面"]')
    # checkin = WebDriverWait(chrome_driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR,'input[jsname="yrriRe"][aria-label="登機報到頁面"]')))
    chrome_driver.execute_script(f"arguments[0].value = '{checkin_date}';", checkin)
    checkin.send_keys(Keys.ENTER)
    time.sleep(3)

    checkout = WebDriverWait(chrome_driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR,'input[jsname="yrriRe"][aria-label="退房"]')))
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
    hotel_complete_name = soup.find("h1", {"class":"FNkAEc o4k8l"}).text.replace("\n", " ")
    listings = soup.find_all("div",{"class":"zIL9xf xIAdxb"})
    result_list = []
    for listing in listings:
        agency = listing.select("span.NiGhzc")[0].text.replace("\n", " ")
        price = listing.select("span.MW1oTb")[0].text.strip('$').replace(',', '')
        result_list.append((hotel_complete_name, checkin_date, checkout_date, agency, int(price), crawl_time_utc_8))
    chrome_driver.quit()
    return list(set(result_list))

def crawl_all_hotels_from_region(region):
    current_utc_time = datetime.datetime.utcnow()
    crawl_time_utc_8 = current_utc_time.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Taipei'))
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    # chrome_options.add_experimental_option("detach", True) # 不自動關閉瀏覽器
    chrome_options.add_argument(f'user-agent={UserAgent().random}')
    chrome_options.add_argument('blink-settings=imagesEnabled=false')
    chrome_service = Service()
    # chrome_service = Service(ChromeDriverManager().install())
    chrome_driver = webdriver.Chrome(service=chrome_service, options=chrome_options) # 開啟瀏覽器視窗(Chrome)
    url = f"https://www.google.com/travel/search?q={region}"
    chrome_driver.get(url)
    # chrome_driver.maximize_window()
    total_click_change_page = 1
    reset_click_count = 0
    click_max = 100
    # result_list = []
    # next_page_button = WebDriverWait(chrome_driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//button[@class='VfPpkd-LgbsSe VfPpkd-LgbsSe-OWXEXe-INsAgc VfPpkd-LgbsSe-OWXEXe-Bz112c-UbuQg VfPpkd-LgbsSe-OWXEXe-dgl2Hf Rj2Mlf OLiIxf PDpWxe LQeN7 my6Xrf wJjnG dA7Fcf tEQgl']")))
    while True: 
        try:
            # reset_button = WebDriverWait(chrome_driver, 5).until(
            #     EC.element_to_be_clickable((By.XPATH, "//button[@class='VfPpkd-LgbsSe VfPpkd-LgbsSe-OWXEXe-INsAgc VfPpkd-LgbsSe-OWXEXe-dgl2Hf Rj2Mlf OLiIxf PDpWxe P62QJc LQeN7 my6Xrf wJjnG dA7Fcf Pn8YIe undefined']"))
            # )
            reset_button = chrome_driver.find_element(By.XPATH, "//button[@class='VfPpkd-LgbsSe VfPpkd-LgbsSe-OWXEXe-INsAgc VfPpkd-LgbsSe-OWXEXe-dgl2Hf Rj2Mlf OLiIxf PDpWxe P62QJc LQeN7 my6Xrf wJjnG dA7Fcf Pn8YIe undefined']")
            if reset_button.is_displayed():
                if reset_click_count <= 3: 
                    reset_button.click()
                    time.sleep(5)
                    reset_click_count += 1
                    print("click reset")
                    total_click_change_page = 1
                    continue
                else:
                    print("click >3 reset button, shut the cralwer。")
                    break
        except NoSuchElementException:
            pass
        except Exception as e:
            print(f"error: {e}")
            break
        
        try:
            next_page_button = WebDriverWait(chrome_driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//button[@class='VfPpkd-LgbsSe VfPpkd-LgbsSe-OWXEXe-INsAgc VfPpkd-LgbsSe-OWXEXe-Bz112c-UbuQg VfPpkd-LgbsSe-OWXEXe-dgl2Hf Rj2Mlf OLiIxf PDpWxe LQeN7 my6Xrf wJjnG dA7Fcf tEQgl']")))
            soup = BeautifulSoup(chrome_driver.page_source, 'lxml')
            listings = soup.find_all("div",{"class":"jVsyI"})
            for listing in listings:
                try:
                    hotel_complete_name = listing.find("h2",{"jscontroller":"bqejFf"}).text
                except:
                    hotel_complete_name = None
                
                try:
                    price = int(listing.find("span",{"class":"qQOQpe prxS3d"}).text.strip('$').replace(',', ''))
                except:
                    price = None
                
                all_history_set.add((region, hotel_complete_name, price, crawl_time_utc_8))
            next_page_button.click()
            time.sleep(5)
            chrome_driver.implicitly_wait(10)
            total_click_change_page += 1
            print(f"next to page {total_click_change_page}")
        except Exception as e:
            print(f"error: {e}")
            break
    # chrome_driver.quit()
    print(f"total page: {total_click_change_page}")

def insert_single_history_to_db(single_history_list):
    cursor = connection.cursor()
    sql_insert_single_hotel = """
        INSERT INTO history (hotel_name, checkin_date, checkout_date, agency, twd_price, crawl_time) 
        VALUES (%s,%s,%s,%s,%s,%s)"""
    cursor.executemany(sql_insert_single_hotel, single_history_list)
    connection.commit()

def insert_all_history_to_db(all_history_list):
    cursor = connection.cursor()
    sql_insert_all_hotels = """
        INSERT IGNORE INTO all_history (region, hotel_name, twd_price, crawl_time)
        VALUES (%s,%s,%s,%s)"""
    cursor.executemany(sql_insert_all_hotels ,all_history_list)
    connection.commit()


class Crawler(threading.Thread):
    def __init__(self, num):
        threading.Thread.__init__(self)
        self.num = num
    
    def run(self):
        while not crawler_queue.empty():
            user_request = crawler_queue.get()
            self.crawl_single_hotel(*user_request)
    
    def crawl_single_hotel(self, hotel_name, checkin_date, checkout_date):
        current_utc_time = datetime.datetime.utcnow()
        crawl_time_utc_8 = current_utc_time.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Taipei'))
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        # chrome_options.add_experimental_option("detach", True) # 不自動關閉瀏覽器
        chrome_options.add_argument(f'user-agent={UserAgent().random}')
        chrome_options.add_argument('blink-settings=imagesEnabled=false') # 不要載圖片
        # chrome_service = Service(ChromeDriverManager().install())
        chrome_service = Service()
        chrome_driver = webdriver.Chrome(service=chrome_service, options=chrome_options) # 開啟瀏覽器視窗(Chrome)
        url = "https://www.google.com/travel/search"
        chrome_driver.get(url)
        # chrome_driver.maximize_window()

        checkin = chrome_driver.find_element(By.CSS_SELECTOR,'input[jsname="yrriRe"][aria-label="登機報到頁面"]')
        # checkin = WebDriverWait(chrome_driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR,'input[jsname="yrriRe"][aria-label="登機報到頁面"]')))
        chrome_driver.execute_script(f"arguments[0].value = '{checkin_date}';", checkin)
        checkin.send_keys(Keys.ENTER)
        time.sleep(3)

        checkout = WebDriverWait(chrome_driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR,'input[jsname="yrriRe"][aria-label="退房"]')))
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
        hotel_complete_name = soup.find("h1", {"class":"FNkAEc o4k8l"}).text.replace("\n", " ")
        listings = soup.find_all("div",{"class":"zIL9xf xIAdxb"})
        for listing in listings:
            agency = listing.select("span.NiGhzc")[0].text.replace("\n", " ")
            price = listing.select("span.MW1oTb")[0].text.strip('$').replace(',', '')
            single_history_set.add((hotel_complete_name, checkin_date, checkout_date, agency, int(price), crawl_time_utc_8))
        chrome_driver.quit()


if __name__ == "__main__":
    single_history_set = set()
    crawler_queue = queue.Queue()
    user_requests = get_tracking_request()
    for user_request in user_requests:
        crawl_single_hotel(*user_request)
    for user_request in user_requests:
        crawler_queue.put(user_request)
    
    crawlers_list = []
    crawler_count = 5 
    for i in range(crawler_count):
        crawler = Crawler(i+1)
        crawlers_list.append(crawler)
    
    for crawler in crawlers_list:
        crawler.start()
    
    for i in range(crawler_count):
        crawlers_list[i].join()
    single_history_list = list(single_history_set)
    insert_single_history_to_db(single_history_list)
    print("finish crawling single history")
    all_history_set = set()
    crawl_all_hotels_from_region("東京")
    crawl_all_hotels_from_region("大阪")
    # print(all_history_set)
    all_history_list = list(all_history_set)


                                          

