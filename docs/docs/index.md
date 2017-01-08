# Huddle

Huddle is an auto-deployment file and application management tool designed to work well in 
auto-scaling environments in which the end number of servers or clients is unknown.  This 
includes auto-scaling web servers and IoT devices, amongst others.

Applications are controlled through huddle using [configuration files](configfiles.md)
which are written in `.json` format.  Each file or application to be controlled will
have its own configuration file, which may be as simple or as complex as the user wishes.

