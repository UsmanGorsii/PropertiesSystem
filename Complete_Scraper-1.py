#!/usr/bin/python3.7
from time import sleep
import requests
from bs4 import BeautifulSoup
import sys
import pandas as pd
import re
import os
import ProxyDistributor
import SendEmail
from MongoClient import MongoClient
from CategoryMapper import MapCategory

base_directory = os.path.abspath(os.path.dirname(__file__))
# print(base_directory)
web_1_records_scraped = 0
category_mapper = MapCategory()
mongo = MongoClient()
email_string = ""

new_property_email = ""


def append_new_email_string(email_str):
    global new_property_email
    new_property_email += email_str


def write_to_console(text):
    sys.stdout.write("\r" + text)
    sys.stdout.flush()


def display_output(mess):
    print(mess)


def get_file_length(file_name):
    try:
        df_fun = pd.read_csv(file_name)
        ss = len(df_fun['brokerage'].tolist())
    except:
        return 0
    return ss


def append_email_string(email_str):
    global email_string
    email_string += email_str


def append_data(file_name, data_dict_arg):
    p = get_file_length(file_name)
    df = pd.DataFrame(data_dict_arg, index=[p])
    if p == 0:
        df.to_csv(file_name, mode='a+', header=True, encoding='utf-8')
    else:
        df.to_csv(file_name, mode='a+', header=False, encoding='utf-8')


def get_data_from_page_web_1(page_soup_arg, s, brokerage, cat_arg):
    global web_1_records_scraped
    base_url_fun = 'https://www.aurorabeachfront.com'
    listing_list = page_soup_arg.find_all('div', {'class': 'content-box'})

    for property_fun in listing_list:
        data_dict = {"brokerage": brokerage, "url": "", "listing_status": "Sold",
                     "listing_category": "", "listing_title": "",
                     "price_prefix": "", "price": "",
                     "listing_id": "", "bedrooms": "", "bathrooms": "", "interior_sqr_ft": "",
                     "exterior_sqr_ft": "", "listing_agent_name": "",
                     "listing_agent_link": "", "mobile_text": "",
                     "listing_agent_image": "", "overview": "", "us_phone_number": "", "office": "", "email": "",
                     "images": "",
                     "description": "", "headline": "", "state": "Nicaragua", "location": "",
                     "land_area_in_meters": "",
                     "total_area_mt_sqr": "", "total_area_sq_ft": "", "total_area": "", "year_built": "",
                     "view": "",
                     "amenities": ""}

        status = "For Sale"
        try:
            status = property_fun.find('div', {'class': 'pstatus'}).text.strip()
        except:
            pass
        if 'sold' not in status.lower() and len(status) > 2:
            status = "For Sale"
        else:
            status = "Sold"
        data_dict['listing_status'] = status
        data_dict['listing_category'] = category_mapper.map_category(cat_arg)
        propert_url = base_url_fun + property_fun.find('a', {'class': 'job_listing-clickbox'})['href']
        error_num = 3
        while True:
            try:
                response = s.get(propert_url)
                break
            except Exception as e:
                print(e, "Internet Issue Brokerage:", brokerage)
                if error_num <= 0:
                    error_num = 3
                    proxies = ProxyDistributor.get_available_proxy()
                    s.proxies.update(proxies)
                sleep(1)
                pass

        soup_fun = BeautifulSoup(response.text, "html.parser")
        data_dict['url'] = propert_url
        # print(propert_url)
        try:
            images_list = []
            images_soup = soup_fun.find('div', {"class": "fotorama"}).find_all("img")
            for img_soup in images_soup:
                images_list.append(img_soup['src'])

            data_dict['images'] = ",".join(images_list)
        except:
            data_dict['images'] = []
        try:
            title_soup = soup_fun.find('h1', {'class': 'widget-title widget-title-job_listing'})
            data_dict['listing_title'] = title_soup.find('span').text.strip()
        except:
            pass
        try:
            price_text = soup_fun.find('meta', {'property': "og:price:amount"})['content']
            data_dict['price'] = price_text
            data_dict['price_prefix'] = soup_fun.find('meta', {'property': "og:price:currency"})['content']
        except:
            pass
        try:
            overview_soup = soup_fun.find('main').find_all('aside',
                                                               {'id': 'listify_widget_panel_listing_content-2'})
            data_dict['overview'] = overview_soup[0].find_all('div')[1].text.replace('\xa0', '').strip()
        except:
            pass

        try:
            data_dict['us_phone_number'] = soup_fun.find("a", string=lambda x: x and 'USA Phone:' in x).text.replace('USA Phone: ', '').strip()
        except:
            pass
        try:
            data_dict['office'] = soup_fun.find("a", string=lambda x: x and 'NICA Phone:' in x).text.replace('NICA Phone: ', '').strip()
        except:
            pass
        try:
            data_dict['email'] = soup_fun.find("a", string=lambda x: x and '@' in x).text.strip()
        except:
            pass
        try:
            overview_soup = soup_fun.find('main').find_all('aside',
                                                           {'id': 'listify_widget_panel_listing_content-2'})
            data_dict['description'] = overview_soup[0].find_all('div')[2].text.replace('\xa0', '').strip()

        except:
            pass
        try:
            table_ = soup_fun.find("table", {"class":"noborderTable"})
            data_dict['amenities'] = table_.text.replace('Property Features', '').replace('•', ',').strip().strip(',')
        except:
            pass

        property_elements = {'Location:': 'location', 'Bedrooms:': 'bedrooms', 'Bathrooms:': 'bathrooms',
                             'Lot Size (sq Meters):': 'land_area_in_meters', 'Lot Size (sq Varas):': 'total_area_sq_ft',
                             'View:': 'view', 'Listing #': "listing_id", "Lot Size": "total_area"}


        try:
            properties = soup_fun.find('aside', {"id": "listify_widget_panel_listing_gallery_slider-2"}).find(
                'div').text.split('|')
            index = 0
            for property in properties:
                index += 1
                for pro_key in property_elements:
                    if pro_key in str(property):
                        data_split = property.split(":")
                        if len(data_split) > 1:
                            data_dict[property_elements[pro_key]] = property.split(":")[1].replace('\n', '').strip()
                        else:
                            data_split = property.split("#")
                            if len(data_split) > 1:
                                data_dict[property_elements[pro_key]] = property.split("#")[1].replace('\n', '').strip()
                            else:
                                data_dict[property_elements[pro_key]] = property.replace('\n', '').strip()

                        break
        except:
            pass
        web_1_records_scraped += 1
        write_to_console("Aurora Beach Records Scraped: " + str(web_1_records_scraped))

        changes, new_ones = mongo.insert_property(data_dict)
        if changes:
            append_email_string(changes)
        if new_ones:
            append_new_email_string(new_ones)
        append_data(file_name, data_dict)


