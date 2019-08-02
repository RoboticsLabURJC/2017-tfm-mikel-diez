from src.vision.matching.services.MatchInterestPointsWithBRIEF import MatchInterestPointsWithBRIEF
from src.vision.matching.services.MatchInterestPointsWithBrisk import MatchInterestPointsWithBrisk
from src.vision.matching.services.MatchInterestPointsWithOrb import MatchInterestPointsWithOrb
from src.vision.matching.services.MatchInterestPointsWithSurf import MatchInterestPointsWithSurf
from src.vision.matching.services.MatchInterestPointsWithSift import MatchInterestPointsWithSift
from src.vision.matching.services.MatchInterestPointsWithFREAK import MatchInterestPointsWithFREAK


class FeatureDetectorFactory:
    matchers = {
        'brisk': 'build_brisk_matcher',
        'brief': 'build_brief_matcher',
        'surf': 'build_surf_matcher',
        'sift': 'build_sift_matcher',
        'orb': 'build_orb_matcher',
        'freak': 'build_freak_matcher'
    }

    def build_matcher(self, calibration_data, type='brisk', threshold=400):
        method_name = self.matchers[type]
        matcher = getattr(self, method_name, lambda: 'Invalid')
        return matcher(calibration_data, threshold)

    @staticmethod
    def build_brisk_matcher(calibration_data, threshold):
        return MatchInterestPointsWithBrisk(calibration_data, threshold)

    @staticmethod
    def build_brief_matcher(calibration_data, threshold):
        return MatchInterestPointsWithBRIEF(calibration_data)

    @staticmethod
    def build_orb_matcher(calibration_data, threshold):
        return MatchInterestPointsWithOrb(calibration_data)

    @staticmethod
    def build_surf_matcher(calibration_data, threshold):
        return MatchInterestPointsWithSurf(calibration_data)

    @staticmethod
    def build_surf_matcher(calibration_data, threshold):
        return MatchInterestPointsWithSift(calibration_data)

    @staticmethod
    def build_freak_matcher(calibration_data, threshold):
        return MatchInterestPointsWithFREAK(calibration_data, threshold)