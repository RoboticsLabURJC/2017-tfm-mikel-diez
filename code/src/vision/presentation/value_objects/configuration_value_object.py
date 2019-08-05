import yaml


class ConfigurationValueObject:
    def __init__(self):
        self.general_configuration = None
        self.calibration_configuration = None
        self.matching_configuration = None
        self.reconstruction_configuration = None
        self.presentation_configuration = None

    @staticmethod
    def build_configuration_from_file(file):
        with open(file, 'r') as configuration_file:
            try:
                configuration = yaml.load(configuration_file, Loader=yaml.UnsafeLoader)

                configuration_value_object = ConfigurationValueObject()
                configuration_value_object.general_configuration = GeneralConfigurationValueObject(
                    configuration['parameters']['general']
                )
                configuration_value_object.calibration_configuration = CalibrationConfigurationValueObject(
                    configuration['parameters']['calibration']
                )
                configuration_value_object.matching_configuration = MatchingConfigurationValueObject(
                    configuration['parameters']['matching']
                )
                configuration_value_object.reconstruction_configuration = ReconstructionConfigurationValueObject(
                    configuration['parameters']['reconstruction']
                )
                configuration_value_object.presentation_configuration = PresentationConfigurationValueObject(
                    configuration['parameters']['presentation']
                )

                return configuration_value_object

            except yaml.YAMLError as exc:
                print(exc)


class GeneralConfigurationValueObject:
    def __init__(self, parameters):
        self.sets_folder = parameters['sets_folder']


class CalibrationConfigurationValueObject:
    def __init__(self, parameters):
        self.type = parameters['type']


class MatchingConfigurationValueObject:
    def __init__(self, parameters):
        self.type = parameters['type']


class ReconstructionConfigurationValueObject:
    def __init__(self, parameters):
        self.type = parameters['type']


class PresentationConfigurationValueObject:
    def __init__(self, parameters):
        self.type = parameters['type']
