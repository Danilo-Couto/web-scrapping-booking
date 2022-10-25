from datetime import datetime, timedelta
import math
from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def prepare_driver(url):
    driver = webdriver.Chrome()
    driver.get(url)
    return driver


def fill_forms(driver, search_location):
    search_input = driver.find_element(By.NAME, "ss")
    search_input.send_keys(search_location)
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    day_after_tomorrow = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')

    try:
        show_calendar = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//button[@class='d47738b911 fe211c0731 d67d113bc3']")))
    except:
        show_calendar = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//span[@class='sb-date-field__icon sb-date-field__icon-btn bk-svg-wrapper calendar-restructure-sb']")))

    show_calendar.click()

    try:
        day_in = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, f"//span[@data-date='{tomorrow}']")))
    except:
        day_in = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, f"//td[@data-date='{tomorrow}']")))

    try:
        day_out = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, f"//span[@data-date='{day_after_tomorrow}']")))
    except:
        day_out = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, f"//td[@data-date='{day_after_tomorrow}']")))
    day_in.click()
    day_out.click()

    try:
        search_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "e57ffa4eb5")))
    except:
        search_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//button[@data-et-click='      customGoal:cCHObTRVDEZRdPQBcGCfTKYCccaT:1 goal:www_index_search_button_click   ']")))
    search_button.click()


def get_url_results(driver):
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.LINK_TEXT, "Pesquisar resultados")))
    url_results = driver.current_url
    return url_results


def hotels_data(url_location, min_pax, max_pax, start_date, end_date):
    property_by_date_list = []

    for adults in range(min_pax, max_pax):
        property_by_adults_list = []
        offset = 0
        pages = 1

        while offset/25 < pages:
            new_sufix = f'&checkin={start_date}&checkout={end_date}&group_adults={adults}&no_rooms=1&group_children=0&sb_travel_purpose=leisure&offset={str(offset)}'
            new_url = url_location.split('checkin=', 1)[0] + new_sufix

            soup = get_soup(new_url)

            checkin = soup.findAll(attrs={'data-testid': 'date-display-field-start'})[0].get_text()
            checkout = soup.findAll(attrs={'data-testid': 'date-display-field-end'})[0].get_text()
            accommodations = int(re.findall(r'\d+', soup.findAll(class_='d3a14d00da')[0].get_text())[0])
            pages = math.ceil(accommodations/25)

            for item in soup.find_all(class_='a1b3f50dcd f7c6687c3d a1f3ecff04 f996d8c258'):
                property_by_page = {}
                property_by_page['name'] = item.findAll(
                    attrs={'data-testid': 'title'})[0].get_text()
                try:
                    property_by_page['rate'] = item.findAll(
                        class_='b5cd09854e d10a6220b4')[0].get_text()
                except Exception:
                    property_by_page['rate'] = ''
                try:
                    property_by_page['evaluations'] = item.findAll(
                        class_='db63693c62')[0].get_text()
                except Exception:
                    property_by_page['evaluations'] = ''
                try:
                    property_by_page['type'] = item.findAll(
                        class_='df597226dd')[0].get_text()
                except Exception:
                    property_by_page['type'] = ''
                property_by_page['dates_and_pax'] = item.findAll(
                    attrs={'data-testid': 'price-for-x-nights'})[0].get_text()
                property_by_page['price'] = item.findAll(
                    attrs={'data-testid': 'price-and-discounted-price'}
                    )[0].get_text()

                property_by_adults_list.append(property_by_page)
            offset += 25

        property_by_date_list += property_by_adults_list
        frame = pd.DataFrame(property_by_date_list)

    frame.insert(0, 'Checkin', checkin[checkin.find(',')+2:])
    frame.insert(1, 'Checkout', checkout[checkout.find(',')+2:])
    frame.to_csv(f'booking_competitors', index=False)
    return len(frame)


def get_soup(new_url):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9'}
    response = requests.get(new_url, headers=headers)
    return BeautifulSoup(response.content, 'html.parser')


if __name__ == '__main__':
    url = 'https://www.booking.com'
    search_location = 'Pipa'
    min_pax = 2
    max_pax = 7
    start_date = "2022-12-30"
    end_date = "2023-01-02"
    try:
        driver = prepare_driver(url)
        fill_forms(driver, search_location)
        url_location = get_url_results(driver)
        hotels_data(url_location, min_pax, max_pax, start_date, end_date)
        driver.quit()
    except:
        driver.quit()
