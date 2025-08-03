uw_course_api 1.0.0 documentation (WIP)

uw_course_api.py -h: display help menu
uw_course_api.py [command] -h: help for command

uw_course_api.py -all: download ALL courses. you can stop and continue where you left off. options
	[-u]: updates existing course data, if needed (add -f to force updates on all files)
	[-r]: clears ALL files and re-downloads from scratch

(refer to <...> -h for help with other commands)

uw_course_api.py -d [commands...]: enter developer mode, contains debug/testing/WIP etc. features.

The script should automatically install any missing packages itself. If not, here is the list of req packages for imports


__future__
sys,subprocess,importlib.util,argparse,json,time
pathlib
datetime
requests
rich.live
rich.panel
rich.text