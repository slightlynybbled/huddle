# Installation

Install:

    python setup.py install
    
Only standard library is utilized currently, no external packages required.
    
# Configuration

Multiple JSON files may be stored in a directory.  Any files prefixed with an underscore `_` will be ignored.
Files must have the extension `.json`.

## Fields

All valid fields can be found in `./huddle/example/_sample_config.json`.  An example of a working script
may be found in `./huddle/example/demo_config.json`.

# Running

Once installed, simply call the `auto_deploy` script from the command line using the appropriate configuration
path:

    huddle --config "C:\example"
    
All valid JSON configuration files that are contained within 'example' will each be managed on its own thread.

