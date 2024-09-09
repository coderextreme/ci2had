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

X3D = xml.etree.ElementTree.parse("../resources/Jaw_Drop.x3d")
root = X3D.getroot()
head = root.find('head')
scene = root.find('Scene')
component = xml.etree.ElementTree.Element('component')
component.set("name", "HAnim")
component.set("level", "3")
head.insert(0, component)
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
            parent.insert(index, new_node)
            parent.remove(cis)

            # replace set_fraction wiht weight
            routes = root.findall(".//ROUTE[@toField='set_fraction'][@toNode='"+DEF+"']")
            for route in routes:
                route.set("toField", "weight")

            # replace value_changed wiht weight
            routes = root.findall(".//ROUTE[@fromField='value_changed'][@fromNode='"+DEF+"']")
            for route in routes:
                route.set("fromField", "weight")
                # set to coordIndex of the new HAnimDisplacer node.
                COORDDEF = route.get("toNode");
                coords = root.findall(".//*[@DEF='"+COORDDEF+"']")
                for coord in coords:
                    parent = find_parent(root, coord)
                    if parent is not None:
                        coordIndex = parent.get("coordIndex")
                        new_node.set("coordIndex", coordIndex)

X3D.write("../resources/Jaw_Drop_Output.x3d")
