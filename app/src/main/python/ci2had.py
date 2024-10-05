import xml.etree.ElementTree

def find_parent(root, child):
    for parent in root.iter():
        if child in parent:
            return parent
    return None

def get_node_index(parent, cis):
    for index, child in enumerate(parent):
        if child == cis:
            return index
    return None

def split_every_third(lst):
    result = []
    for i in range(0, len(lst), 3):
        result.append(lst[i:i + 3])
    return result

X3D = xml.etree.ElementTree.parse("../resources/Jaw_Drop.x3d")
root = X3D.getroot()
head = root.find('head')
scene = root.find('Scene')
component = xml.etree.ElementTree.Element('component')
component.set("name", "HAnim")
component.set("level", "3")
head.insert(0, component)

humanoid = xml.etree.ElementTree.Element('HAnimHumanoid')
humanoid.text = "\n"
humanoid.tail = "\n"
scene.insert(0, humanoid)
humanoid_root = xml.etree.ElementTree.Element('HAnimJoint')
humanoid_root.set("DEF", "root")
humanoid_root.set("containerField", "skeleton")
humanoid_root.text = "\n"
humanoid_root.tail = "\n"
humanoid.append(humanoid_root)
humanoid_root_use = xml.etree.ElementTree.Element('HAnimJoint')
humanoid_root_use.set("USE", "root")
humanoid_root_use.set("containerField", "joints")
humanoid_root_use.text = "\n"
humanoid_root_use.tail = "\n"
humanoid.append(humanoid_root_use)
sacrum = xml.etree.ElementTree.Element('HAnimSegment')
sacrum.text = "\n"
sacrum.tail = "\n"
humanoid_root.insert(0, sacrum)

skullbase = xml.etree.ElementTree.Element('HAnimJoint')
skullbase.set("DEF", "skullbase")
skullbase.set("containerField", "children")
skullbase.text = "\n"
skullbase.tail = "\n"
humanoid_root.append(skullbase)

skullbase_use = xml.etree.ElementTree.Element('HAnimJoint')
skullbase_use.set("USE", "skullbase")
skullbase_use.set("containerField", "joints")
skullbase_use.text = "\n"
skullbase_use.tail = "\n"
humanoid.append(skullbase_use)

for cis in root.iter('CoordinateInterpolator'):
    DEF = cis.get("DEF")
    print(DEF)
    keys = cis.get("key").split()
    keyValues = cis.get("keyValue").split()

    numKeys = len(keys)
    valuesPerKey = int(len(keyValues)/numKeys)
    print(keys)
    print(keyValues)
    key = 0
    base = keyValues[valuesPerKey*key:valuesPerKey*(key+1)]
    key = numKeys - 1
    extension = keyValues[valuesPerKey*key:valuesPerKey*(key+1)]
    print(base)
    print(extension)
    new_node = xml.etree.ElementTree.Element('HAnimDisplacer')
    new_node.text = "\n"
    new_node.tail = "\n"
    displacements = []
    for i in range(len(base)):
        displacements.append(str(float(extension[i]) - float(base[i])))
    print(displacements)
    parent = find_parent(root, cis)
    new_node.set("displacements", " ".join(displacements))
    new_node.set("DEF", DEF)
    if parent is not None:
        index = get_node_index(parent, cis)
        # replace the coordinate interpolator
        if index is not None:
            # parent.insert(index, new_node)
            sacrum.append(new_node)
            parent.remove(cis)

            # replace set_fraction wiht weight
            routes = root.findall(".//ROUTE[@toField='set_fraction'][@toNode='"+DEF+"']")
            for route in routes:
                route.set("toField", "weight")

            # replace value_changed wiht weight
            routes = root.findall(".//ROUTE[@fromField='value_changed'][@fromNode='"+DEF+"']")
            for route in routes:
                # route.set("fromField", "weight")
                # set to coordIndex of the new HAnimDisplacer node.
                COORDDEF = route.get("toNode");
                coords = root.findall(".//*[@DEF='"+COORDDEF+"']")
                for coord in coords:
                    ifs = find_parent(root, coord)
                    if ifs is not None:
                        coordinate_node = ifs.find("Coordinate")
                        points = coordinate_node.get("point").split()
                        pointsMatrix = split_every_third(points)
                        baseMatrix = split_every_third(base)
                        coordIndex = []
                        for i, point in enumerate(baseMatrix):
                            if point in pointsMatrix:
                                coordIndex.append(str(i))
                        new_node.set("coordIndex", " ".join(coordIndex))
                par = find_parent(root, route)
                par.remove(route)

for element in list(scene):
    if not element.tag.startswith("HAnim") and element.tag != "ROUTE":
        sacrum.append(element)
        scene.remove(element)
    elif element.tag == 'ROUTE':
        scene.remove(element)
        scene.append(element)

X3D.write("../resources/Jaw_Drop_Output.x3d")
