from multiprocessing import Process, Manager, Pool
from multiprocessing.pool import AsyncResult


###############################
## Standard Recursive Mergesort
###############################

def merge(ls1, ls2):
    if len(ls1) == 0:
        return ls2
    elif len(ls2) == 0:
        return ls1
    elif ls1[0] < ls2[0]:
        ls = merge(ls1[1:], ls2)
        return [ls1[0]] + ls
    else:
        ls = merge(ls1, ls2[1:])
        return [ls2[0]] + ls
        
def mergesort(ls):
    if len(ls) <= 1:
        return ls
    else:
        mid = int((len(ls)) / 2)
        left = mergesort(ls[:mid])
        right = mergesort(ls[mid:])
        return merge(left, right)


###############################
## In Place Serial Mergesort
###############################

def merge_in_place(ls : list[int], start : int, mid, end : int):
    # if ls1 is totally merged
    if start == mid:
        return
    # if ls2 is totally merged
    elif mid == end:
        return
    ## if element at front is already in the right place
    elif ls[start] < ls[mid]:
        start += 1
    ## otherwise we move value at mid to front and shift everything down
    else:
        tmp = ls[start]
        put = ls[mid]
        for i in range(start, mid+1):
            tmp = ls[i]
            ls[i] = put
            put = tmp
        start += 1
        mid += 1
    merge_in_place(ls, start, mid, end)

def _mergesort(ls : list[int], start : int, end : int):
    if end <= start + 1:
        return
    else:
        mid = int((start + end) / 2)
        _mergesort(ls, start, mid)
        _mergesort(ls, mid, end)
        merge_in_place(ls, start, mid, end)

def mergesort_in_place(ls : list[int]):
    return _mergesort(ls, 0, len(ls))


#########################################
## Parallel In place Mergesort V 1 (SLOW)
#########################################

def _mergesort_pl(ls, start : int, end : int):
    if end <= start + 1:
        return
    else:
        mid = int((start + end) / 2)
        p_left = Process(target=_mergesort_pl, args=(ls, start, mid))
        p_right = Process(target=_mergesort_pl, args=(ls, mid, end))
        p_left.start()
        p_left.join()
        p_right.start()
        p_right.join()
        merge_in_place(ls, start, mid, end)

def mergesort_pl(ls : list[int]):
    m = Manager()
    shared_list = m.list(ls)
    _mergesort_pl(shared_list, 0, len(ls))
    for i in range(len(ls)):
        ls[i] = shared_list[i]




##############################
## Parallel Normal Mergesort
##############################
def _mergesort_rec_pl(ls, start : int, end : int):
    if end <= start + 1:
        return
    else:
        mid = int((start + end) / 2)
        procs = [[start, mid, end]]
        with Pool() as pool:
            while len(procs) > 0:
                
                start, mid, end = procs[0]
                procs = procs[1:]
                
                pool.apply_async(merge_in_place(ls, start, mid, end))

                procs = [[start, mid, end]] + procs
                


def mergesort_rec_pl(ls : list[int]):

    q = [[v] for v in ls]
    running : list[AsyncResult] = []
    with Pool() as p:
        while (len(q) > 1) or (len(running) > 0):
            if len(q) >= 2:
                l1 = q[0]
                l2 = q[1]
                q = q[2:]
                proc = p.apply_async(merge, (l1, l2))
                running.append(proc)
            done = []
            for i in range(len(running)):
                proc = running[i]
                if proc.ready():
                    sublist = proc.get()
                    q.append(sublist)
                    done.append(i)
            done.sort()
            factor = 0
            for i in done:
                del running[i-factor]
                factor += 1
        return q[0]



import time
import random
if __name__ == "__main__":

    ls = [int(random.random() * 100) for i in range(500)]
    ls1 = ls.copy()
    ls2 = ls.copy()
    ls3 = ls.copy()

    # print(f"Original List: {ls}")
    t1 = time.process_time()
    rec = mergesort(ls)
    t2 = time.process_time()
    print(f"Normal Recursive: {t2 - t1} {rec}")

    t1 = time.process_time()
    mergesort_in_place(ls1)
    t2 = time.process_time()
    print(f"In Place: {t2 - t1} {ls1}")

    
    t1 = time.process_time()
    mergesort_pl(ls2)
    t2 = time.process_time()
    print(f"Parallel In Place: {t2 - t1} {ls2}")

    #
    #
    t1 = time.process_time()
    ls3 = mergesort_rec_pl(ls3)
    t2 = time.process_time()
    print(f"Parallel Rec took {t2 - t1}: {ls3}")
    