import subprocess
import threading
import queue
import sys
import os
import fcntl
import time
import re


def test1():
    cmd = 'ping 8.8.8.8'.split()
    run_cmd_interact(cmd, _stderr=1)


def test():
    script_name = 'tests/test_solver.py'
    cmd = ['python3', script_name, '-s', str(10)]
    run_cmd_interact(cmd, _stderr=1)


def run_cmd_interact(cmd, o=None, re_pat=".*\d.*", _stderr=None):
    '''
    DESCRIPTION:
    Run cmd in separate thread and update it out interactively.

    INPUT:
    o - Progress instance with succ(val) function.
    re_pat - re pattern for parsing solver output
             (to proggres.value).
    '''

    # logger.debug("cmd = %s" % str(cmd))
    print(cmd)
    ON_POSIX = 'posix' in sys.builtin_module_names

    def set_non_blocking(fd):
        """
        Set the file description of the given file descriptor to non-blocking.
        """
        flags = fcntl.fcntl(fd, fcntl.F_GETFL)
        flags = flags | os.O_NONBLOCK
        fcntl.fcntl(fd, fcntl.F_SETFL, flags)

    def write_out_interactive(p, _queue, o=None, re_pat=None):
        '''
        Used in separate thread.
        Read each line of cmd ouput interactively.
        Update o (if given) or print itro terminal.

        p is subprocess.Popen
        _queue
        o - progress object with succ(val)
            to update whom.
        re_pat - re pattern for parsing solver output
             (to proggres.value).
    
        '''
        #while True:
        #    _queue.put(line)
        for line in iter(p.stdout.readline, b''):
            if len(line) != 0:
               
                s = line.decode('utf-8')

                # find progress data using re:
                if re_pat is None:
                    re_pat = ".*\d.*"
                res = re.search(re_pat, str(s))
                res_str = res.group()

                if o is not None:
                    o.succ(int(res_str))
                else:
                    print("thread t_1")
                    print("original line:")
                    print(str(line))
            
                    print("parsed line")
                    print(res_str)

        # remove progress after finishing:
        if o is not None:
            o.progress.close()
                
    def read_out_interactive(stdout, _queue):
        print("from therad t_2")
        try:
            print(_queue.get())
        except queue.Empty:
            print("no output yet")

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    #                     bufsize=1, close_fds=ON_POSIX)
    
    #set_non_blocking(p.stdout)
    q = queue.Queue()
    
    t_1 = threading.Thread(target=write_out_interactive,
                           args=(p, q, o, re_pat))
    '''
    t_2 = threading.Thread(target=read_out_interactive,
                           args=(p.stdout, q))
    '''
    t_1.daemon = True
    #t_2.daemon = True

    t_1.start()
    try:
        p.wait()
    except:
        print('except p.wait(3)')

    #t_2.start()
    # print(dir(p))
    #return(p)
    # out, err = p.communicate()
    
    '''

    out, err = p.communicate()
    
    if (err is not None and len(err) > 0
        or _stderr is None):
        raise(GccException(err))
    if _stderr is not None:
        print("out")
        print(out)
        print("err")
        print(err)
    '''
    # return(out)
    

class GccException(Exception):
    '''
    DESCRIPTION:
    For cathing error of gcc.
    For tests cases in tester.py.
    '''
    def __init__(self, err):
        self.err = err


if __name__ == '__main__':
    test()
