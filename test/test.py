import sys
import shutil
import os
import stat
import time

import pytest
import huddle.manage


def remove_readonly(func, path, excinfo):
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except FileNotFoundError:
        pass


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

    # teardown - delete extra git repository
    remove_count = 0
    removed = False
    while remove_count < 5 and not removed:
        try:
            shutil.rmtree(local_path, onerror=remove_readonly)
            removed = True
        except PermissionError:
            time.sleep(1.0)

        remove_count += 1


def test_create_app_manager(app_manager):
    assert True


def test_default_exec(app_manager):
    assert app_manager.exec == '/usr/bin/git'


def test_win32_exec(app_manager):
    app_manager.load_and_validate()
    assert app_manager.exec == 'C:/Program Files/Git/bin/git'



