import logging
import subprocess
import os
import sys
import time
import random
import json

logger = logging.getLogger(__name__)


def check_git_for_updates(branch='master'):
    """
    Periodically checks git for revisions to the master branch and - if there has been an update -
    then download all updates and reboot the server.
    :return:
    """

    os.chdir(os.path.dirname(__file__))

    logger.debug('platform: {}'.format(sys.platform))

    while True:
        if sys.platform == 'win32':
            p = subprocess.Popen(['C:/Program Files/Git/bin/git', 'pull', 'origin', 'master'], stdout=subprocess.PIPE)
        else:
            p = subprocess.Popen(['/usr/bin/git', 'pull', 'origin', branch], stdout=subprocess.PIPE)

        stdout = ''
        for line in p.stdout:
            stdout += line.decode('utf-8')

        if 'changed' in stdout:
            # install new requirements
            p = subprocess.Popen(['../py3env/bin/pip', 'install', '--upgrade', '-r', 'requirements.txt'], stdout=subprocess.PIPE)

            if sys.platform != 'win32':
                os.system('sudo reboot')

        # wait a random amount of time between 60s and 600s
        sleep_time = float(random.randint(60, 600))
        time.sleep(sleep_time)

if __name__ == '__main__':
    default_config_file = 'sample_config.json'

    print(sys.argv)
    print('config file: {}'.format(default_config_file))

    with open(default_config_file, 'r') as f:
        for line in f:
            print(line)

