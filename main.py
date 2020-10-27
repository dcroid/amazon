from common import save_data, get_wrapper
import argparse


parser = argparse.ArgumentParser(description="Args for parsing Amazon product")
parser.add_argument('--url', type=str, help="Amazon url category")
parser.add_argument('--f', type=str, help="File name for save data", default=False)


def main(url, file_name=None):
    spider = get_wrapper(url)
    spider.category_url = url
    spider.run()
    if not file_name:
        file_name = spider.file
    save_data(file_name, spider.product_list)


if __name__ == '__main__':
    args = parser.parse_args()
    main(args.url, args.f)
