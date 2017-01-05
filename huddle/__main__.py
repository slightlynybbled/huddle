import sys
import os
import json
import threading
import time

from huddle.manage import ApplicationManager


def main():
    print(sys.argv)

    if '-c' in sys.argv:
        index = sys.argv.index('-c') + 1
        directory = os.path.abspath(sys.argv[index])
        files = [f for f in os.listdir(directory) if '.json' in f]
        files = [f for f in files if f[0] != '_']

        print('configuration files: {}'.format(files))
    elif '--config' in sys.argv:
        index = sys.argv.index('--config') + 1
        directory = os.path.abspath(sys.argv[index])
        files = [f for f in os.listdir(directory) if '.json' in f]
        files = [f for f in files if f[0] != '_']

        print('configuration files: {}'.format(files))
    else:
        # if no config script is specified, then look for json files in the current directory
        directory = os.path.abspath(os.getcwd())
        files = [f for f in os.listdir(directory) if '.json' in f]
        files = [f for f in files if f[0] != '_']
        print('no configuration specified, using {}'.format(files))

    application_threads = []

    for f in files:
        print('loading: ', os.path.join(directory, f))
        with open(os.path.join(directory, f), 'r') as file:
            config = json.load(file)
            thread = threading.Thread(target=ApplicationManager, args=(config, ), daemon=True)
            thread.start()
            application_threads.append(thread)

    while len(files) > 0:
        time.sleep(1)

if __name__ == '__main__':
    main()
