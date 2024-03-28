import csv
import requests
import parameters
import model
import os


class MetroParser:
    def __init__(self, store_id):
        self.store_id = store_id
        self.headers = parameters.headers
        self.json_data = parameters.json_data
        self.url = parameters.url
        self.path_csv = f'result_msk_spb.csv'
        self.metro_url = 'https://online.metro-cc.ru'

    def parse(self):
        self.json_data['variables']['storeId'] = self.store_id
        self.json_data['variables']['from'] = 0
        while True:
            response = requests.post(self.url, headers=self.headers, json=self.json_data)
            category_dict = response.json()['data']['category']
            products_obj = model.Products.parse_obj(category_dict)
            total = category_dict['total']
            if self.json_data['variables']['from'] > total:
                break
            if not os.path.isfile(self.path_csv):
                self.create_csv()
            self.add_product_to_csv(products_obj)
            self.json_data['variables']['from'] += self.json_data['variables']['size']

    def create_csv(self):
        with open(self.path_csv, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'name', 'url', 'price', 'promo_price', 'brand'])

    def add_product_to_csv(self, data: model.Products):
        with open(self.path_csv, 'a') as f:
            writer = csv.writer(f)
            for product in data.products:
                if self.check_product_in_csv(product.id):
                    writer.writerow(
                        [product.id, product.name, self.metro_url + product.url, product.stocks[0].prices.old_price,
                         product.stocks[0].prices.price, product.manufacturer.name])

    def check_product_in_csv(self, product_id: int):
        with open(self.path_csv) as f:
            for row in csv.reader(f):
                if str(product_id) in row:
                    return False
            return True


if __name__ == '__main__':
    MetroParser(10).parse()
    MetroParser(15).parse()
