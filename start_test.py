import unittest

from start import get_weibo_page_url_and_number, get_pretreat_page
from constants import MAX_TURN_PAGE


class TestStart(unittest.TestCase):

    def test_get_weibo_page_url(self):
        max_count = 0
        for index, (url, number) in enumerate(get_weibo_page_url_and_number()):
            url_number = int(url.split('=')[-1])
            assert_number = index % MAX_TURN_PAGE + 1

            self.assertEqual(url_number, assert_number)
            self.assertEqual(number, assert_number)
            if assert_number == MAX_TURN_PAGE:  # 最大页码计数
                max_count += 1
            if max_count == 2:  # 遍历两次后退出测试
                break
        self.assertEqual(max_count, 2)

    def test_get_protreat_page(self):
        weibo_urls = get_weibo_page_url_and_number()
        page_soup = get_pretreat_page(next(weibo_urls)[0])
        # print(page_soup.prettify())
        # print(page_soup.title.text)
        self.assertEqual(page_soup.title.text, '我的首页')


if __name__ == '__main__':
    unittest.main()
