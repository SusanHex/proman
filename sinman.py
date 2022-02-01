from promancore.Parent import Parent
from argparse import ArgumentParser
import pathlib

def sinman():
    # Constants
    DESCRIPTION = 'script to intercept the output and inject output from a child process.'
    
    # parser and parser arguments
    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument('--config', '-C', default=None, type=pathlib.Path)
    parser.add_argument('--arg', '-a', default=None)
    parser.add_argument('--executable', '-e', default=None)
    

if __name__ == '__main__':
    sinman()