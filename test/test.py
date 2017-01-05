import sys
import shutil
import os
import stat

import pytest
import huddle.manage


def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)


@pytest.fixture
def app_manager(request):
    if sys.platform == 'win32':
        executable = 'C:/Program Files/Git/bin/git'
        local_path = 'C:/_code/_git_example'
    else:
        executable = '/usr/bin/git'
        local_path = '/home/ubuntu/git_example'

    config = {
        'repository': {
            'executable': executable,
            'remote': 'origin',
            'local path': local_path,
            'remote path': 'https://github.com/slightlynybbled/dummy.git',
            'branch': 'master'
        }
    }

    manager = huddle.manage.ApplicationManager(config, runner=False)
    yield manager

    # teardown
    shutil.rmtree(local_path, onerror=remove_readonly)


def test_create_app_manager(app_manager):
    assert True
