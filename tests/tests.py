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


def test_arguments():
    for i in range(1, 3):
        yield time.sleep, i * 0.001

if __name__ == '__main__':
    unittest.main()
