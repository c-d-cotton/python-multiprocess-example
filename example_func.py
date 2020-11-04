#!/usr/bin/env python3
"""
An example script for how I usually conduct multiprocessing.
"""
# PYTHON_PREAMBLE_START_STANDARD:{{{

# Christopher David Cotton (c)
# http://www.cdcotton.com

# modules needed for preamble
import importlib
import os
from pathlib import Path
import sys

# Get full real filename
__fullrealfile__ = os.path.abspath(__file__)

# Function to get git directory containing this file
def getprojectdir(filename):
    curlevel = filename
    while curlevel is not '/':
        curlevel = os.path.dirname(curlevel)
        if os.path.exists(curlevel + '/.git/'):
            return(curlevel + '/')
    return(None)

# Directory of project
__projectdir__ = Path(getprojectdir(__fullrealfile__))

# Function to call functions from files by their absolute path.
# Imports modules if they've not already been imported
# First argument is filename, second is function name, third is dictionary containing loaded modules.
modulesdict = {}
def importattr(modulefilename, func, modulesdict = modulesdict):
    # get modulefilename as string to prevent problems in <= python3.5 with pathlib -> os
    modulefilename = str(modulefilename)
    # if function in this file
    if modulefilename == __fullrealfile__:
        return(eval(func))
    else:
        # add file to moduledict if not there already
        if modulefilename not in modulesdict:
            # check filename exists
            if not os.path.isfile(modulefilename):
                raise Exception('Module not exists: ' + modulefilename + '. Function: ' + func + '. Filename called from: ' + __fullrealfile__ + '.')
            # add directory to path
            sys.path.append(os.path.dirname(modulefilename))
            # actually add module to moduledict
            modulesdict[modulefilename] = importlib.import_module(''.join(os.path.basename(modulefilename).split('.')[: -1]))

        # get the actual function from the file and return it
        return(getattr(modulesdict[modulefilename], func))

# PYTHON_PREAMBLE_END:}}}

import multiprocessing
import shutil

# Functions I Always Need:{{{1
def f1(inputlist):
    """
    inputlist is a list that I input into the function for each run
    """
    filenamestem, output = inputlist

    try:
        os.makedirs(os.path.join(__projectdir__, 'temp', 'output'))
    except Exception:
        None

    with open(os.path.join(__projectdir__, 'temp', 'output', filenamestem + str(output) + '.txt'), 'w+') as f:
        f.write(str(output))


def gettodolist():
    """
    This returns a list of inputlists to run with f1.
    """
    todolist = []
    for filenamestem in ['a', 'b', 'c']:
        for i in range(10):
            todolist.append([filenamestem, i])

    return(todolist)
            

def deletetempfolder():
    if os.path.isdir(os.path.join(__projectdir__, 'temp')):
        shutil.rmtree(os.path.join(__projectdir__, 'temp'))


# Different Run Methods:{{{1
def onebyone():
    """
    Just run the list one by one on the same processor
    """
    deletetempfolder()

    for inputlist in gettodolist():
        f1(inputlist)


def domultiprocessing():
    deletetempfolder() 

    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    pool.map(f1, gettodolist())


def qsub_splitfiles():
    """
    This function creates a folder of python and bash files each of which calls f1 for a single inputlist
    I need this for qsub since qsub needs to run bash files (and bash needs to call a python file)
    """
    qsubfolder = os.path.join(__projectdir__, 'temp', 'qsub')

    try:
        os.makedirs(qsubfolder)
    except Exception:
        None

    if os.path.isfile(__projectdir__ / Path('me/paths/pythonpath.txt')):
        with open(__projectdir__ / Path('me/paths/pythonpath.txt')) as f:
            pythonpath = f.read()
        if pythonpath[-1] == '\n':
            pythonpath = pythonpath[: -1]
    else:
        pythonpath = None

    runlists = gettodolist()

    importattr(__projectdir__ / Path('submodules/split-function-runs/splitfunctionruns_func.py'), 'splitfunctionruns')(os.path.join(__projectdir__, 'example_func.py'), 'f1', qsubfolder, runlists, pythonpath = pythonpath, createlabellist = True)


def qsub_run():
    deletetempfolder() 

    qsub_splitfiles()

    # get necessary run files
    runlists = gettodolist()

    if os.path.isfile(__projectdir__ / Path('me/paths/qsub.txt')) is True:
        with open(__projectdir__ / Path('me/paths/qsub.txt')) as f:
            qsubcommand = f.read()
        if qsubcommand[-1] == '\n':
            qsubcommand = qsubcommand[: -1]
    else:
        qsubcommand = 'qsub'

    # set memory needed
    qsubcommand = qsubcommand + ' -l mem_free=4G'

    qsubfolder = os.path.join(__projectdir__, 'temp', 'qsub')

    importattr(__projectdir__ / Path('submodules/split-function-runs/splitfunctionruns_func.py'), 'qsubfolder')(qsubfolder, qsubcommand = qsubcommand)

