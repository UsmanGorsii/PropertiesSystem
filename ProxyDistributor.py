import csv
import os
status = {"available": "available", "not_available": "not_available"}
columns = ["proxy", "status"]
base_directory = os.path.abspath(os.path.dirname(__file__))

file_path = os.path.join(base_directory,'proxies.csv')


def update_proxy_file(proxy_dict):
    os.remove(file_path)
    with open(file_path, "w", newline="") as csv_file:
        dict_writer = csv.DictWriter(csv_file, fieldnames=columns)
        dict_writer.writeheader()
        dict_writer.writerows(proxy_dict)


def reset_all_proxies():
    proxy_dict = []
    with open(file_path, "r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for proxy_row in csv_reader:
            proxy_row[columns[1]] = status["available"]
            proxy_dict.append(proxy_row)
    update_proxy_file(proxy_dict)
    return True


def get_available_proxy(reuest=True):
    proxy = None
    found = False
    while True:
        proxy_dict = []
        with open(file_path, "r") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for proxy_row in csv_reader:
                if proxy_row[columns[1]] == status["available"] and not found:
                    found = True
                    proxy = proxy_row[columns[0]]
                    proxy_row[columns[1]] = status["not_available"]

                proxy_dict.append(proxy_row)
        if proxy is None:
            reset_all_proxies()
        else:
            break

    update_proxy_file(proxy_dict)
    if reuest:
        proxy = {'http': 'http://Seljoel:V0o5KvP@{0}'.format(proxy)} #
    return proxy

