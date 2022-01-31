from queue import Queue
import stat
from threading import Thread
from subprocess import Popen

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
        
        
        # create thread
        self._stdout_worker = Thread()
        
        # if run, call the run func
        if run:
            self.run()
    
        
    def run(self) -> None:
        pass
        
    @staticmethod
    def _reader(child_process: Popen, message_queue: Queue, ):
        pass
        
            
        
        