from . import Parent
from queue import Queue
from typing import IO
from sys import stdout, stderr

def outputConsumer(parent_instance: Parent):
    while parent_instance.running or parent_instance.isOutput():
        try:
            line = parent_instance.read()
            if line:
                print(line, end='')
            line = parent_instance.read(error=True)
            if line:
                stderr.write(line)
        except OSError as e:
            print(f"Error in output consumer: {e}, {parent_instance.status()}")
            break
    print(parent_instance.status())