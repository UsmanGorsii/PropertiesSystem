import pymongo
from datetime import datetime

class MongoClient:
    def __init__(self):
        self.client = pymongo.MongoClient("mongodb+srv://joelDB:bmuu8erQx3GZLRF@cluster0-jx1vv.mongodb.net/test?retryWrites=true&w=majority")
        self.db = self.client.PropertiesData

    def insert_property(self, property_dict):
        result = self.db.properties.find_one({"url": property_dict['url']})
        change_str = None
        new_str = None
        if not result:
            new_str = "\n***  New Property link:  " + str(property_dict['url']) + "  ***"
            property_dict["listing_date"] = datetime.utcnow().strftime("%d/%m/%Y")
            self.db.properties.insert(property_dict)
        else:
            result.pop('_id')
            set1 = set(result.items())
            set2 = set(property_dict.items())
            try:
                property_dict["listing_date"] = result["listing_date"]
            except:
                pass
            change = set1 - set2
            change_2 = set2 - set1
            if change:
                cat_change = False
                for val in list(change_2):
                    inde = 0
                    if val[0] == "listing_category":
                        inde = 1
                    elif val[1] == "listing_category":
                        inde = 0
                    else:
                        inde = -1
                    if inde != -1:
                        category_list = result['listing_category'].split(',')
                        category_list = [ca.lower().strip() for ca in category_list]
                        for new_cat in val[inde].split(','):
                            if new_cat.lower().strip() not in category_list:
                                cat_change = True
                                category_list.append(new_cat.strip())
                add = False
                new_changes = []
                for val in list(change_2):
                    if val[0] == "price" or val[1] == "price":
                        new_changes.append(val)
                        add = True
                    if val[0] == "listing_status" or val[1] == "listing_status":
                        new_changes.append(val)
                        add = True

                old_changes = []
                for val in list(change):
                    if val[0] == "price" or val[1] == "price":
                        old_changes.append(val)
                    if val[0] == "listing_status" or val[1] == "listing_status":
                        old_changes.append(val)

                if add:
                    change_str = "\n***  " + str(property_dict['url']) + "  ***"
                    change_str += "\nBefore Update: " + str(old_changes)
                    change_str += "\nAfter Update: " + str(new_changes)

                if cat_change:
                    property_dict['listing_category'] = ",".join(category_list)
            self.db.properties.find_one_and_update({"url": property_dict['url']}, {"$set": property_dict})
        return change_str, new_str