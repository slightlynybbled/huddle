import subprocess
import os
import sys

class Repo:
    """ Not intended for direct use, but to enforce a structure """

    def __init__(self):
        pass

    def clone(self, *args):
        raise NotImplementedError

    def fetch(self):
        raise NotImplementedError

    def pull(self):
        raise NotImplementedError

    def diff(self):
        raise NotImplementedError

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


class Git(Repo):

    def __init__(self, local_path, remote_path, executable=None, branch='master', remote='origin'):
        super().__init__()

        if executable:
            self.exec = executable
        else:
            if sys.platform == 'win32':
                self.exec = 'C:/Program Files/Git/bin/git'
            else:
                self.exec = '/usr/bin/git'

        self.local_path = local_path
        self.remote_path = remote_path
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

    def pull(self):
        script = '{} pull {} {}'.format(self.exec, self.remote, self.branch)
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


