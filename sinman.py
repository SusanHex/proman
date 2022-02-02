from promancore.Parent import Parent, SingleParentCLI
from promancore.Parent.functions import outputConsumer
from argparse import ArgumentParser
from threading import Thread
import pathlib

def sinman():
    # Constants
    DESCRIPTION = 'script to intercept the output and inject output from a child process.'
    
    # parser and parser arguments
    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument('--config', '-C', default=None, type=pathlib.Path)
    parser.add_argument('--arg', '-a', default=None)
    parser.add_argument('--executable', '-e', default=None)
    parser.add_argument('--max-queue-len', default=0)
    args = parser.parse_args()
    print(args.__dict__)
    parent_instance = Parent(args.arg)
    parent_instance.run()
    # start consumer thread
    consumer_thread = Thread(target=outputConsumer, args=(parent_instance,))
    consumer_thread.start()
    SingleParentCLI(parent_instance).cmdloop()
    
if __name__ == '__main__':
    sinman()