import xml.etree.ElementTree
# from lxml import etree as ElementTree
import os
import re
import glob
import sys
import time
import itertools

# find the parent of a child
def find_parent(root, child):
    for parent in root.iter():
        if child in parent:
            return parent
    return None

input_file = '../resources/ManyClocks.x3d'
print(f"Input file: {input_file}")

X3D = xml.etree.ElementTree.parse(input_file)
root = X3D.getroot()
scene = root.find("Scene")
displacers = scene.findall(".//HAnimDisplacer")
for displacer in displacers:
    routes = scene.findall(".//ROUTE[@toField='weight']")
    for route in routes:
        route.set("toField", "set_fraction")
    Animation_DEF = displacer.get('DEF')
    print(Animation_DEF)
    ci = xml.etree.ElementTree.Element('CoordinateInterpolator')
    ci.text = ""
    ci.tail = "\n"
    ci.set("DEF", Animation_DEF)

    short_Coordinate_DEF = re.sub(r"(.*)_MorphInterpolator_(.*)", r"\1_COORD", Animation_DEF)
    if not short_Coordinate_DEF.startswith("__") and not short_Coordinate_DEF.startswith("Hair_") and not short_Coordinate_DEF.startswith("Left_upper_vermillion_lip001_COORD"):
        route = xml.etree.ElementTree.Element('ROUTE')
        route.text = ""
        route.tail = "\n"
        route.set("fromNode", Animation_DEF)
        route.set("fromField", "value_changed")
        route.set("toNode", short_Coordinate_DEF)
        route.set("toField", "point")
        scene.append(route)

    # add CoordinateInterpolator after HAnimDisplacer
    par = find_parent(scene, displacer)
    index = list(par).index(displacer)
    par.insert(index + 1, ci)


    coordIndex = displacer.get('coordIndex')
    if coordIndex is None:
        coordIndex = []
    else:
        coordIndex = coordIndex.split()

    displacements = displacer.get('displacements')
    if displacements is not None:
        displacements = displacements.replace(",", "")
        displacements = displacements.split()
    else:
        displacements = []

    if Animation_DEF is not None:
        Coordinate_DEF = re.sub(r"(.*)_MorphInterpolator_(.*)", r"\1_COORD_\2", Animation_DEF)

        coordinates = scene.findall(".//Coordinate[@USE='"+Coordinate_DEF+"']")
        for coordinate in coordinates:
            par = find_parent(root, coordinate);
            par.remove(coordinate)

        coordinates = scene.findall(".//Coordinate[@DEF='"+Coordinate_DEF+"']")
        for coordinate in coordinates:
            short_Coordinate_DEF = re.sub(r"(.*)_MorphInterpolator_(.*)", r"\1_COORD", Animation_DEF)
            coordinate.set('DEF', short_Coordinate_DEF)
            #print("Found", coordinate.get('DEF'))
            point = coordinate.get("point")
            if point is not None:
                point = point.replace(",", "")
                point = point.split()
            else:
                print("NO POINT")
                point = []
            ci.set("key", "0")
            ci.set("keyValue", " ".join(point))
            lastpoint = []
            for ch, first in enumerate(point):
                appended = False
                if ch % 3 == 0:
                    for c, ind in enumerate(coordIndex):
                        if int(ind) == int(ch//3) and not appended:
                            #print(ind, ch//3, ch, c*3)
                            for i in range(3):
                                #print(float(point[ch+i]), "+", float(displacements[c*3+i]), "=", str(float(point[ch+i]) + float(displacements[c*3+i])))
                                lastpoint.append(str(float(point[ch+i]) + float(displacements[c*3+i])))
                                # print("append1", str(float(point[ch+i]) + float(displacements[c*3+i])))
                            appended = True
                    if not appended:
                        for i in range(3):
                            lastpoint.append(str(float(point[ch+i])))
                            # print("append2", str(float(point[ch+i])))
            #print("coordIndex", coordIndex)
            #print("displacements", displacements)
            #print("first point", point)
            #print("last point", lastpoint)
            ci.set("key", "0 1")
            ci.set("keyValue", " ".join(point)+" "+(" ".join(lastpoint)))
            # break


    # remove HAnimDisplacer
    #if len(coordIndex) <= 0 and len(displacements) <= 0:
    par = find_parent(scene, displacer)
    par.remove(displacer)


def createdCDATA(element):
    child = element[-1]
    if child.tail:
        child.tail = '<![CDATA['+child.tail+']]>'

scripts = scene.findall(".//Script")
for script in scripts:
    createdCDATA(script)

world_info = scene.findall(".//WorldInfo")
for wi in world_info:
    wi.set('title', "BackToCoordinate.x3d")

header = '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE X3D PUBLIC "ISO//Web3D//DTD X3D 4.0//EN" "https://www.web3d.org/specifications/x3d-4.0.dtd">'
xmlstr = xml.etree.ElementTree.tostring(root, encoding='unicode')
xmlstr = xmlstr.replace("&lt;![CDATA[", "<![CDATA[")
xmlstr = xmlstr.replace("]]&gt;", "]]>")

wi_str = '''
  </Scene>
</X3D>
'''

xmlString = f"{header}{xmlstr[:-16]}{wi_str}"
file_output = os.path.join("../resources/",os.path.basename("BackToCoordinate.x3d"))
with open(file_output, "w") as output_file:
    output_file.write(xmlString)
