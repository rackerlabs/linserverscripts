#!/usr/bin/env python2
"""
This script identifies the max speed of CPUs based on the model name, then monitors the cores for speed stepping.
The goal is to retain the highest speed and identify cores that are not scaling properly.
monitor /proc/cpuinfo and track for changes
"""

import re
from time import sleep
import sys

class AutoVivification(dict):
    """Implementation of perl's autovivification feature."""
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value

class ansi:

    """
    This class is to display different color fonts
    example:
    print "Testing a color    [ %sOK%s ]" % (
        ansi.CYAN,
        ansi.ENDC
                    )
    or to avoid a new line
    import sys
    sys.stdout.write("%s%s" % (ansi.CLR,ansi.HOME))
    """
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    CLR = '\033[2J'
    HOME = '\033[H'

cpuspeed = AutoVivification()
cycle_counter=0
allclear=0

sys.stdout.write("%s%s" % (ansi.CLR,ansi.HOME))

while allclear == 0:
    infile = open('/proc/cpuinfo', 'r')
    cpuinfo = infile.readlines()
    cpu=""
    for line in cpuinfo:
        # cpu
        # model
        # mhz
        result = re.match('(processor|model name|cpu MHz)[\s:]+(\d*)(.*)', line.strip())
        # group 1 is category
        # group 2 is numbers (speed or processor number)
        # group 3 is anything following numbers (model name)

        if not result:
            continue
        if result.group(1)=="processor":
            # which CPU core are we talking about?
            cpu = int(result.group(2))
        elif result.group(1)=="model name" and not "model" in cpuspeed[cpu]:
            # we only set the model if it isn't already set, and we get the max speed at the same time too
            cpuspeed[cpu]["model"]=result.group(3)
            result = re.search('([\d\.]+)GHz', line.strip())
            cpuspeed[cpu]["maxmhz"]=int(float(re.search('([\d\.]+)GHz', line.strip()).group(1))*1000)
        elif result.group(1)=="cpu MHz":
            # you can't reference the variable that isn't set, so max alone doesn't work
            if not "mhz" in cpuspeed[cpu]:
                cpuspeed[cpu]["mhz"]=int(result.group(2))
            else:
                cpuspeed[cpu]["mhz"]=max(cpuspeed[cpu]["mhz"],int(result.group(2)))
    sys.stdout.write("%s" % (ansi.HOME,))
    # assume all the CPUs are good (allclear), then test for lower states. Exit if they are all clear.
    allclear=1
    for key in cpuspeed:
        # "stuck" CPUs tend to stay at 1200MHz, so flag those as red
        # If the CPU hit the model's max, or 1 over max if it is static, flag it green
        # If the CPU is in between, mark it yellow
        print "CPU : %s, Model: %s, Max: %s" % (key,cpuspeed[key]["model"],cpuspeed[key]["maxmhz"])
        if cpuspeed[key]["mhz"]==1200:
            status_color=ansi.RED
            allclear=0
        elif cpuspeed[key]["mhz"] >= cpuspeed[key]["maxmhz"]:
            status_color=ansi.GREEN
        else:
            status_color=ansi.YELLOW
            allclear=0
        print "Max observed speed: %s%s%s" % (status_color,cpuspeed[key]["mhz"],ansi.ENDC)
    infile.close()
    print "." * cycle_counter
    cycle_counter+=1
    sleep(.1)
