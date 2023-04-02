# -*- coding: utf-8 -*-
# -*- mode: python; -*-
"""exec" "`dirname \"$0\"`/call.sh" "$0" "$@"; """
from __future__ import print_function

import time
import os
import sys
import csv
import json

import util

__doc__ = """
Created on Tue Jan 20 11:55:00 2015

@author: joschi
"""

input_format = {}

def analyzeFile(inputFile, counter):
    idField = input_format["patient_id"]
    with open(inputFile) as csvFile:
        reader = csv.DictReader(csvFile)
        for row in reader:
            id = row[idField]
            if id in counter:
                counter[id] += 1
            else:
                counter[id] = 1

def compute(allPaths, counter, human_readable, output, filter_zero=False):
    for (path, isfile) in allPaths:
        if isfile:
            analyzeFile(path, counter)
        else:
            util.process_directory(path, lambda file, printInfo: analyzeFile(file, counter))

    list = counter.keys()
    if filter_zero:
        list = [ k for k in list if counter[k] > 0 ]
    list.sort(key = lambda k: counter[k])
    padding = len(str(counter[list[len(list) - 1]])) if list else 0
    total = 0
    try:
        for id in list:
            num = counter[id]
            total += num
            if human_readable:
                print('{0:{width}}'.format(num, width=padding) + ' ' + id, file=output)
            else:
                print(id, file=output)
        if human_readable:
            print('', file=output)
            print('time: '+str(time.clock() - starttime)+'s', file=output)
            print('ids: '+str(len(list)), file=output)
            print('entries: '+str(total), file=output)
            print('mean: '+str(total / len(list)), file=output)
    except IOError as e:
        if e.errno != 32:
            raise

def usage():
    print('usage: {0} [-h] [-m] -f <format> -- <file or path>...'.format(sys.argv[0]), file=sys.stderr)
    print('-h: print help', file=sys.stderr)
    print('-m: batch compatible output', file=sys.stderr)
    print('-f <format>: specifies table format file', file=sys.stderr)
    print('<file or path>: a list of input files or paths containing them', file=sys.stderr)
    exit(1)

if __name__ == '__main__':
    human_readable = True
    starttime = time.clock()
    counter = {}
    allPaths = []
    args = sys.argv[:]
    args.pop(0)
    while args:
        arg = args.pop(0)
        if arg == '--':
            break
        if arg == '-h':
            usage()
        elif arg == '-m':
            human_readable = False
        elif arg == '-f':
            if not args or args[0] == "--":
                print('-f requires format file', file=sys.stderr)
                usage()
            util.read_format(args.pop(0), input_format, usage)
        else:
            print('illegal argument: '+arg, file=sys.stderr)
            usage()
    util.convert_paths(args, allPaths)
    if not len(allPaths):
        print('no path given', file=sys.stderr)
        usage()
    compute(allPaths, counter, human_readable, sys.stdout)
