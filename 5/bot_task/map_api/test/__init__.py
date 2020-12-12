import unittest

from urllib.parse import urlparse


class TestCase(unittest.TestCase):
    def assertURLEqual(self, url1, url2):

        u1_parsed = urlparse(url1)
        u2_parsed = urlparse(url2)

        self.assertURLEqual(u1_parsed, u2_parsed)