#!/usr/bin/env python

from __future__ import print_function
from os import path
import subprocess
import sys

# global state

commands = {}
config_path = path.expanduser('~/.cfg')
user_path = path.expanduser('~')
verbose = False
version = '0.1'

# helper functions
def execute(cmdString):
    subprocess.Popen(cmdString.split())

def git_bare(git_cmd):
    execute('git ' + git_cmd)

def git(git_cmd):
    git_bare('--git-dir={} --work-tree={} {}'.format(config_path, user_path, git_cmd))

def register(name, fn, dict):
    dict[name] = fn

def registerCommand(name, fn):
    register(name, fn, commands)

def verbose_print(string):
    if verbose:
        print(string)

# misc funtions

def help():
    verbose_print(commands.keys())

def init():
    if path.exists(path.expanduser(config_path)):
        verbose_print('Already configured')
    else:
        git_bare('init --bare {}'.format(config_path))
        git('config --local status.showUntrackedFiles no')
        verbose_print('Initialized config directory')


registerCommand('status', lambda: git('status'))
registerCommand('add', lambda: git('add'))
registerCommand('commit', lambda: git('commit'))
registerCommand('push', lambda: git('push'))
registerCommand('version', lambda: print(version))
registerCommand('help', help)
registerCommand('init', init)

# execute commands
if len(sys.argv) >= 1:
    if sys.argv[1] in commands:
        commands[sys.argv[1]]()
    else:
        print('Not a valid command')
else:
    help()
