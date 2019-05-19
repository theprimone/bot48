import unittest

from utils import get_fcl_users, get_fcl_user_tag


class TestStart(unittest.TestCase):

    def test_get_fcl_users(self):
        self.assertIsInstance(get_fcl_users(), dict)

    def test_get_fcl_user_tag(self):
        self.assertEqual(get_fcl_user_tag('SNH48-孙珍妮'), '#孙珍妮#')
        self.assertEqual(get_fcl_user_tag('SNH48'), '')


if __name__ == '__main__':
    unittest.main()
