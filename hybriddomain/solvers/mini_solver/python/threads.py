import queue
import threading
import multiprocessing as mp
import time


class Kernel(threading.Thread):
    def __init__(self, work_queue, number):
        threading.Thread.__init__(self)
        self.work_queue = work_queue
        
        self.number = number

    def run(self):
        while True:
            try:
                entry = self.work_queue.get()
                if entry is None:
                    break
                self.do_work(entry)
        
            finally:
                self.work_queue.task_done()
                
    def do_work(self, entry):
        '''What will be done for each thread'''
        print("thread %s " % (str(self.number)), "entry:")
        print(entry)


if __name__ == "__main__":

    print("count of physical cpu:")
    print(mp.cpu_count())

    num_worker_threads = 2

    q = queue.Queue()

    threads = []

    for i in range(num_worker_threads):
        # t = threading.Thread(target=worker)
        t = Kernel(q, i)
        t.start()
        threads.append(t)

    # part 1:
    print("beginning to add work")
    time_start = time.time()
    for item in [[1, 2, 3], [4, 5, 6]]:
        q.put(item)
    print("end of add work")
    # block until all tasks are done
    q.join()
    print("unblock")
    print("running time:")
    print(time.time()-time_start)

    # part 2:
    print("beginning to add work")
    time_start = time.time()
    for item in [[1, 2, 3], [4, 5, 6]]:
        q.put(item)
    print("end of add work")
    # block until all tasks are done
    q.join()
    print("unblock")
    print("running time:")
    print(time.time()-time_start)
    
    # stop workers
    for i in range(num_worker_threads):
        q.put(None)
    for t in threads:
        t.join()
    
