import os
from multiprocessing import Process


def start_worker(worker_id):
    os.system(f"python3 main.py {worker_id}")


if __name__ == "__main__":
    num_workers = 6
    print(f"Launching {num_workers} DataFlux workers...\n")

    processes = []
    for i in range(num_workers):
        p = Process(target=start_worker, args=(i,))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()
