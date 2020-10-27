import re
from wrappers.us import AmazonSpider as AmazonUsSpider, \
    AmazonProduct as AmazonUsProduct


class AmazonProduct(AmazonUsProduct):

    def count_stock(self):
        cnt = self.grab.doc('id("availability")/span[@class="a-size-medium a-color-success"]').text(default='')
        if cnt:
            cnt = re.findall('(\d+)', cnt)
            return int(cnt[0]) if len(cnt) > 0 else 0
        return 0

    def details(self):
        xpath = '//tr[@class="a-spacing-small"]/td[@class="a-span3"]/span[@class="a-size-base a-text-bold"]'
        cat = self.grab.doc(xpath).text_list()
        xpath_val = 'id("productOverview_feature_div")/div[@class="a-section a-spacing-small a-spacing-top-small"]' \
                    '/table[@class="a-normal a-spacing-micro"]/tbody/tr[@class="a-spacing-small"]/td[@class="a-span9"]' \
                    '/span[@class="a-size-base"]'
        value = self.grab.doc(xpath_val).text_list()
        result = list(zip(cat, value))
        return result


class AmazonSpider(AmazonUsSpider):
    main_url = 'https://www.amazon.it'
    product = AmazonProduct
