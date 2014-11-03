import data_collector
import sys
import os.path

if __name__ == '__main__':
    path = os.path.abspath("queries")
    if len(sys.argv) > 1:
        path = argv[1]
    data_collector.init()
    raise SystemExit(data_collector.main(path))
