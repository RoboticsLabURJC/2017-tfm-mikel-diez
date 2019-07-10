from Vision.Services.Matching.MatchInterestPointsWithBRIEF import MatchInterestPointsWithBRIEF
from Vision.Services.Matching.MatchInterestPointsWithBrisk import MatchInterestPointsWithBrisk
from Vision.Services.Matching.MatchInterestPointsWithOrb import MatchInterestPointsWithOrb
from Vision.Services.Matching.MatchInterestPointsWithSurf import MatchInterestPointsWithSurf
from Vision.Services.Matching.MatchInterestPointsWithSift import MatchInterestPointsWithSift
from Vision.Services.Matching.MatchInterestPointsWithFREAK import MatchInterestPointsWithFREAK


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