import shapefile
import pyproj
import svgwrite

#shape_path = "/home/makakova/mapdata/naturalEarthCountries/ne_10m_admin_0_countries.shp"
shape_path = "/home/makakova/mapdata/naturalEarthCountries/ne_50m_admin_0_countries.shp"
#shape_path = "/home/makakova/mapdata/naturalEarthCountries/ne_110m_admin_0_countries.shp"
#shape_path = "/home/makakova/mapdata/naturalEarthCountriesLakes/ne_110m_admin_0_countries_lakes.shp"
#shape_path = "/home/makakova/mapdata/land/ne_110m_land.shp"
selected_attributes = (17,18,19,20)
scale = 0.00003

# Source projection
sp = pyproj.Proj(init='epsg:4326')
# Target projection
tp = pyproj.Proj('+proj=robin +lon_0=0 +lat_0=0 +x_0=0 +y_0=0 +ellps=WGS84 +datum=WGS84 +units=m +no_defs')


sf = shapefile.Reader(shape_path)
shp_records = sf.shapeRecords()
# suomi = sf.shape(74)
# print(suomi.points)
countries = []
for sr in shp_records:
    shp = []
    for p in sr.shape.points:
        x,y = pyproj.transform(sp,tp,p[0],p[1])
        coordinates = ((x+17005833)*scale, (y+8625154)*scale)
        shp.append(coordinates) 
    attributes = tuple([sr.record[i] for i in selected_attributes])
    countries.append((attributes,shp))

dwg = svgwrite.Drawing(filename="test.svg")
for c in countries:
    shapes = dwg.add(dwg.g(id=c[0][2]))
    shapes.add(dwg.polygon(c[1], fill="lime", stroke="black", stroke_width="1"))
dwg.save()
