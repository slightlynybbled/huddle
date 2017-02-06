import sys
import os
import json
import threading
import time
import logging

from huddle.manage import ApplicationManager
from huddle.util import config_parser_load

logger = logging.getLogger(__name__)


def main():
    if '--debug' in sys.argv or '-d' in sys.argv:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    logger.debug('arguments: {}'.format(sys.argv))

    if '-c' in sys.argv or '--config' in sys.argv:
        if '-c' in sys.argv:
            index = sys.argv.index('-c') + 1
        else:
            index = sys.argv.index('--config') + 1
        directory = os.path.abspath(sys.argv[index])

        json_files = [f for f in os.listdir(directory) if '.json' in os.path.splitext(f.lower())]
        json_files = [f for f in json_files if f[0] != '_']

        ini_files = [f for f in os.listdir(directory) if '.ini' in os.path.splitext(f.lower())]
        ini_files = [f for f in ini_files if f[0] != '_']

        files = json_files + ini_files

        logger.debug('configuration files: {}'.format(files))
    else:
        # if no config script is specified, then look for json files in the current directory
        directory = os.path.abspath(os.getcwd())

        json_files = [f for f in os.listdir(directory) if '.json' in os.path.splitext(f.lower())]
        json_files = [f for f in json_files if f[0] != '_']

        ini_files = [f for f in os.listdir(directory) if '.ini' in os.path.splitext(f.lower())]
        ini_files = [f for f in ini_files if f[0] != '_']

        files = json_files + ini_files

        logger.debug('no configuration specified, using {}'.format(files))

    application_threads = []

    for f in files:
        logger.info('loading: {}'.format(os.path.join(directory, f)))
        if '.json' in f.lower():
            with open(os.path.join(directory, f), 'r') as file:
                config = json.load(file)

                thread = threading.Thread(target=ApplicationManager, args=(config, ), daemon=True)
                thread.start()
                application_threads.append(thread)
        elif '.ini' in f.lower():
            config = config_parser_load(os.path.join(directory, f))

            thread = threading.Thread(target=ApplicationManager, args=(config, ), daemon=True)
            thread.start()
            application_threads.append(thread)
        else:
            raise ValueError('incorrect configuration file type - must be JSON or INI')

    while len(files) > 0:
        time.sleep(1)

    print('there are no files currently active, exiting...')


if __name__ == '__main__':
    main()
