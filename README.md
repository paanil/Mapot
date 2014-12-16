UNdataMap
=========

UndataMap is a web application that visualizes statistical data on a 3D-map using color and height.

The data is retrieved from UNdata (http://data.un.org/), using UNdata API.

From the height/color box the user can choose the dataset to be visualized by height/color.

Parameters can be used to divide the data by population or area.

The view can be moved, zoomed and rotated using the mouse.

Libraries: Three.js, Flask, pyshp, pyproj.

![screenshot](https://raw.githubusercontent.com/wiki/paanil/UNdataMap/screenshot.png)


Building 3D map
---------------

To build the 3D map you need python 3, pyshp, pyproj and blender (version 2.72 is known to work) installed.
Installing pyproj on Windows can be difficult because of a bug in python distutils.
Run 3Dmap/build.py

```
Options:
  -h, --help            show this help message and exit
  -p PYTHON, --path-to-python=PYTHON
  -b BLENDER, --path-to-blender=BLENDER
```

These options are optional if you have python 3 as "python" and blender as "blender" in the path.

The output files world\_map.json and world\_map\_hd.json are created in ServerApplication/static/.

Data collector
-------------

Data collector retrieves the data with UNdata API.
The datasets to be retrieved are defined in Data/metadata.json file.
Corresponding queries created with [SDMX Browser](http://data.un.org/SdmxBrowser/start) are expected to be in DataCollector/queries/.

Run DataCollector/data_collector.py

```
Options:
  -h, --help            show this help message and exit
  -n, --only-new-queries
                        Collects only datasets not found in Data/ folder
```

The output JSON-files are created in Data/.

Server application
------------------

To start the server run ServerApplication/server_application.py.

The server needs to be restarted if datasets are modified.
