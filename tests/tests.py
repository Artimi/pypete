import unittest
import pypete
import time


class BasicTest(unittest.TestCase):

    @pypete.timeit(repeat=3, number=10)
    def test_time(self):
        time.sleep(0.01)

if __name__ == '__main__':
    unittest.main()
