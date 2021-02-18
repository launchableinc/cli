import unittest
from launchable.commands.record.commit import _build_proxy_option

class CommitTest(unittest.TestCase):
  def test_proxy_options(self):
      self.assertEqual(_build_proxy_option("https://some_proxy:1234"), "-Dhttps.proxyHost=some_proxy -Dhttps.proxyPort=1234 ")
      self.assertEqual(_build_proxy_option("some_proxy:1234"), "-Dhttps.proxyHost=some_proxy -Dhttps.proxyPort=1234 ")
      self.assertEqual(_build_proxy_option("some_proxy"), "-Dhttps.proxyHost=some_proxy ")
      self.assertEqual(_build_proxy_option("https://some_proxy"), "-Dhttps.proxyHost=some_proxy ")
      self.assertEqual(_build_proxy_option("http://yoyoyo"), "-Dhttps.proxyHost=yoyoyo ")
