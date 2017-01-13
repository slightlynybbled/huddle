<img src="/huddle/img/huddle.png" style="float: right; margin-left: 10px;">

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

# Motivation

<img src="/huddle/img/git-push-model.png" style="float: right; margin-left: 10px;">

It would appear that most auto-deployment tools are focused on using git hooks and use a 'push'
model to deploy from Git to various nodes.  In the simplest case, this involves knowing the IP
address or similar information for each server.  In the most complex cases, this involves 
a coordinator and workers testing, deploying, and pushing to the servers.

<img src="/huddle/img/pull-model.png" style="float: right; margin-left: 10px;">

In an environment of unknown scale - such as auto-scaling web servers and IoT devices, the 
devices themselves need to be intelligent enough to self-deploy.  This is where huddle comes
in.  Each device takes charge of its self and does a pull as the git repository is updated.
This has the advantage of not requiring any sort of global registry or count of devices and
scales very well.

In addition, huddle will pull from any number of git repositories and initiate any number of 
applications.  Huddle only requires one configuration script per application.

In auto-scaling environments, typically an initial image is created for the server or IoT device 
which contains:

 - python environment
 - huddle installation
 - appropriate huddle configuration script(s)
 - huddle loaded at startup (probably `@restart` cron job)

Each server then manages its own application suite!
