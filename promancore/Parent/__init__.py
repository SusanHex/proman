from cgitb import text
from distutils import command
from queue import Queue
import queue
from sys import excepthook
from threading import Thread
from subprocess import Popen, PIPE
from typing import TextIO, IO
from cmd import Cmd
from shlex import split


class Parent(object):
    """[summary]
        A class to control the stdout, stderr, and stdin of a child process.
    """

    def __init__(self, command: str, executable=None, max_queue_size=0, dedicated_stderr_queue=False, run=False) -> None:

        # parse the command string set process init data
        self._args = split(command))
        self._executable=executable
        # create child process instance
        self._process=Popen(self._args, executable = executable,
                            stdout = PIPE, stdin = PIPE, stderr = PIPE, text = True)

        # init process queues
        self._stdout_queue=Queue(maxsize = max_queue_size)
        self._stdin_queue=Queue(maxsize = max_queue_size)
        self._stderr_queue=Queue(maxsize = max_queue_size)


        # create thread instances
        self._stdout_worker=Thread(
            target = self._reader, args = (
                self._process,
                self._stdout_queue,
                self._process.stdout,
                ))
        self._stdin_worker=Thread(
            target = self._writer, args = (
                self._process,
                self._stdin_queue,
                self._process.stdin,
            ))
        if self._stderr_queue:
            self._stderr_worker=Thread(
                target = self._reader, args = (
                    self._process,
                    self._stderr_queue,
                    self._process.stderr,
                ))

        # if run, call the run func
        if run:
            self.run()



    def read(self, wait = False) -> str:
        try:
            return self._stdout_queue.get(wait)
        except queue.Empty:
            return ''

    def readlines(self, limit = 0) -> list:
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

    def write(line: str, end = '\n') -> None:


    @ staticmethod
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

    @ staticmethod
    def _writer(child_process: Popen, message_queue: Queue, stream: TextIO):
        while child_process.poll() is None:
            send_data=message_queue.get()
            try:
                stream.write(send_data)
                message_queue.task_done()
            except OSError as e:
                print(f"Writer Thread has encountered an error: {e}")
                break


class ParentCLI(Cmd):
    def __init__(self, completekey: str = ..., stdin: IO[str] = ..., stdout: IO[str] = ...) -> None:
        super().__init__(completekey, stdin, stdout)
