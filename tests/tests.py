import unittest
import pypete
import time


class BasicTest(unittest.TestCase):

    def setUp(self):
        self.a = 'Lorem ipsum'

    def test_time(self):
        time.sleep(0.001)

    def test_time2(self):
        time.sleep(0.002)

    def test_fail(self):
        self.assertTrue(False)

if __name__ == '__main__':
    unittest.main()
