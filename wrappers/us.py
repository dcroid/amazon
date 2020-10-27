import re
import json
import time
from datetime import datetime

from weblib.error import DataNotFound
from grab.spider import Spider, Task


class AmazonProduct:

    grab = None
    asin = None
    url = None
    brand = ''

    def title(self):
        try:
            return self.grab.doc('id("productTitle")').text()
        except Exception as er:
            print(self.grab.doc('//title').text())

    def description(self):
        return self.grab.doc('id("productDescription")').text()

    def stock(self):
        return self.grab.doc('id("availability")/span[@class="a-size-medium a-color-success"]').text(default=0)

    def count_stock(self):
        cnt = self.grab.doc('//span[@class="a-size-medium a-color-price"]').text(default='')
        if cnt:
            cnt = re.findall('(\d+)', cnt)
            return int(cnt[0])
        return 0

    def price_current(self):
        price = self.grab.doc('//span[@class="a-size-medium a-color-price priceBlockBuyingPriceString"]')\
            .text(default='0.0').replace(",", ".").replace("$", "").replace("€", "").strip()
        return float(price)

    def price_orig(self):
        price = self.grab.doc('//span[@class="priceBlockStrikePriceString a-text-strike"]').text(default='0.0')\
            .replace(",", ".").replace("$", "").replace("€", "").strip()
        return float(price)

    def section(self):
        return self.grab.doc('//li/span[@class="a-list-item"]/a[@class="a-link-normal a-color-tertiary"]').text_list()

    def main_image(self):
        try:
            return self.grab.doc('//div[@id="imgTagWrapperId"]/img').attr('data-old-hires')
        except Exception as er:
            print(self.grab.doc("//title").text())
            pass

    def set_images(self):
        r = self.grab.doc.rex_search('\'colorImages\': \{ \'initial\':(.*?)},\n')
        images = r.group(1)
        images = [img['large'] for img in json.loads(images)]
        return images

    def details(self):
        xpath = '//ul[@class="a-unordered-list a-nostyle a-vertical a-spacing-none detail-bullet-list"]/' \
                'li/span[@class="a-list-item"]/span'
        cat = self.grab.doc(f'{xpath}[1]').text_list()
        cat = [res.replace(' :', '') for res in cat]
        value = self.grab.doc(f'{xpath}[2]').text_list()
        return AmazonProduct.splitter(cat, value)

    def product_overview(self):
        cat = self.grab.doc('//td[@class="a-span3"]/span').text_list()
        value = self.grab.doc('//td[@class="a-span9"]/span').text_list()
        result = AmazonProduct.splitter(cat, value)
        self.brand = result.get('Brand', '')
        return AmazonProduct.splitter(cat, value)

    @staticmethod
    def splitter(cat, value):
        result = list(zip(cat, value))
        result = {param[0]: param[1] for param in result}
        return result

    def video(self):
        try:
            js = self.grab.doc.rex_search('\"videos\":(.*?),\"lazyLoadExperienceDisabled\"')
            js = json.loads(js.group(1))
            if len(js) > 0:
                return [v['url'] for v in js]
            return []
        except DataNotFound:
            return []

    @classmethod
    def get(cls, grab, url, asin):
        item = cls()
        item.grab = grab
        item.url = url
        item.asin = asin
        return item.director()

    def director(self):
        price_orig = self.price_orig()
        price_current = self.price_current()
        if price_current == 0.0:
            price_current = price_orig

        sale_percent = 0
        if price_orig:
            sale_percent = 100 - (100 / price_orig * price_current)
            sale_percent = round(sale_percent)

        stock = self.stock()
        cnt_stock = self.count_stock()
        if cnt_stock > 0:
            stock = True

        result = {
            'timestamp': str(datetime.fromtimestamp(int(time.time()))),
            'RPC': self.asin,
            'url': self.url,
            'title': self.title(),
            'stock': {
                'in_stock': stock,
                'count': cnt_stock
            },
            'price_data': {
                'original': price_orig,
                'current': price_current,
                'sale_tag': f"Скидка: {sale_percent}%"
            },
            'section': self.section(),
            'assets': {
                'main_image': self.main_image(),
                'set_images': self.set_images(),
                'video': self.video(),
            },
            'metadata': {
                '__description': self.description(),
                **self.details(),
                **self.product_overview()
            },
            'brand': self.brand,
        }
        return result


class AmazonSpider(Spider):
    main_url = 'https://www.amazon.com'
    category_url = ''
    items_asin = []
    product = AmazonProduct
    product_list = []
    file = None

    def task_generator(self):
        if self.category_url:
            yield Task('end_page', url=self.category_url)
        else:
            raise Exception("No amazon category url")

    def file_name(self, grab):
        if not self.file:
            cat_name = grab.doc('id("nav-subnav")/a[@class="nav-a nav-b"]/span[@class="nav-a-content"]').text(default='not_cat_name').replace(" ", "_")
            title = grab.doc('//span[@class="a-color-state a-text-bold"]').text(default='not_title').replace(" ", "_")
            self.file = f"{cat_name}_{title}.json"

    def task_end_page(self, grab, task):
        self.file_name(grab)

        end_page_xpath = '//li[@class="a-disabled"]'
        num_page = grab.doc(end_page_xpath).text_list()
        if len(num_page) > 1:
            end_page = int(num_page[-1]) + 1
        else:
            end_page = 2
        for page in range(1, end_page):
            yield Task('items_page', url=f"{self.category_url}&page={page}")

    def task_items_page(self, grab, task):
        items_xpath = '//div[@data-component-type="s-search-result"]'
        asins = grab.doc(items_xpath).attr_list('data-asin')
        for asin in asins:
            yield Task('item_page', url=f"{self.main_url}/-/dp/{asin}/", asin=asin)

    def task_item_page(self, grab, task):
        item = self.product.get(grab, task.url, task.asin)
        self.product_list.append(item)

