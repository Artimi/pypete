import unittest
import pypete
import time


class BasicTest(unittest.TestCase):

    def test_time(self):
        time.sleep(0.001)

if __name__ == '__main__':
    unittest.main()
