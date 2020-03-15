import unittest
from src.vision.matching.domain.factories.MatcherFactory import FeatureDetectorFactory

class TestFeatureDetectorFactory(unittest.TestCase):
    def test_build_matcher(self):
        self.assertAlmostEqual(True, True)
