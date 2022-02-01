from asyncio.subprocess import PIPE
from queue import Queue
import queue
import stat
from threading import Thread
from subprocess import Popen, PIPE
from typing import TextIO

class Parent(object):
    """[summary]
        A class to control the stdout, stderr, and stdin of a child process.
    """
    
    def __init__(self, max_queue_size=0, dedicated_stderr_queue=False, run=False) -> None:

        # init process queues
        self._stdout_queue = Queue(maxsize=max_queue_size)
        self._stdin_queue = Queue(maxsize=max_queue_size)
        if dedicated_stderr_queue:
            self._stderr_queue = Queue(maxsize=max_queue_size)
        else:
            self._stderr_queue = self._stdout_queue
        
        # create thread instances
        self._stdout_worker = Thread()
        self._stdin_worker = Thread()
        
        # if run, call the run func
        if run:
            self.run()
    
        
    def run(self) -> None:
        pass
        
    @staticmethod
    def _reader(child_process: Popen, message_queue: Queue, stream: TextIO) -> None:
        while child_process.poll() is None:
            process_data = stream.readline()
            try:
                message_queue.put(process_data)
            except queue.Full:
                message_queue.get()
                message_queue.put(message_queue)
    
    @staticmethod
    def _writer(child_process: Popen, message_queue: Queue, stream: TextIO):
        while child_process.poll() is None:
            send_data = message_queue.get()
            stream.write(send_data)
            
                
                
        
            
        
        