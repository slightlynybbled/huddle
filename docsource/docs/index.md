# Huddle

Huddle is an auto-deployment file and application management tool designed to work well in 
auto-scaling environments in which the end number of servers or clients is unknown.  This 
includes auto-scaling web servers and IoT devices, amongst others.

Applications are controlled through huddle using [configuration files](configfiles.md)
which are written in `.json` ir `.ini` format.  Each file or application to be controlled will
have its own configuration file, which may be as simple or as complex as the user wishes.

An example configuration in JSON:

    {
      "repository": {
        "remote": "origin",
        "remote path": "https://github.com/slightlynybbled/dummy.git",
        "local path": "C:/_code/_git_example",
        "branch": "master",
        "executable": "C:/Program Files/Git/bin/git.exe"
      },
    
      "timing": {
        "minimum": 10,
        "maximum": 20
      },
    
      "application": {
        "start": "python -m dummy_app.py"
      }
    }

The same configuration as an INI file:

    [repository]
    remote = origin
    remote path: https://github.com/slightlynybbled/dummy.git
    local path: C:/_code/_git_example
    branch: master
    executable: C:/Program Files/Git/bin/git.exe
    
    [timing]
    minimum = 10
    maximum = 20
    
    [application]
    start = python -m dummy_app.py

