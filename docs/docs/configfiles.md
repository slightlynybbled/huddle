# Settings

All settings for a particular configuration are encapsulated into a single JSON object
which consists of key-value pairs.  Each section below will consist of an object that
contains the keys and information required to properly configure each key.

## Repository

The `repository` key contains all remote/local relationship data, including paths to the
executable.  This is the most important field and the only one that is actually required.

| key           | description            | valid values   | default value |
|---------------|------------------------|----------------|---------------|
| `remote`      | the name of the remote | any string     | "origin"      |
| `remote path` | the remote url or path | any string     | -             |
| `local path`  | the local path         | any string     | -             |
| `branch`      | the git branch to sync | any string     | "master"      |
| `executable`  | the executable         | string/path | "/usr/bin/git" or "C:\Program Files\Git\bin\git.exe" |

Example of `repository` object:

    {
        "repository": {
            "remote": "origin",
            "remote path": "https://github.com/slightlynybbled/dummy.git",
            "local path": "C:/_code/_git_example",
            "branch": "master",
            "type": "git",
            "executable": "/usr/bin/git"
        }
    }

## Testing

The `test` key is reserved, but not currently implemented.

## Timing

If no timing is specified, then the default will be 60 seconds.  If only a `minimum` is
specified, then the remote will be checked at that interval.  Finally, if a `minimum`
and a `maximum` are specified, then the remote will be checked for updates at a random
time between the `minimum` and `maximum` values.

| key           | description             | valid values   | default value |
|---------------|-------------------------|----------------|---------------|
| `minimum`     | minimum time in seconds | any integer    | 60            |
| `maximum`     | maximum time in seconds | any string     | -             |

Example of `timing` object:

    "timing": {
        "minimum": 30,
        "maximum": 300
    },

## Application 

The `application` key is used to identify the application that is to be started and 
monitored.  On remote update, this is the application that will be stopped, updated,
and reloaded.

| key           | description             | valid values   | default value |
|---------------|-------------------------|----------------|---------------|
| `start`       | the start executable    | any integer    | 60            |

Example of `application` object:

    "application": {
        "start": "python -m dummy_app.py"
    },

## Scripts

There are two times at which an arbitrary script or group of `scripts` must be executed
and that is `pre-pull` and `post-pull`.  The `pre-pull` scripts are supplied as a JSON 
array, with each being executed in succession.

This `scripts` will execute two scripts before the pull and will reboot the machine
after the pull

    "scripts": {
        "pre-pull": [
            "/bin/ls /home/ubuntu/ > /home/ubuntu/values.txt", 
            "/bin/ls /etc/ > /home/ubuntu/values.txt"
        ],
        "post-pull": ["sudo reboot"]
    }

# Example Configuration Scripts

## Minimal File Sync 

This configuration will keep the local `C:/_code/_git_example` directory in synce with the 
remote `develop` branch.  It will not start or run any applications.

    {
        "repository": {
            "remote": "origin",
            "remote path": "https://github.com/slightlynybbled/dummy.git",
            "local path": "C:/_code/_git_example",
            "branch": "develop",
            "executable": "C:/Program Files/Git/bin/git"
        }
    }

## Syncing/Run an Application

This configuration will sync every 60s to 600s.  When there is an update, this application 
will be halted, updated, then restarted after the update.

    {
        "repository": {
            "remote": "origin",
            "remote path": "https://github.com/slightlynybbled/dummy.git",
            "local path": "C:/_code/_git_example",
            "branch": "master",
            "executable": "C:/Program Files/Git/bin/git"
        },

        "timing": {
            "minimum": 60,
            "maximum": 600
        },

        "application": {
            "start": "python -m dummy_app.py"
        }
    }

## Sync Application/Reboot Server

This configuration will check the remote every 60s and, when new data is available, huddle
will stop the application and reboot the machine with a `post-pull` script.

    {
        "repository": {
            "remote": "origin",
            "remote path": "https://github.com/slightlynybbled/dummy.git",
            "local path": "C:/_code/_git_example",
            "executable": "/usr/bin/git"
        },

        "application": {
            "start": "python -m dummy_app.py"
        },

        "scripts": {
            "post-pull": ["/sbin/reboot"]
        }
    }
