from configparser import ConfigParser
import logging
import os


logger = logging.getLogger(__name__)


def config_parser_load(path):
    config = ConfigParser()
    config.read(path)

    logger.debug('reading config file from {}'.format(path))

    return config_to_dict(config)


def config_to_dict(config):
    config_dict = {}

    for section in config.sections():
        s = section.strip()
        config_dict[s] = {}
        logger.debug('section: {}'.format(s))

        for key in config[section].keys():
            k = key.strip()
            v = config[section][key].strip()
            config_dict[s][k] = v

            logger.debug('key: {}'.format(k))
            logger.debug('value: {}'.format(v))

            # when commas are present, then create a list of strings
            if ',' in config_dict[s][k]:
                v = config_dict[s][k].split(',')
                v = [e.strip() for e in v]
                config_dict[s][k] = v

    logger.debug('configuration: {}'.format(config_dict))

    return config_dict


def find_all_files(path):
    for file in os.listdir(path):
        full_path = os.path.join(path, file)
        if os.path.isfile(full_path):
            yield full_path
        else:
            yield from find_all_files(full_path)
