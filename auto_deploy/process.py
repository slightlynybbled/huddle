import json
import time
import sys
import json
import logging
import random

logger = logging.getLogger(__name__)


class AutoDeploy:
    def __init__(self, path_to_config):
        self.config = {}
        self.load_and_validate(path_to_config)

        self.run(self.config)

    def load_and_validate(self, path_to_config):
        try:
            with open(path_to_config, 'r') as f:
                self.config = json.load(f)
            logger.debug(self.config)
        except FileNotFoundError:
            logger.debug('path "{}" not found'.format(path_to_config))
            sys.exit(1)

    def check_for_updates(self, config=None):
        pass

    def check_test(self, config=None):
        pass

    def pre_pull_scripts(self, config=None):
        pass

    def pull(self, config=None):
        pass

    def post_pull_scripts(self, config=None):
        pass

    def run(self, config):
        configuration = config if config else self.config

        while True:

            # determine the sleep time
            sleep_time = 60  # default
            if 'timing' in configuration.keys():
                if 'minimum' in configuration['timing'] and 'maximum' in configuration['timing']:
                    min_time = int(configuration['timing']['minimum'])
                    max_time = int(configuration['timing']['maximum'])
                    sleep_time = random.randint(min_time, max_time)
                    logger.debug('minimum sleep time: {} maximum sleep time: {} '.format(min_time, max_time))
                elif 'minimum' in configuration['timing']:
                    sleep_time = int(configuration['timing']['minimum'])

            logger.debug('sleeping for {}s'.format(sleep_time))

            time.sleep(sleep_time)
