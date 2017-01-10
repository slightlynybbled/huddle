# Running in a Virtual Environment

The below assumes ubuntu linux, but applies equally as well to other distributions
and to windows.

First, the user must create the virtual environment:

    ubuntu ~\$ virtualenv -p python3 /home/ubuntu/py3env

Install Huddle into the environment:

    ubuntu ~\$ /home/ubuntu/py3env/bin/pip install huddle 

Create a location for your configuration files:

    mkdir /home/ubuntu/huddle_config

Place all JSON configuration files into the configuration directory, then start huddle:

    /home/ubuntu/py3env/bin/huddle -c /home/ubuntu/huddle_config 

Huddle will then start your applications!

## Running at Startup (Linux)

The most straightforward method of starting Huddle at startup is to use cron jobs.

    crontab -e 

Or, if your application requires root permissions:

    sudo crontab -u root -e 

This will open a text editor that allows you to enter applications to execute at certain
times.  One of these times is at reboot.  Enter the following line at the bottom of the 
file:

    @reboot /home/ubuntu/py3env/bin/huddle -c /home/ubuntu/huddle_config

Now, Huddle will start and run the configuration files at reboot!

# Server Considerations

## Git Executable

Huddle, by default, uses the Git executable already installed on the user's machine
in order to manipulate the Git repository.  In Windows, the default executable is
in `C:/Program Files/Git/bin/git`.  In Linux, the default executable is in `\usr\bin\git`.
It is recommended that the [`executable`](configfiles.md#Repository) configuration file
be used to specify the executable location. 

## Authentication

When working with remote repositories, you must have the server set up so that you can
simply `git clone origin master` on the command line without having to enter a password.
This usually involves creating private and public keys on the pulling server and uploading
the public key to the repository server, although other methods are available.

In auto-scaling environments, it is recommended to generate this key on the base image
so that all of the auto-generated machines have access to the key.
