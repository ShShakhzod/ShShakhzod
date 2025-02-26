import multiprocessing
import time

def cpu_task(n):
    print(f"{n}-vazifa boshlandi...")
    time.sleep(3)  # Katta hisob-kitoblar o‘rniga shunchaki kutish
    print(f"{n}-vazifa tugadi!")

if __name__ == "__main__":
    p1 = multiprocessing.Process(target=cpu_task, args=(1,))
    p2 = multiprocessing.Process(target=cpu_task, args=(2,))

    p1.start()
    p2.start()

    p1.join()
    p2.join()

    print("Barcha jarayonlar tugadi!")
