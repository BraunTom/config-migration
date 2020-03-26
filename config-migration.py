#!/usr/bin/env python

from __future__ import print_function
from os import path
import subprocess
import sys

# global state

commands = {}
config_path = path.expanduser('~/.cfg')
current_arg_index = 0
user_path = path.expanduser('~')
verbose = False
version = 0.1


# helper functions
def are_all_args_read():
    return len(sys.argv) - current_arg_index > 1

# Todo: wait for finish
def execute(cmdString):
    subprocess.Popen(cmdString.split())

def git_bare(git_cmd):
    # git command without any predefined parameters
    execute('git ' + git_cmd)

def git(git_cmd):
    # git command for working on the dotfile repo
    git_bare('--git-dir={} --work-tree={} {}'.format(config_path, user_path, git_cmd))

def prompt(string):
    return raw_input(string)

def read_next_arg():
    global current_arg_index
    if are_all_args_read():
        current_arg_index += 1
        return sys.argv[current_arg_index]
    else:
        return ''

def read_rest_args():
    return ' '.join(sys.argv[current_arg_index+1:])

def register(name, fn, dict):
    dict[name] = fn

def register_command(name, fn):
    register(name, fn, commands)

def only_verbose_print(string):
    if verbose:
        print(string)


# misc funtions

def help():
    print(commands.keys())

def init():
    if path.exists(path.expanduser(config_path)):
        only_verbose_print('Already configured')
    else:
        git_bare('init --bare {}'.format(config_path))
        git('config --local status.showUntrackedFiles no')
        only_verbose_print('Initialized config directory')

# Todo: replace rsync and rm by python functionality
def load(repoURL):
    git('clone --separate-git-dir=$HOME/.dotfiles {} ~/tmpdotfiles'.format(repoURL))
    execute('rsync --recursive --verbose --exclude ".git" ~/tmpdotfiles ~')
    execute('rm -r ~/tmpdotfiles')


register_command('add', lambda: git('add'))
register_command('commit', lambda: git('commit -a -m ' + prompt('Please enter a commit message:\n')))
register_command('git', lambda: git(read_rest_args()))
register_command('help', help)
register_command('init', init)
register_command('load', lambda: load(prompt('Please enter your dotfiles repo name: ')))
register_command('push', lambda: git('push'))
register_command('status', lambda: git('status'))
register_command('version', lambda: print(version))

# Todo: handle ctrl-c
# execute commands
if are_all_args_read():
    if sys.argv[1] in commands:
        commands[read_next_arg()]()
    else:
        print('Not a valid command')
else:
    help()
