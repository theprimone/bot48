import unittest

from start import get_weibo_page_url, get_pretreat_page
from constants import MAX_TURN_PAGE


class TestStart(unittest.TestCase):

    def test_get_weibo_page_url(self):
        for index, url in enumerate(get_weibo_page_url()):
            url_number = int(url.split('=')[-1])
            assert_number = index % MAX_TURN_PAGE + 1

            self.assertEqual(url_number, assert_number)

    def test_get_protreat_page(self):
        weibo_urls = get_weibo_page_url()
        page_soup = get_pretreat_page(next(weibo_urls))
        # print(page_soup.prettify())
        # print(page_soup.title.text)
        self.assertEqual(page_soup.title.text, '我的首页')


if __name__ == '__main__':
    unittest.main()
