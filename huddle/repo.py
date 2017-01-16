import subprocess
import os
import sys
import requests
from hashlib import sha256

from huddle.util import find_all_files


class Repo:
    """ Not intended for direct use, but to enforce a structure """

    def __init__(self, local_path, remote_path):
        self.local_path = local_path
        self.remote_path = remote_path

        try:
            os.chdir(self.local_path)
        except FileNotFoundError:
            pass

    def clone(self, *args):
        raise NotImplementedError

    def fetch(self):
        raise NotImplementedError

    def diff(self):
        raise NotImplementedError

    def pull(self):
        raise NotImplementedError


    @staticmethod
    def run_script(script):
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


class GitRepo(Repo):

    def __init__(self, local_path, remote_path, executable=None, branch='master', remote='origin'):
        super().__init__(local_path, remote_path)

        if executable:
            self.exec = executable
        else:
            if sys.platform == 'win32':
                self.exec = 'C:/Program Files/Git/bin/git'
            else:
                self.exec = '/usr/bin/git'

        self.branch = branch
        self.remote = remote

    def clone(self):
        script = '{} clone {} {}'.format(self.exec, self.remote_path, self.local_path)
        out = self.run_script(script)

        try:
            os.chdir(self.local_path)
            return True, out
        except FileNotFoundError:
            return False, out

    def checkout(self):
        script = '{} checkout {}'.format(self.exec, self.branch)
        out = self.run_script(script)

        return True, out

    def fetch(self):
        script = '{} fetch {} {}'.format(self.exec, self.remote, self.branch)
        out = self.run_script(script)

        return True, out

    def diff(self):
        remote_branch = self.remote + '/' + self.branch

        script = '{} diff {} {}'.format(self.exec, self.branch, remote_branch)
        out = self.run_script(script)

        # if the output is blank, then the remote branch and the local branch are the same
        if out.strip() == '':
            return False, out
        else:
            return True, out

    def pull(self):
        script = '{} pull {} {}'.format(self.exec, self.remote, self.branch)
        out = self.run_script(script)

        return True, out


class HttpRepo(Repo):

    def __init__(self, local_path, remote_path, user=None, pw=None):
        super().__init__(local_path, remote_path)

        self.user = user
        self.pw = pw

    def clone(self):
        if self.user or self.pw:
            r = requests.get(self.remote_path, auth=(self.user, self.pw))
        else:
            r = requests.get(self.remote_path, auth=(self.user, self.pw))

        if r.status_code == 200:
            with open(self.local_path, 'wb') as f:
                f.write(r.content)
            return True, ''
        else:
            return False, ''

    def fetch(self):
        """ There is no http equivalent for 'fetch' in http/https """
        return False, ''

    def diff(self):
        # calculate md5 hash for all files in current directory that don't start with '_'
        local_hash = sha256()
        for file in find_all_files(self.local_path):
            with open(file, 'rb') as f:
                local_hash.update(f.read())

        # request the hash from the server
        server_hash = '0'

        if local_hash.hexdigest() == server_hash:
            return True, 'local and remote hash are the same'
        else:
            return False, 'local ({}) and remote ({}) hashes are different'.format(local_hash, server_hash)

    def pull(self):
        # in the http context, 'pull' and 'clone' have the same meaning
        self.clone()

