from . import Parent
from queue import Queue
from typing import IO
from sys import stdout, stderr

def outputConsumer(parent_instance: Parent):
    while parent_instance.running:
        try:
            line = parent_instance.read()
            if line:
                stdout.write(line)
            line = parent_instance.read(error=True)
            if line:
                stderr.write(line)
        except OSError:
            print("Error in output consumer")
            break