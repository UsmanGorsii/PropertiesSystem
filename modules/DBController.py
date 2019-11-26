import pymongo
import pandas as pd
import re
from datetime import datetime, timedelta


def get_file_length(file_name, column_name):
    try:
        df_fun = pd.read_csv(file_name)
        ss = len(df_fun[column_name].tolist())
    except:
        return 0
    return ss


def append_data(data_dict_arg, file_name, column_name):
    p = get_file_length(file_name, column_name)
    df = pd.DataFrame(data_dict_arg, index=[p])
    if p == 0:
        df.to_csv(file_name, mode='a+', header=True, encoding='utf-8', index=False)
    else:
        df.to_csv(file_name, mode='a+', header=False, encoding='utf-8', index=False)


class DBController:

    def __init__(self):
        self.all_properties_details = []
        self.conn = pymongo.MongoClient('mongodb+srv://joelDB:bmuu8erQx3GZLRF@cluster0-jx1vv.mongodb.net/test?retryWrites=true&w=majority')
        self.properties_db = self.conn["PropertiesData"]
        self.users_db = self.conn["PropertiesData"]
        self.brokerages = []

    def check_login_details(self, username_arg, password_arg):
        cursor_user = self.properties_db["users"].find({})
        for user in cursor_user:
            print(user['username'].strip().lower())
            print(user['password'])

            print(username_arg.strip().lower())
            print(password_arg)
            if user['username'].strip().lower() == username_arg.strip().lower():
                print("good  1")
                if user["password"] == password_arg:
                    print("good")
                    return True
        return False

    def get_all_properties(self):
        self.all_properties_details = []
        cursor = self.properties_db["properties"].find({})
        for prop_doc in cursor:
            if prop_doc['brokerage'].strip() != "" and prop_doc['brokerage'].lower().strip() not in self.brokerages:
                self.brokerages.append(prop_doc['brokerage'].lower().strip())
            self.all_properties_details.append(prop_doc)
        return self.all_properties_details, self.brokerages

    @staticmethod
    def filter_string(str_input, input_list, split_str=False):
        input_list = [inp.lower().strip() for inp in input_list]

        if split_str:
            str_input = str(str_input).split(",")
            for strr in str_input:
                if strr.lower().strip() in input_list:
                    return True

            return False
        if str(str_input).lower().strip() in input_list:
            return True
        else:
            return False

    @staticmethod
    def filter_number(input_num, min_number, max_number):
        if min_number == "":
            min_number = None
        else:
            min_number = int(min_number)
        if max_number == "":
            max_number = None
        else:
            max_number = int(max_number)

        try:
            input_num = str(input_num).split('.')[0]
            numbers = re.findall(r'\b\d+\b', input_num)
            numbers = "".join(numbers)
        except:
            numbers = 0
        try:
            numbers = int(numbers)
        except:
            numbers = 0
            pass
        good = True
        if min_number is not None and numbers > min_number:
            good = True
        else:
            if min_number is not None:
                return False

        if max_number is not None and numbers <= max_number:
            good = True
        else:
            if max_number is not None:
                good = False
        return good

    def filter_records(self, brokerage_list=[], property_status_list=[], listing_category_list=[], price_min=None,
                       price_max=None, bathrooms_min=None, bathrooms_max=None, bedrooms_min=None, bedrooms_max=None):
        if self.all_properties_details.__len__() <= 0:
            self.get_all_properties()

        filtered_properties = []

        for property_dict in self.all_properties_details:
            append = True
            if len(brokerage_list) > 0:
                append = self.filter_string(property_dict['brokerage'], brokerage_list)
            if append and len(property_status_list) > 0:
                append = self.filter_string(property_dict['listing_status'], property_status_list)
            if append and len(listing_category_list) > 0:
                append = self.filter_string(property_dict['listing_category'], listing_category_list, True)
            if append:
                append = self.filter_number(property_dict['price'], price_min, price_max)
            if append:
                append = self.filter_number(property_dict['bedrooms'], bedrooms_min, bedrooms_max)
            if append:
                append = self.filter_number(property_dict['bathrooms'], bathrooms_min, bathrooms_max)

            if append:
                filtered_properties.append(property_dict)
        return filtered_properties, self.brokerages

    def close_connection(self):
        self.conn.close()
        self.all_properties_details = []
