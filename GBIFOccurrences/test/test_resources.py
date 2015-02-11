# coding=utf-8
"""Resources test.

"""

__author__ = 'n.noe@biodiversity.be'
__date__ = '2014-11-18'
__copyright__ = 'Copyright 2014, Nicolas Noé - Belgian Biodiversity Platform'

import unittest

from PyQt4.QtGui import QIcon


class GBIFOccurrencesDialogTest(unittest.TestCase):
    """Test rerources work."""

    def setUp(self):
        """Runs before each test."""
        pass

    def tearDown(self):
        """Runs after each test."""
        pass

    def test_icon_png(self):
        """Test we can click OK."""
        path = ':/plugins/GBIFOccurrences/icon.png'
        icon = QIcon(path)
        self.assertFalse(icon.isNull())

if __name__ == "__main__":
    suite = unittest.makeSuite(GBIFOccurrencesResourcesTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
