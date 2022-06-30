class MapCategory:
    def __init__(self):
        self.categories = {"Houses": "Houses", "Apartments": "Apartments",
                           "Land": "Land", "Commercial": "Commercial",
                           "Farms": "Farms"}

        self.houses_mapping = ["house", "houses", "townhouses", "urban sjds", "villas", "villa", "both", "residential"]
        self.apartments_mapping = ["apartments", "condominium", "condos", "condo/townhome", "apartment"]
        self.land_mapping = ["lot/land", "lot/raw land", "acreages", "lots", "land", "farmland", "green real estate", "both", "surf real estate"]
        self.commercial_mapping = ["business", "commercial"]
        self.farm_mapping = [""]

    def map_category(self, cat_str_arg):
        if not cat_str_arg.__contains__(','):
            if "commercial" in cat_str_arg.lower() and "house" in cat_str_arg.lower():
                cat_str_arg = "commercial,house"
            if "lot/raw land" in cat_str_arg.lower() and "house" in cat_str_arg.lower():
                cat_str_arg = "lot/raw land,house"
            if "condo/townhome" in cat_str_arg.lower() and "house" in cat_str_arg.lower():
                cat_str_arg = "condo/townhome,house"

        categories = cat_str_arg.split(",")
        category_string = ""
        for category in categories:
            mapped = False
            if category.strip('\n').strip().lower() in self.houses_mapping:
                mapped = True
                category_string += self.categories['Houses'] + ", "
            if category.strip('\n').strip().lower() in self.apartments_mapping:
                mapped = True
                category_string += self.categories['Apartments'] + ", "
            if category.strip('\n').strip().lower() in self.land_mapping:
                mapped = True
                category_string += self.categories['Land']+ ", "
            if category.strip('\n').strip().lower() in self.commercial_mapping:
                mapped = True
                category_string += self.categories["Commercial"] + ", "
            if category.strip('\n').strip().lower() in self.farm_mapping:
                mapped = True
                category_string += self.categories["Farms"] + ", "
            if not mapped:
                print("Not Mapped:", category)
                category_string += category + ", "

        return category_string[:category_string.__len__()-2]