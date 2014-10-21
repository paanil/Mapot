import shapefile
import pyproj
import svgwrite
import json

#shape_path = "/home/makakova/mapdata/naturalEarthCountries/ne_10m_admin_0_countries.shp"
#shape_path = "/home/makakova/mapdata/naturalEarthCountries/ne_50m_admin_0_countries.shp"
shape_path = "/home/makakova/mapdata/naturalEarthCountries/ne_110m_admin_0_countries.shp"
#shape_path = "/home/makakova/mapdata/naturalEarthCountriesLakes/ne_110m_admin_0_countries_lakes.shp"
#shape_path = "/home/makakova/mapdata/land/ne_110m_land.shp"
selected_attributes = (17,18,19,20)
scale = 0.00003

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

sf = shapefile.Reader(shape_path)
shp_records = sf.shapeRecords()

countries = []
for sr in shp_records:
    polygons = separate_polygons(sr.shape)
    polygons = [[project(x) for x in xs] for xs in polygons]
    attributes = tuple([sr.record[i] for i in selected_attributes])
    countries.append((attributes,polygons))

json_output = ""
for c in countries:
    json_output += json.dumps({'id': str(c[0][2]), 'name': str(c[0][1]), 'shapes': c[1]})

#print(json_output)

dwg = svgwrite.Drawing(filename="test.svg")
for c in countries:
    shapes = dwg.add(dwg.g(id=c[0][2]))
    for polygon in c[1]:
        shapes.add(dwg.polygon(polygon, fill="lime", stroke="black", stroke_width="1"))
dwg.save()
    
