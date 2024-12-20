import xml.etree.ElementTree
# from lxml import etree as ElementTree
import os
import re
import glob
import sys
import time

# find the parent of a child
def find_parent(root, child):
    for parent in root.iter():
        if child in parent:
            return parent
    return None

input_file = '../resources/MultiFacialAnimationMenu.x3d'
print(f"Input file: {input_file}")

X3D = xml.etree.ElementTree.parse(input_file)
root = X3D.getroot()
scene = root.find("Scene")
displacers = scene.findall(".//HAnimDisplacer")
for displacer in displacers:
    if not displacer.get('coordIndex') or not displacer.get('displacements'):
        routes = scene.findall(".//ROUTE[@fromNode='"+displacer.get('DEF')+"']")
        for route in routes:
            par = find_parent(scene, route)
            par.remove(route)
        routes = scene.findall(".//ROUTE[@toNode='"+displacer.get('DEF')+"']")
        for route in routes:
            par = find_parent(scene, route)
            par.remove(route)
        par = find_parent(scene, displacer)
        par.remove(displacer)
        print(f"Removed Displacer")

def createdCDATA(element):
    child = element[-2]
    if child.tail:
        child.tail = '<![CDATA['+child.tail+']]>'

scripts = scene.findall(".//Script")
for script in scripts:
    createdCDATA(script)

world_info = scene.findall(".//WorldInfo")
for wi in world_info:
    wi.set('title', "CleanedMultiFacialAnimationMenu.x3d")

header = '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE X3D PUBLIC "ISO//Web3D//DTD X3D 4.0//EN" "https://www.web3d.org/specifications/x3d-4.0.dtd">'
xmlstr = xml.etree.ElementTree.tostring(root, encoding='unicode')
xmlstr = xmlstr.replace("&lt;![CDATA[", "<![CDATA[")
xmlstr = xmlstr.replace("]]&gt;", "]]>")

wi_str = '''
  </Scene>
</X3D>
'''

xmlString = f"{header}{xmlstr[:-16]}{wi_str}"
file_output = os.path.join("../resources/",os.path.basename("CleanedMultiFacialAnimationMenu.x3d"))
with open(file_output, "w") as output_file:
    output_file.write(xmlString)
