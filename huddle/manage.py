import subprocess
import time
import sys
import logging
import random
import os

from huddle.repo import GitRepo

logger = logging.getLogger(__name__)


class ApplicationManager:
    def __init__(self, config, runner=True):
        """

        :param config: a dictionary containing the configuration
        """
        self.config = config
        self.exec = None
        self.app_ref = None
        self.repo = None

        if runner:
            self.load_and_validate()
            self.run(self.config)

    def load_and_validate(self, config=None):
        """
        Sets the local executable and takes care of other initialization tasks
        :param config: dictionary containing the configuration
        :return:
        """
        configuration = config if config else self.config

        # determine the repository type
        if 'type' in configuration['repository'].keys():
            repo_type = configuration['repository']['type'].lower()
        else:
            repo_type = 'git'

        if repo_type == 'git':
            # find the local executable
            if 'executable' in configuration['repository'].keys():
                executable = configuration['repository']['executable']
            else:
                executable = None

            local_path = configuration['repository']['local path']
            remote_path = configuration['repository']['remote path']

            self.repo = GitRepo(local_path, remote_path, executable=executable)

            if 'branch' in configuration['repository'].keys():
                self.repo.branch = configuration['repository']['branch']

            if 'remote' in configuration['repository'].keys():
                self.repo.remote = configuration['repository']['remote']
        else:
            raise NotImplementedError('repository type not supported: {}'.format(repo_type))

        # if the local directory does not exist, then it must be cloned and checked out
        path_valid = False
        while not path_valid:
            if not os.path.exists(self.repo.local_path):
                logger.debug('path not found: {}'.format(configuration['repository']['local path']))
                logger.debug('cloning repository')

                self.repo.clone()

                try:
                    os.chdir(self.repo.local_path)
                    path_valid = True
                except FileNotFoundError:
                    logger.info('repository not cloned, waiting...')
                    time.sleep(10.0)
            else:
                logger.debug('path found: {}'.format(self.repo.local_path))
                path_valid = True

        self.repo.checkout()
        self.post_pull_scripts()

        if not self.is_new(configuration):
            self.start_application(configuration)

    def run_script(self, script):
        """
        Will run a single command-line script and return the output

        :param script: a string containing the script to be executed
        :return: the command-line output
        """
        parts = script.split()
        p = subprocess.Popen(parts, stdout=subprocess.PIPE)

        stdout = ''
        for line in p.stdout:
            stdout += line.decode('utf-8')
        return stdout

    def run_scripts(self, list_of_scripts):
        """
        Runs a series of scripts, returning the output of each as a list

        :param list_of_scripts:  list of scripts
        :return: list of outputs
        """
        outs = []
        for script in list_of_scripts:
            out = self.run_script(script)

            logger.debug('script: {}'.format(script))
            logger.debug('script output: {}'.format(out))
            outs.append(out)

        return outs

    def get_branch(self, config=None):
        """
        Returns the local branch from the configuration

        :param config: dictionary containing the configuration
        :return: the branch name from the configuration
        """
        configuration = config if config else self.config

        if 'branch' in configuration['repository'].keys():
            return configuration['repository']['branch']
        else:
            return 'master'

    def is_new(self, config=None):
        """
        Fetches the references from the remote repository and determines if the remote branch has new commits.

        :param config: dictionary containing the configuration
        :return: True if remote is new, else false
        """
        configuration = config if config else self.config

        _, out = self.repo.fetch()
        logger.debug('fetch output: {}'.format(out))

        diff_status, out = self.repo.diff()
        logger.debug('diff output: {}'.format(out))

        return diff_status

    def tests_pass(self, config=None):
        """
        Determines if the test server is passing or failing on this branch

        :param config: dictionary containing the configuration
        :return: True if tests pass or False
        """
        configuration = config if config else self.config

        if 'test' in configuration.keys():
            raise NotImplementedError('')
            # todo: add test check scripting
        else:
            logger.debug('no tests specified')
            return True

    def pre_pull_scripts(self, config=None):
        """
        Runs all pre-pull scripts

        :param config: dictionary containing the configuration
        :return:
        """
        configuration = config if config else self.config

        try:
            return self.run_scripts(configuration['scripts']['pre-pull'])
        except KeyError:
            return []

    def pull(self, config=None):
        """
        Pulls the remote branch into the local branch

        :param config:
        :return:
        """
        configuration = config if config else self.config

        _, out = self.repo.pull()

        logger.debug('pull output: {}'.format(out))

    def post_pull_scripts(self, config=None):
        """
        Runs all post-pull scripts

        :param config: dictionary containing the configuration
        :return:
        """
        configuration = config if config else self.config

        try:
            return self.run_scripts(configuration['scripts']['post-pull'])
        except KeyError:
            return []

    def stop_application(self):
        """
        Stops the user application

        :return:
        """
        if self.app_ref:
            if sys.platform == 'win32':
                script = 'Taskkill /PID {} /F'.format(self.app_ref.pid)
            else:
                script = 'kill {}'.format(self.app_ref.pid)

            self.run_script(script)
            self.app_ref = None

    def start_application(self, config=None):
        """
        Starts the user application

        :param config: dictionary containing the configuration
        :return:
        """
        configuration = config if config else self.config

        if 'application' in configuration.keys():
            if 'start' in configuration['application'].keys():
                logger.debug('starting application: {}'.format(configuration['application']['start']))
                parts = configuration['application']['start'].split()
                self.app_ref = subprocess.Popen(parts, stdout=subprocess.PIPE)

    def run(self, config):
        """
        Periodically runs the full script at the interval determined by the configuration

        :param config: dictionary containing the configuration
        :return:
        """
        configuration = config if config else self.config

        while True:
            if self.is_new():
                logger.debug('branch is new')

                if self.tests_pass():
                    self.stop_application()
                    self.pre_pull_scripts()
                    self.pull()
                    self.post_pull_scripts()
                    self.start_application()

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
