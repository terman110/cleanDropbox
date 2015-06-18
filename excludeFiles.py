#!/usr/bin/python

from __future__ import (absolute_import, division, print_function, unicode_literals)

import os
import sys
import shutil
import re

ignore_path = './_ignore'
__debug = False #True

def rmfile(file):
	if not __debug:
		os.remove(file)

def rmdir(dir):
	if not __debug:
		shutil.rmtree(dir)

def dirIsEmpty(path):
	return len(os.listdir(path)) <= 0

def question(question, default="yes"):
    valid = {"yes": True, "y": True, "j": True, "ja": True,
             "no": False, "n": False, "nein": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no'.\n")

def parseIgnoreFile(ignore_path):
	# Read ifgnore file
	lines = []
	with open(ignore_path) as f:
	    lines = f.read().splitlines()

	# Remove empty
	lines = [x for x in lines if x]

	# Remove spaces
	for i in range(len(lines)):
		lines[i] = lines[i].replace(' ','')
		lines[i] = lines[i].replace('.','\\.')
		lines[i] = lines[i].replace('*','.*')

	# Remove comments
	lines = [x for x in lines if not x[0] == '#']

	# Remove duplicates
	lines = sorted(set(lines))

	return lines

def listDropboxFiles(base_path='.'):
	lines = [os.path.join(dp, f) for dp, dn, fn in os.walk(base_path) for f in fn]
	lines = [x for x in lines if not '.dropbox' in x]
	return lines

def listFilesToRemove(ignore, files):
	# Prepare list of directory expressions
	ignd = [x for x in ignore if '/' in x]
	for i in range(len(ignd)):
		if ignd[i][-1] == '/':
			ignd[i] = ignd[i][:-1]
		if not ignd[i][0] == '/':
			ignd[i] = '/' + ignd[i]
		ignd[i] = '.*' + ignd[i] + '$'

	# Prepare list of file expressions
	ignf = [x for x in ignore if not x in ignd]
	for i in range(len(ignf)):
		ignf[i] = '^' + ignf[i] + '$'

	# Files to remove
	rfiles = []
	for ign in ignf:
		rfiles += [x for x in files if re.search(ign, os.path.split(x)[1])]

	# Directories to remove
	rdirs = []
	for ign in ignd:
		rdirs += [x for x in files if re.search(ign, os.path.split(x)[0])]
	for i in range(len(rdirs)):
		rdirs[i] = os.path.split(rdirs[i])[0]
	rdirs = list(set(rdirs))

	return (rfiles, rdirs)

def removeFiles(files, dirs):
	print('Delete files:')
	for f in files:
		if os.path.isfile(f):
			print('  ', os.path.split(f)[1])
			rmfile(f)

	print('Delete dirs:')
	for f in dirs:
		if os.path.isdir(f):
			if not dirIsEmpty(f):
				if not question("  Dir is not empty.\n  "+f+"\nRemove it anyway? ", default="no"):
					continue
			print("  ", f)
			rmdir(f)

if __name__ == '__main__':
	print('Parse ignore file ...')
	ignore = parseIgnoreFile(ignore_path)

	print('List Dropbox files ...')
	dbfiles = listDropboxFiles()

	print('Extract files to remove ...')
	(remf, remd) = listFilesToRemove(ignore, dbfiles)

	removeFiles(remf, remd)