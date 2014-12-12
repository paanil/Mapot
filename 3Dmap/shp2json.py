
#   Copyright (C) 2014 Susanne Jauhiainen, Markku Kovanen, Ilari Paananen
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.


import shapefile
import pyproj
import json
import sys

scale = 0.0000003

# Source projection
sp = pyproj.Proj(init='epsg:4326')
# Target projection
tp = pyproj.Proj('+proj=robin +lon_0=0 +lat_0=0 +x_0=0 +y_0=0 +ellps=WGS84 +datum=WGS84 +units=m +no_defs')

def project(point: (int,int)) -> (int,int):
    """Projects a point from geograpic coordinates to screen coordinates"""
    x,y = point
    x,y = pyproj.transform(sp,tp,x,y)
    return  (scale * x, scale * y) 

def separate_polygons(shape) -> [[(int,int)]]:
    """Separates polygons from a shape-object"""
    points = shape.points
    parts = shape.parts
    parts.append(len(points)) # Includes the last part
    polygons = []
    for i,j in zip(parts, parts[1:]):
        if j == []:
            j = len(shape.Points)
        polygons.append(points[i:j])
    return polygons

def get_shapes_and_attributes_of_countries(attribute_indices: [int], shapefile_path: str) -> [([str],[(int,int)])]:
    """   """
    sf = shapefile.Reader(shapefile_path)
    shp_records = sf.shapeRecords()
    countries = []
    for sr in shp_records:
        polygons = separate_polygons(sr.shape)
        polygons = [[project(point) for point in polygon] for polygon in polygons]
        attributes = [sr.record[int(i)] for i in attribute_indices]
        countries.append((attributes,polygons))
    return countries

def get_shapes_of_countries(id_index: int, name_index: int, shapefile_path: str):
    """ """
    countries = get_shapes_and_attributes_of_countries([id_index, name_index], shapefile_path)
    return  [(c[0][0], convert_if_bytes(c[0][1]), c[1]) for c in countries if c[0][0] != "ATA"] #TODO: Do something smarter to leave Antarctice out

def convert_if_bytes(obj):
    if type(obj) == bytes:
        return obj.decode("cp1252")
    return obj


def list_fields(shapefile_path: str):
    sf = shapefile.Reader(shapefile_path)
    fields = []
    for field in sf.fields:
        fields.append(("index=" + str(sf.fields.index(field) - 1), field[0]))
    return fields
    
if len(sys.argv) < 2:
    print("Give .shp file as argument")

else:
    data = get_shapes_of_countries(44, 18, sys.argv[1])
    print(json.dumps(data))
