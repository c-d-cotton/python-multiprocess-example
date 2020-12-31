#!/usr/bin/env python3
"""
An example script for how I usually conduct multiprocessing.
"""
import os
from pathlib import Path
import sys

__projectdir__ = Path(os.path.dirname(os.path.realpath(__file__)) + '/')

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

    sys.path.append(str(__projectdir__ / Path('submodules/split-function-runs/')))
    from splitfunctionruns_func import splitfunctionruns
    splitfunctionruns(os.path.join(__projectdir__, 'example_func.py'), 'f1', qsubfolder, runlists, pythonpath = pythonpath, createlabellist = True)


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

    sys.path.append(str(__projectdir__ / Path('submodules/split-function-runs/')))
    from splitfunctionruns_func import qsubfolder
    qsubfolder(qsubfolder, qsubcommand = qsubcommand)

