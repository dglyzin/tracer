import time
import sys


if __name__ == '__main__':
    if '-s' in sys.argv:
        try:
            ind = sys.argv.index('-s')
            n = sys.argv[ind+1]

            for i in range(int(n)):
                print(i)
                #sys.stdout.write(str(i))

                # for interactive out:
                sys.stdout.flush()
                time.sleep(1)
        except:
            print("wrong argument: -s 10")
