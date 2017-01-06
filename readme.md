# Huddle

`Huddle` is an application that allows one or more programs to be started, monitored, stopped, updated, and 
restarted from one or more configuration files.  This program works in Windows and Linux.

## Configuration File Format

The purpose of this program is to auto-deploy any arbitrary program in a fashion that is more suited to auto-scaling
servers.  Instead of having a git hook that pushes to a known set of servers, a running server continually polls
the git at specified intervals and - when there is an update - the server will pull the new data and re-deploy.

All of this is done using a configuration file, so no Python knowledge is required.

The simplest example of a configuration file will simply check for updates for a set of files every 60s:

    {
      "repository": {
        "remote path": "https://github.com/slightlynybbled/dummy.git",
        "local path": "/home/ubuntu/git_example",
      },
    }
    
A more comprehensive configuration file:

    {
      "repository": {
        "remote": "origin",
        "remote path": "https://github.com/slightlynybbled/dummy.git",
        "local path": "/home/ubuntu/git_example",
        "branch": "develop",
        "executable": "/usr/bin/git"
      },
    
      "timing": {
        "minimum": 60,
        "maximum": 600
      },
    
      "application": {
        "start": "/home/ubuntu/py3env/bin/python -m dummy_app.py"
      }
    }
    
This file will initially start the application using the command under `start`, and check for application updates
every 60s to 600s (random).  When an update to the `develop` branch is detected, the application will be halted, the
local file updated, and the application re-started automatically.

The current flow chart for each application is:

![desired flow chart](flow-chart.png)

This program, at initialization, should be all that is required to clone a remote repository, verify test status,
sync changes, and stop/start/reboot the application.

## Configuration Files

All configuration files should be saved within a particular directory with `.json` extensions.  Any file that is
prefixed with an underscore `_` will be ignored.

    /home/ubuntu/config_files
        /app1.json
        /app2.json
        /_app3.json
        
Or, in windows:

    C:\config_files
        \app1.json
        \app2.json
        \_app3.json
        
Note that `_app3.json` will be ignored.

## Running the Application

To execute huddle, simply pass it the path to your configuration files using the `-c` or `--config` options:

    python -m huddle -c /home/ubuntu/config_files
    python -m huddle -c C:\config_files
    
Depending on the install location for huddle (virtual environments, etc.), the `python -m` may not be required:

    huddle -c /home/ubuntu/config_files
    huddle -c C:\config_files

# Status

The interface is stable enough to depend on.  Testing is at about 60% on unit tests and I have verified basic
functionality on windows and on linux (Debian).  Currently, the 'check tests' portion of the API is not implemented
and - if attempted - will raise a `NotImplementedError`.

# Installation

Install with `pip install huddle` or simply download the most recent version of this repository and
`python setup.py install`.