def go_through_all_pages_web_1(category_link_url, s, brokerage, cat_arg):
    proxies = ProxyDistributor.get_available_proxy()
    error_num = 3
    s.proxies.update(proxies)
    while True:
        try:
            response_fun = s.get(category_link_url.format(1))
            break
        except Exception as e:
            print(e, "Internet Issue Brokerage:", brokerage)
            if error_num <= 0:
                error_num = 3
                proxies = ProxyDistributor.get_available_proxy()
                s.proxies.update(proxies)
            sleep(1)
            pass

    soup_fun = BeautifulSoup(response_fun.text, "html.parser")
    total_pages = int(soup_fun.find_all('a', {'class': 'page'})[-1].text)
    get_data_from_page_web_1(soup_fun, s, brokerage, cat_arg)
    for i in range(2, total_pages + 1):
        error_num = 3
        while True:
            try:
                response_fun = s.get(category_link_url.format(i))
                break
            except Exception as e:
                print(e, "Internet Issue Brokerage:", brokerage)
                if error_num <= 0:
                    error_num = 3
                    proxies = ProxyDistributor.get_available_proxy()
                    s.proxies.update(proxies)
                sleep(1)
                pass
        soup_fun = BeautifulSoup(response_fun.text, "html.parser")
        get_data_from_page_web_1(soup_fun, s, brokerage, cat_arg)


def get_website_1():
    brokerage_web1 = "aurorabeachfront"
    s = requests.session()
    s.headers.update({
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'
    })
    category_links = {
        "Houses": "https://www.aurorabeachfront.com/nicaraguarealestate/searchresult.php?page={0}&type=3&location=0&beds=0&baths0&price=$0%20-%20$1000000",
        "Condos": "https://www.aurorabeachfront.com/nicaraguarealestate/searchresult.php?page={0}&type=4&location=0&beds=0&baths0&price=$0%20-%20$1000000",
        "Lots": "https://www.aurorabeachfront.com/nicaraguarealestate/searchresult.php?page={0}&type=11&location=0&beds=0&baths0&price=$0%20-%20$1000000",
        "Acreages": "https://www.aurorabeachfront.com/nicaraguarealestate/searchresult.php?page={0}&type=12&location=0&beds=0&baths0&price=$0%20-%20$1000000"
    }
    for category in category_links:
        go_through_all_pages_web_1(category_links[category], s, brokerage_web1, category)
    s.close()


if __name__ == "__main__":
    file_name = os.path.join(base_directory, "aurora_beach.csv")
    import os
    try:
        os.remove(file_name)
    except:
        pass
    get_website_1()
    if email_string != "":
        # print(email_string)
        SendEmail.send_emails("Aurora Beach Property Updates:", email_string)
    if new_property_email != "":
        SendEmail.send_emails("Aurora Beach Property New Listings:", new_property_email)