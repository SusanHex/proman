from queue import Queue
import queue
from threading import Thread
from subprocess import Popen, PIPE
from typing import TextIO, IO
from cmd import Cmd
from shlex import split


class Parent(object):
    """[summary]
        A class to control the stdout, stderr, and stdin of a child process.
    """

    def __init__(self, command: str, executable=None, max_queue_size=0, run=False) -> None:

        # parse the command string set process init data
        self._args = split(command)
        self._executable=executable
        # create child process instance
        self._process=None

        # init process queues
        self._stdout_queue=Queue(maxsize = max_queue_size)
        self._stdin_queue=Queue(maxsize = max_queue_size)
        self._stderr_queue=Queue(maxsize = max_queue_size)


        # if run, call the run func
        if run:
            self.run()

    def run(self):
        # create child process instance
        self._process=Popen(self._args, executable = self._executable,
                            stdout = PIPE, stdin = PIPE, stderr = PIPE, text = True)

        # create thread instances
        self._stdout_worker=Thread(
            target = self._reader, daemon=True, args = (
                self._process,
                self._stdout_queue,
                self._process.stdout,
                ))
        self._stdin_worker=Thread(
            target = self._writer, daemon=True, args = (
                self._process,
                self._stdin_queue,
                self._process.stdin,
            ))
        if self._stderr_queue:
            self._stderr_worker=Thread(
                target = self._reader, daemon=True, args = (
                    self._process,
                    self._stderr_queue,
                    self._process.stderr,
                ))
        
        # start threads
        self._stdout_worker.start()
        self._stderr_worker.start()
        self._stdin_worker.start()
    
    def close(self) -> bool:
        try:
            self._checkRunning()
            self._process.terminate()
        except (ValueError, OSError):
            self._process.kill()
        finally:
            self._stderr_worker.join()
            self._stdout_worker.join()
            self._stdin_worker.join()
        return True
    
    def status(self) -> dict:
        return {
            'Process': 'NOT RAN' if self._process is None else self._process.poll(),
            'Output Worker': self._stdout_worker.is_alive(),
            'Error Worker': self._stderr_worker.is_alive(),
            'Input Worker': self._stdin_worker.is_alive(),
            'Output Queue': self._stdout_queue.qsize(),
            'Error Queue': self._stderr_queue.qsize(),
            'Input Queue': self._stdin_queue.qsize()
                }
        


    def read(self, wait = False, error=False) -> str:
        self._checkRunning()
        try:
            if error:
                return self._stderr_queue.get(wait)
            else:
                return self._stdout_queue.get(wait)
        except queue.Empty:
            return ''

    def readlines(self, limit=0) -> list:
        self._checkRunning()
        lines=[]
        if limit > 0:
            for i in range(limit):
                try:
                    lines.append(self._stdout_queue.get_nowait())
                except queue.Empty:
                    return lines
            return lines
        else:
            while True:
                try:
                    lines.append(self._stdout_queue.get_nowait())
                except queue.Empty:
                    return lines

    def write(self, line: str, end = '\n') -> None:
        self._checkRunning()
        self._stdin_queue.put(line + end)
    

    @property
    def running(self):
        return False if self._process is None or self._process.poll() is not None else True
        
    def _checkRunning(self) -> None:
        if self._process is None:
            raise ValueError('Child process has not been ran/inited')
        elif self._process.poll() is None:
            raise OSError('Action attempted on a closed childprocess')
    



    @staticmethod
    def _reader(child_process: Popen, message_queue: Queue, stream: TextIO) -> None:
        while child_process.poll() is None:
            try:
                process_data=stream.readline()
            except OSError as e:
                print(f"Writer Thread has encountered an error: {e}")
                break
            try:
                message_queue.put(process_data)
            except queue.Full:
                message_queue.get()
                message_queue.put(message_queue)

    @staticmethod
    def _writer(child_process: Popen, message_queue: Queue, stream: TextIO):
        while child_process.poll() is None:
            send_data=message_queue.get()
            try:
                stream.write(send_data)
                message_queue.task_done()
            except OSError as e:
                print(f"Writer Thread has encountered an error: {e}")
                break


class SingleParentCLI(Cmd):
    def __init__(self, completekey: str = ..., stdin: IO[str] = ..., stdout: IO[str] = ...) -> None:
        super().__init__(completekey, stdin, stdout)
