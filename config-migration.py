#!/usr/bin/env python

from __future__ import print_function
from os import path, listdir
import shutil
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
def execute(cmdString, print_stdout = True):
    print(cmdString)
    child = subprocess.Popen(cmdString.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = child.communicate()
    if print_stdout:
        print(out)
    return child.returncode, out, err

def git_bare(git_cmd, print_stdout = True):
    # git command without any predefined parameters
    return execute('git ' + git_cmd, print_stdout)

def git(git_cmd, print_stdout = True):
    # git command for working on the dotfile repo
    return git_bare('--git-dir={} --work-tree={} {}'.format(config_path, user_path, git_cmd), print_stdout)

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

def join():
    pass

def load(repoURL):
    tmp_path = user_path + '/tmpdotfiles'
    git_bare('clone --separate-git-dir={} {} {}'.format(config_path, repoURL, tmp_path))
    for file in filter(lambda file: file != '.git', listdir('{}'.format(tmp_path))):
        shutil.move(tmp_path + '/' + file, user_path + '/' + file)
    shutil.rmtree(tmp_path)

# profile management

def if_git_else(cmd, if_fail):
    profile = read_next_arg()
    code, out, err = git(cmd. format(profile))
    if code != 0:
        print(if_fail.format(profile))

def change_profile_to():
    if_git_else('checkout {}', 'Could not change to profile: {}')

def current_profile():
    code, out, err = git('rev-parse --abbrev-ref HEAD', False)
    return out

def new_profile():
    if_git_else('branch {}', 'Could not create profile: {}. Maybe there already exists a profile with this name')

def remove_profile():
    if_git_else('branch -d {}', 'Unable to delete profile: {}')


register_command('add', lambda: git('add'))
register_command('commit', lambda: git('commit -a'))
register_command('current-profile', lambda: print(current_profile()))
register_command('git', lambda: git(read_rest_args()))
register_command('help', help)
register_command('init', init)
register_command('load', lambda: load(prompt('Please enter your dotfiles repo name: ')))
register_command('new-profile', new_profile)
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
