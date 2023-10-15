from multiprocessing import Process, Manager, Pool
import time
def slow(i):
    time.sleep(1)
    return i + 1

def map_basic(f, arr):
    for i in range(len(arr)):
        arr[i] = f(arr[i])


def map_parallel(f, arr):
    with Pool() as pool:
        ls = pool.map(f, arr)
    ls = list(ls)
    for i in range(len(arr)):
        arr[i] = ls[i]

if __name__ == "__main__":
    ls = [i for i in range(20)]
    ls2 = ls.copy()

    print("Running Slow")
    map_basic(slow, ls)
    print(ls)
    print("Running fast")
    map_parallel(slow, ls2)
    print(ls2)