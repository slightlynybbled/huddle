import json
import time
import sys
import json
import logging

logger = logging.getLogger(__name__)


class AutoDeploy:
    def __init__(self, path_to_config):
        self.config = {}
        self.load_and_validate(path_to_config)

        self.run()

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

    def run(self):
        while True:


            time.sleep(60)
