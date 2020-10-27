import json
import import_string


def get_code(url):
    if 'amazon.com' in url:
        return 'us'
    return 'it'


def get_wrapper(url):
    code = get_code(url)
    wrapper_cls = import_string('wrappers.' + code + ':AmazonSpider')
    if not wrapper_cls:
        raise NotImplementedError(
            'Can\'t found wrapper: {}'.format(code)
        )
    return wrapper_cls()


def save_data(file_name, product_list):
    with open(file_name, 'w') as f:
        f.write(json.dumps(product_list, ensure_ascii=False))
