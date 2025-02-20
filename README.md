# cfgr

A configuration file manager and diff tool.

Problem:  I want to keep *some* of my OS configuration files under
version control.  The configuration file as placed in the OS is not in
a place where I want the entire directory under version control,
(i.e. /etc).

Strategy:  This tool, `cfgr`, will act as the "go between" performing
diff, push, and pull functionality between a directory tree of managed
configuration files and the deployed location (i.e. /etc) of that
configuration file.
