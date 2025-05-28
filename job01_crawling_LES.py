from numpy.f2py.rules import defmod_rules
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from setuptools.package_index import user_agent
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import pandas as pd
import re
import time
import datetime
# 'https://oxylabs.io/blog/how-to-scrape-tripadvisor'에서 추가하라고 한 라이브러리
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup

options = ChromeOptions()
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36'
options.add_argument('user-agent=' + user_agent)
options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
options.add_experimental_option("useAutomationExtension", False)
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('lang=ko-KR')
service = ChromeService(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

hrefs = []
names = []
categories = []
rates = []
review_num = []


# start_url = 'https://www.tripadvisor.co.kr/Attractions-g2023524-Activities-c47-oa0-Chungcheongbuk_do.html'
# driver.get(start_url)
time.sleep(1.5)
Cb_num = 91
Cn_num = 139
Jn_num = 250
DG_num = 74
US_num = 27

driver.get(
    'https://www.tripadvisor.co.kr/Attractions-g1072086-Activities-c47-oa30-Jeollanam_do.html')
time.sleep(1)
driver.execute_script('window.scrollTo(0, document.documentElement.scrollHeight);')
print("광고를 불러 올 때까지 기다림")
time.sleep(5)
#미완성 코드!!! 관광지 섹션이 3회 나올 때마다 광고가 1회 삽입되는 것을 감안해서 반복문의 반복 횟수를 수정하고 조건을 추가해야 합니다!!
for i in range(3, 41):
    try:
        print('{}번째'.format(i))
        name = driver.find_element(By.XPATH,
                                   '//*[@id="lithium-root"]/main/div/div/div[2]/div[2]/div[2]/div[2]/div/div/div[2]/div/div[2]/div/div/section[{}]/div/div/div/div/article/div[2]/header/div/div/div/a[1]/h3/div/span/div'.format(
                                       i)).text
        href = driver.find_element(By.XPATH,
                                   '//*[@id="lithium-root"]/main/div/div/div[2]/div[2]/div[2]/div[2]/div/div/div[2]/div/div[2]/div/div/section[{}]/div/div/div/div/article/div[2]/header/div/div/div/a[1]'.format(
                                       i)).get_attribute('href')
        hrefs.append(href)
        names.append(name)
        category = driver.find_element(By.XPATH,
                                       '//*[@id="lithium-root"]/main/div/div/div[2]/div[2]/div[2]/div[2]/div/div/div[2]/div/div[2]/div/div/section[{}]/div/div/div/div/article/div[2]/div[1]/div[1]/div/div/div[1]'.format(
                                           i)).text
        categories.append(category)
        try:
            rate = driver.find_element(By.XPATH,
                                       '//*[@id="lithium-root"]/main/div/div/div[2]/div[2]/div[2]/div[2]/div/div/div[2]/div/div[2]/div/div/section[{}]/div/div/div/div/article/div[2]/header/div/div/div/a[2]/div/div[1]/div/span/div'.format(
                                           i)).text
            rates.append(rate)
            rev_n = driver.find_element(By.XPATH,
                                        '//*[@id="lithium-root"]/main/div/div/div[2]/div[2]/div[2]/div[2]/div/div/div[2]/div/div[2]/div/div/section[{}]/div/div/div/div/article/div[2]/header/div/div/div/a[2]/div/div[2]'.format(
                                            i)).text
            review_num.append(rev_n)
        except NoSuchElementException:
            print("NoSuchElementException from append!")
            rates.append('NaN')
            review_num.append('0')
    except NoSuchElementException:
        print("NoSuchElementException!")
        names.append('NaN')
        hrefs.append('NaN')
        categories.append('NaN')
        rates.append('NaN')
        review_num.append('0')
    except:
        print("exception!")
    time.sleep(0.2)

next_button_path = '/html/body/div[1]/main/div/div/div[2]/div[2]/div[2]/div[2]/div/div/div[2]/div/div[2]/div/div/section[41]/div/div[1]/div/div[1]/div/div/a'

print(names)
print(hrefs)
print(categories)
print(rates)
print(review_num)

df = pd.DataFrame({'name':names, 'url':hrefs, 'category':categories, 'rate':rates, 'review_num':review_num})
df.info()
df.to_csv('./dataset/LES/Jeonnam/Jeonnam_landmark_list_2.csv', index=False)
