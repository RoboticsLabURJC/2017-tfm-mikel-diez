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

    def build_matcher(self, calibrationData, type='brisk', threshold=400):
        method_name = self.matchers[type]
        matcher = getattr(self, method_name, lambda: 'Invalid')
        return matcher(calibrationData, threshold)

    @staticmethod
    def build_brisk_matcher(calibrationData, threshold):
        return MatchInterestPointsWithBrisk(calibrationData, threshold)

    @staticmethod
    def build_brief_matcher(calibrationData, threshold):
        return MatchInterestPointsWithBRIEF(calibrationData)

    @staticmethod
    def build_orb_matcher(calibrationData, threshold):
        return MatchInterestPointsWithOrb(calibrationData)

    @staticmethod
    def build_surf_matcher(calibrationData, threshold):
        return MatchInterestPointsWithSurf(calibrationData)

    @staticmethod
    def build_surf_matcher(calibrationData, threshold):
        return MatchInterestPointsWithSift(calibrationData)


    @staticmethod
    def build_freak_matcher(calibrationData, threshold):
        return MatchInterestPointsWithFREAK(calibrationData, threshold)