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


def fill_forms(driver, search_location, start_date, end_date):
    search_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "e57ffa4eb5")))
    search_input = driver.find_element(By.NAME, "ss")
    search_input.send_keys(search_location)

    try:
        show_calendar = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//button[@data-testid='date-display-field-start']")))
    except:
        show_calendar = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='sb-date-field__display']")))

    show_calendar.click()

    print(start_date, end_date)
    day_in = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, f"//span[@data-date='{start_date}']")))
    day_in.click()

    day_out = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, f"//span[@data-date='{end_date}']")))
    day_out.click()
    search_button.click()


def get_url_results(driver):
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.LINK_TEXT, "Pesquisar resultados")))
    url_results = driver.current_url
    return url_results


def get_competitors(url_location, min_pax, max_pax):
    property_by_date_list = []

    for adults in range(min_pax, max_pax):
        property_by_adults_list = []
        offset = 0
        pages = 1

        while offset/25 < pages:
            new_sufix = f'group_adults={adults}&no_rooms=1&group_children=0&sb_travel_purpose=leisure&offset={str(offset)}'
            new_url = url_location.split('group_adults', 1)[0] + new_sufix
            print(new_url)

            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9'}
            response = requests.get(new_url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')

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
    frame.to_csv(f'booking_competitors_feriadao_2', index=False)
    return len(frame)


if __name__ == '__main__':
    url = 'https://www.booking.com/index.pt-br.html?aid=331424&sid=c7aeecaa57fb939d369a8f0fc5332070&keep_landing=1&sb_price_type=total&'
    search_location = 'Pipa'
    min_pax = 2
    max_pax = 3
    start_date = "2022-10-24"
    end_date = "2022-10-27"
    try:
        driver = prepare_driver(url)
        fill_forms(driver, search_location, start_date, end_date)
        url_location = get_url_results(driver)
        # hotel_results = scrape_results(url_location)
        # hotels_data = export_hotels_data(hotel_results)
        get_competitors(url_location, min_pax, max_pax)
    finally:
        ...
        # driver.quit()


'https://www.booking.com/searchresults.pt-br.html?ss=Pipa&sid=c7aeecaa57fb939d369a8f0fc5332070&aid=331424&lang=pt-br&sb=1&src_elem=sb&src=searchresults&dest_id=-662045&dest_type=city&ac_position=0&ac_click_type=b&ac_langcode=en&ac_suggestion_list_length=5&search_selected=true&search_pageview_id=b3c9090d1ef201f7&ac_meta=GhBiM2M5MDkwZDFlZjIwMWY3IAAoATICZW46BFBpcGFAAEoAUAA%3D&checkin=2022-10-24&checkout=2022-10-27&group_adults=2&no_rooms=1&group_children=0&sb_travel_purpose=leisure&offset=0'