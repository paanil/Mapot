
if __name__ == '__main__':
    import config
    config.read("config.json")
    import data_collector
    raise SystemExit(data_collector.main())
