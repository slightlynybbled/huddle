import subprocess
import time
import sys
import json
import logging
import random

logger = logging.getLogger(__name__)


class AutoDeploy:
    def __init__(self, path_to_config):
        self.config = {}
        self.exec = '/usr/bin/git'  # default executable (linux)
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

        if 'executable' in self.config['repository'].keys():
            self.exec = self.config['repository']['executable']
        else:
            if sys.platform == 'win32':
                self.exec = 'C:/Program Files/Git/bin/git'

    def get_branch(self, config=None):
        configuration = config if config else self.config
        if 'branch' in configuration['repository'].keys():
            return configuration['repository']['branch']
        else:
            return 'master'

    def is_new(self, config=None):
        configuration = config if config else self.config

        branch_name = self.get_branch(configuration)
        p = subprocess.Popen([self.exec, 'fetch', 'origin', branch_name], stdout=subprocess.PIPE)
        stdout = ''
        for line in p.stdout:
            stdout += line.decode('utf-8')
        logger.debug('fetch output: {}'.format(stdout))

        remote_branch = 'origin/' + branch_name
        p = subprocess.Popen([self.exec, 'diff', 'origin', branch_name, remote_branch], stdout=subprocess.PIPE)

        stdout = ''
        for line in p.stdout:
            stdout += line.decode('utf-8')
        logger.debug('diff output: {}'.format(stdout))

        # todo: check the stdout

    def tests_pass(self, config=None):
        configuration = config if config else self.config

        if 'test' in configuration.keys():
            raise NotImplementedError('')
        else:
            return True

    def pre_pull_scripts(self, config=None):
        configuration = config if config else self.config

        try:
            for script in configuration['scripts']['pre-pull']:
                parts = script.split()
                p = subprocess.Popen(parts, stdout=subprocess.PIPE)

                stdout = ''
                for line in p.stdout:
                    stdout += line.decode('utf-8')
                logger.debug('script: {}'.format(script))
                logger.debug('script output: {}'.format(stdout))

        except KeyError:
            pass

    def pull(self, config=None):
        configuration = config if config else self.config
        p = subprocess.Popen([self.exec, 'fetch', 'origin', self.get_branch(configuration)], stdout=subprocess.PIPE)

        stdout = ''
        for line in p.stdout:
            stdout += line.decode('utf-8')
        logger.debug('pull output: {}'.format(stdout))

    def post_pull_scripts(self, config=None):
        configuration = config if config else self.config

        try:
            for script in configuration['scripts']['post-pull']:
                parts = script.split()
                p = subprocess.Popen(parts, stdout=subprocess.PIPE)

                stdout = ''
                for line in p.stdout:
                    stdout += line.decode('utf-8')
                logger.debug('script: {}'.format(script))
                logger.debug('script output: {}'.format(stdout))

        except KeyError:
            pass

    def run(self, config):
        configuration = config if config else self.config

        while True:
            if self.is_new():
                logger.debug('branch is new')

                if self.tests_pass():
                    self.pre_pull_scripts()
                    self.pull()
                    self.post_pull_scripts()

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
