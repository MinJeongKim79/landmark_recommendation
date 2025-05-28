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

# driver 설정
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

time.sleep(1.5)

# 리스트 페이지 URL 지정(oa를 0부터 30의 배수만큼 올림)
driver.get(
    'https://www.tripadvisor.co.kr/Attractions-g1072096-Activities-c47-oa30-Chungcheongnam_do.html')
time.sleep(1)
# 스크롤을 내려야 광고가 생김
driver.execute_script('window.scrollTo(0, document.documentElement.scrollHeight);')
# 광고를 불러 올 때까지 기다림
print("기다리는 중...")
time.sleep(5)
for i in range(3, 41): # 3부터 40번째 section까지 크롤링, 만일 페이지 내 관광지가 30개 미만인 경우 페이지 마지막의 관광지 section의 인덱스를 XPath로 알아내야 함
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
        try: # 평점과 리뷰 갯수
            rate = driver.find_element(By.XPATH,
                                       '//*[@id="lithium-root"]/main/div/div/div[2]/div[2]/div[2]/div[2]/div/div/div[2]/div/div[2]/div/div/section[{}]/div/div/div/div/article/div[2]/header/div/div/div/a[2]/div/div[1]/div/span/div'.format(
                                           i)).text
            rates.append(rate)
            rev_n = driver.find_element(By.XPATH,
                                        '//*[@id="lithium-root"]/main/div/div/div[2]/div[2]/div[2]/div[2]/div/div/div[2]/div/div[2]/div/div/section[{}]/div/div/div/div/article/div[2]/header/div/div/div/a[2]/div/div[2]'.format(
                                            i)).text
            review_num.append(rev_n)
        except NoSuchElementException: # 평점과 리뷰 갯수가 아예 없는 경우
            print("NoSuchElementException from append!")
            rates.append('NaN')
            review_num.append('0')
    except NoSuchElementException: # 해당 섹션이 관광지 정보를 담고 있지 않는 경우(광고인 경우)
        print("NoSuchElementException!")
        names.append('NaN')
        hrefs.append('NaN')
        categories.append('NaN')
        rates.append('NaN')
        review_num.append('0')
    except: # 아무튼 예상치 못한 뭔 일이 난 경우
        print("exception!")
    time.sleep(0.2)

print(names)
print(hrefs)
print(categories)
print(rates)
print(review_num)

df = pd.DataFrame({'name':names, 'url':hrefs, 'category':categories, 'rate':rates, 'review_num':review_num}) # 데이터프레임으로 저장
df.info()
df.to_csv('./dataset/LES/Ulsan/Ulsan_landmark_list_1.csv', index=False) # csv 파일로 저장
