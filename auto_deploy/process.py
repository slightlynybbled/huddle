import subprocess
import time
import sys
import logging
import random
import os

logger = logging.getLogger(__name__)


class AutoDeploy:
    def __init__(self, config):
        """

        :param config: a dictionary containing the configuration
        """
        self.config = config
        self.exec = '/usr/bin/git'  # default executable (linux)
        self.app_ref = None

        self.load_and_validate()
        self.run(self.config)

    def load_and_validate(self, config=None):
        """
        Sets the local executable and takes care of other initialization tasks
        :param config: dictionary containing the configuration
        :return:
        """
        configuration = config if config else self.config

        # find the local executable
        if 'executable' in configuration['repository'].keys():
            self.exec = configuration['repository']['executable']
        else:
            if sys.platform == 'win32':
                self.exec = 'C:/Program Files/Git/bin/git'

        # if the local directory does not exist, then it must be cloned and checked out
        if not os.path.exists(configuration['repository']['local path']):
            logger.debug('path not found: {}'.format(configuration['repository']['local path']))
            logger.debug('cloning repository')

            remote_path = configuration['repository']['remote path']
            local_path = configuration['repository']['local path']

            script = '{} clone {} {}'.format(self.exec, remote_path, local_path)
            self.run_script(script)

            script = '{} checkout {}'.format(self.exec, self.get_branch(configuration))
            self.run_script(script)
        else:
            logger.debug('path found: {}'.format(configuration['repository']['local path']))

        os.chdir(configuration['repository']['local path'])
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

        local_branch = self.get_branch(configuration)
        remote_branch = configuration['repository']['remote'] + '/' + local_branch

        script = '{} fetch {} {}'.format(self.exec, configuration['repository']['remote'], local_branch)
        out = self.run_script(script)
        logger.debug('fetch output: {}'.format(out))

        script = '{} diff {} {}'.format(self.exec, local_branch, remote_branch)
        out = self.run_script(script)
        logger.debug('diff output: {}'.format(out))

        # if the output is blank, then the remote branch and the local branch are the same
        if out.strip() == '':
            logger.debug('is not new')
            return False
        else:
            logger.debug('is new')
            return True

    def tests_pass(self, config=None):
        """
        Determines if the test server is passing or failing on this branch

        :param config: dictionary containing the configuration
        :return: True if tests pass or False
        """
        configuration = config if config else self.config

        if 'test' in configuration.keys():
            raise NotImplementedError('')
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
            for script in configuration['scripts']['pre-pull']:
                out = self.run_script(script)

                logger.debug('script: {}'.format(script))
                logger.debug('script output: {}'.format(out))

        except KeyError:
            pass

    def pull(self, config=None):
        """
        Pulls the remote branch into the local branch

        :param config:
        :return:
        """
        configuration = config if config else self.config

        remote = configuration['repository']['remote']
        script = '{} pull {} {}'.format(self.exec, remote, self.get_branch(configuration))
        out = self.run_script(script)

        logger.debug('pull output: {}'.format(out))

    def post_pull_scripts(self, config=None):
        """
        Runs all post-pull scripts

        :param config: dictionary containing the configuration
        :return:
        """
        configuration = config if config else self.config

        try:
            for script in configuration['scripts']['post-pull']:
                out = self.run_script(script)

                logger.debug('script: {}'.format(script))
                logger.debug('script output: {}'.format(out))

        except KeyError:
            pass

    def stop_application(self):
        if self.app_ref:
            if sys.platform == 'win32':
                script = 'Taskkill /PID {} /F'.format(self.app_ref.pid)
            else:
                script = 'kill {}'.format(self.app_ref.pid)

            self.run_script(script)
            self.app_ref = None

    def start_application(self, config=None):
        configuration = config if config else self.config

        if 'application' in configuration.keys():
            if 'start' in configuration['application'].keys():
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
