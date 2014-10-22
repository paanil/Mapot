import shapefile
import pyproj
#import svgwrite
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
    return  (scale * x, scale * y) #((x+17005833)*scale, (y+8625154)*scale)

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
        polygons = [[project(x) for x in xs] for xs in polygons]
        attributes = [sr.record[int(i)] for i in attribute_indices]
        countries.append((attributes,polygons))
    return countries

def get_shapes_of_countries(id_index: int, shapefile_path: str):
    """ """
    countries = get_shapes_and_attributes_of_countries([id_index], shapefile_path)
    return  [(c[0][0],c[1]) for c in countries]
    
if len(sys.argv) < 2:
    print("Give .shp file as argument")
else:
    data = get_shapes_of_countries(19, sys.argv[1])
    print(json.dumps(data))

#with open("C:\\MyTemp\\data.json", "w") as f:
#    f.write(json.dumps(data))
    
# json_output = ""
# for c in countries:
#     json_output += json.dumps({'id': str(c[0][2]), 'name': str(c[0][1]), 'shapes': c[1]})


# dwg = svgwrite.Drawing(filename="test.svg")
# for c in countries:
#     shapes = dwg.add(dwg.g(id=c[0][2]))
#     for polygon in c[1]:
#         shapes.add(dwg.polygon(polygon, fill="lime", stroke="black", stroke_width="1"))
# dwg.save()
    
