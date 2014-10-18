import config

if __name__ == '__main__':
    config.read("config.json")
    import data_collector
    raise SystemExit(data_collector.main())
