import math
from bs4 import BeautifulSoup
import requests
import pandas as pd
import re


def get_competitors():
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9'}
    property_by_date_list = []

    for adults in range(2, 7):
        property_by_adults_list = []
        offset = 0
        pages = 1

        while offset/25 < pages:
            URL_BASE = f'https://www.booking.com/searchresults.html?ss=Pipa&ssne=Pipa&ssne_untouched=Pipa&label=gen173nr-1FCAEoggI46AdIM1gEaGyIAQGYATG4AQfIAQzYAQHoAQH4AQKIAgGoAgO4AvTIm_IFwAIB&sid=7101b3fb6caa095b7b974488df1521d2&aid=304142&lang=pt-br&sb=1&src_elem=sb&src=searchresults&dest_id=-662045&dest_type=city&checkin=2022-11-11&checkout=2022-11-14&group_adults={adults}&no_rooms=1&group_children=0&sb_travel_purpose=leisure&offset={str(offset)}'

            response = requests.get(URL_BASE, headers=headers)
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


print(get_competitors())
