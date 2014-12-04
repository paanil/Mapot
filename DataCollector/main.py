import data_collector
import sys
import os.path

if __name__ == '__main__':
    collect_all = True
    if len(sys.argv) > 1:
        opt = sys.argv[1]
        if opt == "--only-new-queries" or opt == "-n":
            collect_all = False
    data_collector.init()
    raise SystemExit(data_collector.main(collect_all))
