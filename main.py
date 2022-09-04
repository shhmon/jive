import os
import sys
import subprocess
from collector import Collector

commands = {}

# Command register decorator
def command(name):
    def decorator(fnc):        
        global commands
        commands[name] = fnc
        return fnc
    return decorator

def git(args):
    os.chdir(f'{os.getcwd()}/.jive')
    subprocess.run(f'git {" ".join(args)}', shell=True)
    os.chdir('..')

@command('init')
def init(args):
    cwd = os.getcwd()
    os.mkdir(f'{cwd}/.jive')
    git(['init'])
    subprocess.run('echo "Backup\n.DS_Store\nIcon?" >> .jive/.gitignore', shell=True)
    git(['add .gitignore'])
    git(['commit -m "jive init"'])
    print(f'Initialized Jive in {cwd}')

@command('shove')
def push(args):
    cwd = os.getcwd()
    collector = Collector(cwd)
    collector.push(cwd + '/.jive')

@command('collect')
def push(args):
    cwd = os.getcwd()
    collector = Collector(cwd)
    collector.collect_project()

def main():
    global commands
    cmd = sys.argv[1]
    args = sys.argv[1:]
    cwd = os.getcwd()

    is_init = '.jive' in os.listdir(cwd)

    if is_init or cmd == 'init':
        if cmd in commands.keys():
            commands[cmd](args[1:])
        else:
            git(args)
    else:
        print('Not a jive project')
    

if __name__ == "__main__":
    main()