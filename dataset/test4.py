from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import time
import random
import pickle
import logging
from tqdm import tqdm
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crawler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
MAX_RETRIES = 3
SCROLL_PAUSE_TIME = 0.2
BATCH_SIZE = 20
DEFAULT_TIMEOUT = 10


def init_driver():
    options = ChromeOptions()
    # Performance optimizations
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-extensions')
    options.add_argument('--dns-prefetch-disable')
    options.add_argument('--disable-infobars')
    options.page_load_strategy = 'eager'

    # Bot detection evasion
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--disable-blink-features=AutomationControlled")

    try:
        service = ChromeService(ChromeDriverManager(driver_version='135.0.7049.96').install())
        driver = webdriver.Chrome(service=service, options=options)

        # Hide webdriver flag
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                  get: () => undefined
                })
            """
        })

        # Set default timeout
        driver.implicitly_wait(DEFAULT_TIMEOUT)
        return driver
    except Exception as e:
        logger.error(f"Failed to initialize driver: {e}")
        raise


def is_detail_page(driver):
    # 상세 페이지인지 판단하는 핵심 요소가 있는지 확인
    try:
        driver.find_element(By.XPATH,
                            "/html/body/div[1]/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[3]/div/div/button[2]")
        return True
    except NoSuchElementException:
        return False


def is_list_page(driver):
    # 리스트 페이지인지 판단
    try:
        driver.find_element(By.CLASS_NAME, "Nv2PK")  # 검색결과 카드 존재 여부
        return True
    except NoSuchElementException:
        return False


def click_first_result(driver):
    # 검색 결과 리스트에서 첫 번째 결과 클릭
    try:
        first_result = driver.find_elements(By.CLASS_NAME, "Nv2PK")[0]
        first_result.click()
        time.sleep(2)
        return True
    except Exception as e:
        print(f"️검색 결과 클릭 실패: {e}")
        return False


def search_place(driver, place_name):
    # 통합된 검색 및 판단 로직
    driver.get("https://www.google.com/maps")
    time.sleep(1.5)

    search_box = driver.find_element(By.ID, "searchboxinput")
    search_box.clear()
    search_box.send_keys(place_name)
    search_box.send_keys(Keys.ENTER)
    print(f"'{place_name}' 검색 중...")
    time.sleep(3)

    if is_detail_page(driver):
        print(f"'{place_name}' → 바로 상세 페이지 진입")
        return True

    elif is_list_page(driver):
        print(f"'{place_name}' → 검색 결과 리스트 표시됨")
        if click_first_result(driver):
            if is_detail_page(driver):
                print(f"'{place_name}' → 리스트에서 상세 페이지 진입 성공")
                return True
            else:
                print(f"'{place_name}' → 클릭 후에도 상세 페이지 인식 실패")
                return False
        else:
            print(f"'{place_name}' → 첫 결과 클릭 실패")
            return False

    else:
        print(f"'{place_name}' → 상세도 리스트도 아님")
        return False


def click_review_tab(driver):
    try:
        xpath_list = [
            "/html/body/div[1]/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[3]/div/div/button[2]",
            "/html/body/div[1]/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[3]/div/div/button[3]"
        ]

        for xpath in xpath_list:
            try:
                button = driver.find_element(By.XPATH, xpath)
                if "리뷰" in button.text:
                    button.click()
                    print(f"리뷰 탭 클릭 성공: {xpath}")
                    time.sleep(2)
                    return True
            except NoSuchElementException:
                continue

        print("리뷰 탭 버튼이 존재하지 않거나 '리뷰' 탭이 아님")
        return False

    except Exception as e:
        print(f"리뷰 탭 클릭 중 오류 발생: {e}")
        return False


def wait_and_find_element(driver, by, value, timeout=DEFAULT_TIMEOUT):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except TimeoutException:
        return None


def wait_and_find_elements(driver, by, value, timeout=DEFAULT_TIMEOUT):
    try:
        elements = WebDriverWait(driver, timeout).until(
            EC.presence_of_all_elements_located((by, value))
        )
        return elements
    except TimeoutException:
        return []


def scroll_review_section(driver, max_reviews=50):
    try:
        scrollable_div = wait_and_find_element(driver, By.CSS_SELECTOR, 'div.m6QErb.DxyBCb.kA9KIf.dS8AEf')
        if not scrollable_div:
            logger.error("Could not find scrollable review section")
            return False

        last_height = driver.execute_script('return arguments[0].scrollHeight', scrollable_div)
        scroll_attempts = 0
        max_attempts = 20

        while scroll_attempts < max_attempts:
            driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
            time.sleep(SCROLL_PAUSE_TIME)

            new_height = driver.execute_script('return arguments[0].scrollHeight', scrollable_div)
            if new_height == last_height:
                break

            last_height = new_height
            scroll_attempts += 1

            # Check if we have loaded enough reviews
            review_elements = driver.find_elements(By.CLASS_NAME, 'wiI7pd')
            if len(review_elements) >= max_reviews:
                break

        return True
    except Exception as e:
        logger.error(f"Error during scrolling: {e}")
        return False


def extract_reviews(driver, max_reviews=50):
    try:
        review_elements = wait_and_find_elements(driver, By.CLASS_NAME, 'wiI7pd')
        rating_elements = wait_and_find_elements(driver, By.CLASS_NAME, 'kvMYJc')

        if not review_elements or not rating_elements:
            logger.warning("No reviews or ratings found")
            return [], []

        reviews = []
        ratings = []

        for review, rating in zip(review_elements[:max_reviews], rating_elements[:max_reviews]):
            try:
                reviews.append(review.text.strip())
                rating_text = rating.get_attribute('aria-label')
                ratings.append(rating_text if rating_text else None)
            except StaleElementReferenceException:
                continue

        return reviews, ratings
    except Exception as e:
        logger.error(f"Error extracting reviews: {e}")
        return [], []


def collect_reviews_for_place(driver, place_name, max_reviews):
    for attempt in range(MAX_RETRIES):
        try:
            if not click_review_tab(driver):
                logger.warning(f"Failed to click review tab for {place_name} (attempt {attempt + 1}/{MAX_RETRIES})")
                continue

            time.sleep(2)

            if not scroll_review_section(driver, max_reviews):
                logger.warning(f"Failed to scroll reviews for {place_name} (attempt {attempt + 1}/{MAX_RETRIES})")
                continue

            reviews, ratings = extract_reviews(driver, max_reviews)

            if reviews and ratings:
                return reviews, ratings

        except Exception as e:
            logger.error(f"Error collecting reviews for {place_name} (attempt {attempt + 1}/{MAX_RETRIES}): {e}")

        time.sleep(random.uniform(1, 2))

    return [], []


def process_place_batch(place_names):
    driver = None
    results = []

    try:
        driver = init_driver()

        for place in place_names:
            try:
                logger.info(f"Searching for '{place}'...")
                success = search_place(driver, place)
                time.sleep(random.uniform(1.5, 2.5))

                if success:
                    reviews, ratings = collect_reviews_for_place(driver, place, max_reviews=50)
                    results.append({
                        'name': place,
                        'reviews': ' '.join(reviews) if reviews else "?",
                        'ratings': ' '.join(ratings) if ratings else "?"
                    })
                else:
                    results.append({
                        'name': place,
                        'reviews': "?",
                        'ratings': "?"
                    })
            except Exception as e:
                logger.error(f"Error processing place '{place}': {e}")
                results.append({
                    'name': place,
                    'reviews': "?",
                    'ratings': "?"
                })
    finally:
        if driver:
            driver.quit()

    return results


def ensure_directory_exists(file_path):
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Created directory: {directory}")


def save_results(results, region_name):
    try:
        # Create base directories
        dataset_dir = "./dataset"
        pickle_dir = os.path.join(dataset_dir, region_name)
        reviews_dir = os.path.join(dataset_dir, "KMJ", "google_maps_reviews")

        # Ensure directories exist
        for directory in [dataset_dir, pickle_dir, reviews_dir]:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Ensuring directory exists: {directory}")

        # Save to pickle
        reviews = [r['reviews'] for r in results]
        ratings = [r['ratings'] for r in results]
        names = [r['name'] for r in results]

        pickle_reviews_path = os.path.join(pickle_dir, f"{region_name}_reviews.pickle")
        pickle_ratings_path = os.path.join(pickle_dir, f"{region_name}_ratings.pickle")

        with open(pickle_reviews_path, 'wb') as f:
            pickle.dump(reviews, f)
        with open(pickle_ratings_path, 'wb') as f:
            pickle.dump(ratings, f)

        # Save to CSV
        df_out = pd.DataFrame(results)
        csv_path = os.path.join(reviews_dir, f"{region_name}_reviews.csv")
        df_out.to_csv(csv_path, index=False, encoding='utf-8-sig')
        logger.info(f"Results saved to {csv_path}")

    except Exception as e:
        logger.error(f"Error saving results: {e}")
        raise

# 아래 지역 이름을 수정해야 합니다.
def main():
    region_name = "Gangwon-do"  # Change this for different regions

    try:
        # 아래 폴더 위치와 파일 명을 바꿔 주셔야 합니다.
        df = pd.read_csv("./dataset/KMJ/Gangwon-do_landmark_list_final.csv")
        place_names = df["name"].tolist()
        logger.info(f"Loaded {len(place_names)} places to process")

        # Process places in batches
        all_results = []
        for i in tqdm(range(0, len(place_names), BATCH_SIZE), desc="Processing batches"):
            batch = place_names[i:i + BATCH_SIZE]
            results = process_place_batch(batch)
            all_results.extend(results)

            # Save intermediate results
            if i % (BATCH_SIZE * 2) == 0 and i > 0:
                save_results(all_results, f"{region_name}_intermediate_{i}")

        # Save final results
        save_results(all_results, region_name)

    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        raise


if __name__ == "__main__":
    main()