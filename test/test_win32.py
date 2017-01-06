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
    remove_time = 0.0
    time_inc = 0.1
    removed = False
    while remove_time < 10.0 and not removed:
        try:
            shutil.rmtree(local_path, onerror=remove_readonly)
            removed = True
        except PermissionError:
            time.sleep(time_inc)

        remove_time += time_inc


def test_create_app_manager(app_manager):
    assert True


def test_default_exec(app_manager):
    assert app_manager.exec == '/usr/bin/git'


def test_win32_exec(app_manager):
    app_manager.load_and_validate()
    assert app_manager.exec == 'C:/Program Files/Git/bin/git'


def test_custom_exec(app_manager):
    config = app_manager.config
    config['repository']['executable'] = 'C:/Program Files/Git/bin/git'

    app_manager.load_and_validate()
    assert app_manager.exec == 'C:/Program Files/Git/bin/git'


def test_default_branch(app_manager):
    config = app_manager.config
    config['repository'].pop('branch')

    app_manager.load_and_validate()
    assert app_manager.get_branch() == 'master'


def test_no_tests_specified(app_manager):
    assert app_manager.tests_pass()


def test_tests_specified(app_manager):
    config = app_manager.config
    config['test'] = {}

    with pytest.raises(NotImplementedError):
        app_manager.tests_pass(config)


def test_pre_pull_scripts(app_manager):
    config = app_manager.config
    config['scripts'] = {
        'pre-pull': [
            'cmd /c echo 0 1 2',
            'cmd /c echo 3 4 5'
        ]
    }

    outs = app_manager.pre_pull_scripts(config)

    assert '0 1 2' in outs[0]
    assert '3 4 5' in outs[1]


def test_pre_pull_scripts_empty(app_manager):
    outs = app_manager.pre_pull_scripts()

    assert outs == []


def test_post_pull_scripts(app_manager):
    config = app_manager.config
    config['scripts'] = {
        'post-pull': [
            'cmd /c echo 0 1 2',
            'cmd /c echo 3 4 5'
        ]
    }

    outs = app_manager.post_pull_scripts(config)

    assert '0 1 2' in outs[0]
    assert '3 4 5' in outs[1]


def test_post_pull_scripts_empty(app_manager):
    outs = app_manager.post_pull_scripts()

    assert outs == []

