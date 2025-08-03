uw_course_api 1.0.0 documentation (WIP)

uw_course_api.py -h: display help menu
uw_course_api.py [command] -h: help for specified command

uw_course_api.py -all: download ALL courses. you can stop the script and continue where you left off. options
	[-u]: updates existing course data, if needed (add [-f] to force updates on all files)
	[-r]: deletes ALL files in c-data\courses\... and re-downloads from scratch

uw_course_api.py -d [commands...]: enter developer mode, contains debug/testing/WIP etc. features.
...
(refer to <command> [-h] for help with other commands)
...



By default, the ALL command saves data to <current directory>\c-data\courses\<course>.json. 
The COURSE command saves to c-data\<course>.json. The output location can be configured through the [--out] option.



The script should automatically install any missing packages itself. If not, here is the list of req packages/imports


__future__
sys,subprocess,importlib.util,argparse,json,time
pathlib
datetime
requests
rich.live
rich.panel
rich.text