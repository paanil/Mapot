import json

def parse_id(line):
    i = line.index('id="') + 4
    j = line.index('"', i)
    return line[i:j]

def parse_points(line):
    i = line.index('points="') + 8
    j = line.index('"', i)
    s = line[i:j]
    points = []
    scale = 0.01
    for point in s.split(" "):
        co = point.split(",")
        x = float(co[0]) * scale
        y = float(co[1]) * scale
        points.append((x, y))
    return points

def parse_polygons(f):
    polygons = []
    for line in f:
        if line.startswith("</g>"):
            return polygons
        if line.startswith("<polygon"):
            polygons.append(parse_points(line))
    print("Error: No ending tag </g>")
    return polygons

def parse(f):
    map = {}
    for line in f:
        if line.startswith("<g"):
            id = parse_id(line)
            map[id] = parse_polygons(f)
    return map

def convert():
    map = None
    with open("test.svg", "r") as f:
        map = parse(f)
    with open("test.json", "w") as f:
        f.write(json.dumps(map, sort_keys=True))

convert()