import subprocess
import time
import logging
import random
import os
import signal
import threading
import requests
import socket

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
        self.block_update = False
        self.block_watchdog = False

        if 'watchdog' in self.config:
            self.watchdog_thread = threading.Thread(target=self.watchdog, args=(config, ))
            self.watchdog_thread.start()

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
            try:
                os.kill(self.app_ref.pid, signal.CTRL_C_EVENT)
            except AttributeError:
                os.kill(self.app_ref.pid, signal.SIGTERM)
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

    def check_socket(self, config=None):
        """
        Checks the application health using the specified host and port
        :param config: dictionary containing the configuration
        :return:
        """
        configuration = config if config else self.config

        # load the proper values from the configuration
        try:
            port = configuration['watchdog']['port']
        except KeyError:
            port = '80'

        try:
            host = configuration['watchdog']['host']
        except KeyError:
            host = '127.0.0.1'

        try:
            request = configuration['watchdog']['request']
        except KeyError:
            request = 'watchdog'

        # create a socket and send the health request
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            address = (host, int(port))
            sock.connect(address)
            sock.sendall(bytes(request, 'utf-8'))
        except ConnectionError:
            return False

        # read the response from the socket
        response = b''
        received = b'1'
        while received != b'':
            received = sock.recv(128)
            response += received
        sock.close()

        response = response.decode('utf-8')

        # check the response against the expected response and return True or False
        try:
            application_check = True if configuration['watchdog']['response'] in response else False
        except KeyError:
            logger.debug('proper watchdog response not found')
            application_check = False

        return application_check

    def run(self, config):
        """
        Periodically runs the full script at the interval determined by the configuration

        :param config: dictionary containing the configuration
        :return:
        """
        configuration = config if config else self.config

        while True:
            # if an update is blocked, then skip this iteration of the update
            if self.is_new() and not self.block_update:
                logger.debug('branch is new')

                if self.tests_pass():
                    self.block_watchdog = True

                    self.stop_application()
                    self.pre_pull_scripts()
                    self.pull()
                    self.post_pull_scripts()
                    self.start_application()

                    self.block_watchdog = False

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

    def watchdog(self, config):
        """
        Implements a watchdog timer for the application that attempts a stop and restart if the application is not
        responding appropriately.

        :param config: dictionary containing the configuration
        :return:
        """
        configuration = config if config else self.config

        sleep_time = float(configuration['watchdog']['period']) if 'period' in configuration['watchdog'].keys() else 60.0
        time.sleep(sleep_time)

        while True:
            # if the watchdog is blocked by an update, then skip it this time
            if self.block_watchdog:
                # when blocked, then sleep for 1 second
                time.sleep(1.0)
            else:
                # when not blocked, then execute the normal watchdog code
                port = configuration['watchdog']['port'] if 'port' in configuration['watchdog'].keys() else '80'
                host = configuration['watchdog']['host'] if 'host' in configuration['watchdog'].keys() else '127.0.0.1'

                address = '{}:{}'.format(host, port)
                logger.debug('watchdog check of {}...'.format(address))

                # check the application health via http or via a socket
                if 'http' in host:
                    r = requests.get(address)
                    application_check = True if r.status_code == 200 else False
                else:
                    application_check = self.check_socket(configuration)

                if not application_check:
                    logger.debug('watchdog FAIL, restarting application')
                    # attempt to restart the application
                    self.block_update = True
                    self.stop_application()
                    self.start_application()
                    self.block_update = False
                else:
                    logger.debug('watchdog pass')

                time.sleep(sleep_time)
