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
import os
import sys
import subprocess


class Booking:
    def __init__(self, search_location, min_pax, max_pax, start_date, end_date, table_name):
        self.url = 'https://www.booking.com'
        self.search_location = search_location
        self.min_pax = min_pax
        self.max_pax = max_pax
        self.start_date = start_date
        self.end_date = end_date

        self.checkin_year = self.start_date.split('-')[0]
        self.checkin_month = self.start_date.split('-')[1]
        self.checkin_monthday = self.start_date.split('-')[2]
        self.checkout_year = self.end_date.split('-')[0]
        self.checkout_month = self.end_date.split('-')[1]
        self.checkout_monthday = self.end_date.split('-')[2]

        self.table_name = table_name
        self.driver = self.prepare_driver()

    def prepare_driver(self):
        print('preparing webdriver')
        driver = webdriver.Chrome()
        driver.get(self.url)
        return driver

    def fill_forms(self):
        print('filling the forms')
        search_input = self.driver.find_element(By.NAME, "ss")
        search_input.send_keys(self.search_location)
        tomorrow = str((datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'))
        day_after_tomorrow = str((datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'))

        try:
            show_calendar = WebDriverWait(self.driver, 2).until(EC.presence_of_element_located((By.XPATH, "//button[@class='d47738b911 fe211c0731 d67d113bc3']")))
        except Exception:
            show_calendar = WebDriverWait(self.driver, 2).until(EC.presence_of_element_located((By.XPATH, "//span[@class='sb-date-field__icon sb-date-field__icon-btn bk-svg-wrapper calendar-restructure-sb']")))
        show_calendar.click()

        try:
            day_in = self.driver.find_element(By.XPATH, f"//span[@data-date='{tomorrow}']")
        except Exception:
            day_in = self.driver.find_element(By.XPATH, f"//td[@data-date='{tomorrow}']")

        try:
            day_out = self.driver.find_element(By.XPATH, f"//span[@data-date='{day_after_tomorrow}']")
        except Exception:
            day_out = self.driver.find_element(By.XPATH, f"//td[@data-date='{day_after_tomorrow}']")
        day_in.click()
        day_out.click()
        try:
            search_button = WebDriverWait(self.driver, 2).until(EC.presence_of_element_located((By.XPATH, "//*[@id='frm']/div[1]/div[4]/div[2]/button")))
        except Exception:
            search_button = WebDriverWait(self.driver, 2).until(EC.presence_of_element_located((By.XPATH, '//*[@id="indexsearch"]/div[2]/div/div/div/form/div[1]/div[4]/button/span')))
        search_button.click()

    def get_url_result(self):
        print('getting url')
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.LINK_TEXT, "Pesquisar resultados")))
            url_result = self.driver.current_url
            return url_result
        except:
            self.driver.quit()

    def get_soup(self, new_url):
        print('preparing the soup')
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9'}
        response = requests.get(new_url, headers=headers)
        return BeautifulSoup(response.content, 'html.parser')

    def hotels_data(self):
        print('getting data')
        property_by_date_list = []
        url = self.get_url_result().split('checkin_year=', 1)[0]

        for adults in range(self.min_pax, self.max_pax):
            print(f'getting data for adults quantity: {adults}')
            property_by_adults_list = []
            offset = 0
            pages = 1

            while offset/25 < pages:
                print(f'page: {int(offset/25+1)}')

                new_sufix = f'checkin_year={self.checkin_year}&checkin_month={self.checkin_month}&checkin_monthday={self.checkin_monthday}&checkout_year={self.checkout_year}&checkout_month={self.checkout_month}&checkout_monthday={self.checkout_monthday}&efdco=1&group_adults={adults}&group_children=0&no_rooms=1&group_children=0&sb_travel_purpose=leisure&offset={str(offset)}'

                new_url = url + new_sufix
                soup = self.get_soup(new_url)

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
                    try:
                        property_by_page['days'] = (item.findAll(
                            attrs={'data-testid': 'price-for-x-nights'})[0].get_text()).split(', ')[0]
                    except Exception:
                        property_by_page['days'] = ''
                    try:
                        property_by_page['adults'] = item.findAll(
                            attrs={'data-testid': 'price-for-x-nights'})[0].get_text().split(', ')[1]
                    except Exception:
                        property_by_page['adults'] = ''
                    try:
                        property_by_page['price'] = item.findAll(attrs={'data-testid': 'price-and-discounted-price'})[0].get_text()
                    except Exception:
                        property_by_page['price'] = ''

                    property_by_adults_list.append(property_by_page)
                offset += 25
            property_by_date_list += property_by_adults_list
            data_table = pd.DataFrame(property_by_date_list)

        data_table.insert(0, 'CheckIn', self.start_date)
        data_table.insert(1, 'CheckOut', self.end_date)
        data_table.to_csv(f'scrap_booking_{self.table_name}', index=False)
        print('scrap done')

    def main(self):
        self.fill_forms()
        self.hotels_data()
        self.driver.quit()


if __name__ == '__main__':
    booking = Booking(
        search_location='Pipa',
        min_pax=2,
        max_pax=7,
        start_date="2023-01-16",
        end_date="2023-01-31",
        table_name="2q-janeiro"
    )
    try:
        booking.main()
    except:
        print("Restarting the program")
        subprocess.call([sys.executable, os.path.realpath(__file__)] + sys.argv[1:])  #restart the program
        booking.main()
