import xml.etree.ElementTree
# from lxml import etree as ElementTree
import os
import re
import glob
import sys

epsilon = sys.float_info.epsilon

def non_zero(num):
    if abs(float(num)) > epsilon:
        return True
    else:
        return False

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

def find_elements_by_prefix(root, prefix):
    matched_elements = []
    for elem in root.iter():
        def_value = elem.get("DEF")
        if def_value and re.match("("+prefix+"$|"+prefix+"[-_])", def_value):
            matched_elements.append(elem)
        def_value = elem.get("USE")
        if def_value and re.match("("+prefix+"$|"+prefix+"[-_])", def_value):
            matched_elements.append(elem)
    return matched_elements

def find_segments_by_prefix(root, prefix):
    matched_elements = []
    for elem in root.iter():
        def_value = elem.get("DEF")
        if def_value and elem.tag == 'HAnimSegment':
            def_value = def_value[6:]
            if prefix == def_value:
                #print(f"looking at {def_value} {prefix} {elem.tag}")
                matched_elements.append(elem)
    return matched_elements

def process_file(file_input):
    # print(f"Input file: {file_input}")
    X3D = xml.etree.ElementTree.parse(file_input)
    root = X3D.getroot()
    return root

def processMega(megaX3D):

    finalX3D = xml.etree.ElementTree.Element('X3D')
    finalX3D.text = "\n"
    finalX3D.tail = "\n"
    finalX3D.set("profile", "Immersive")
    finalX3D.set("version", "4.0")
    head = xml.etree.ElementTree.Element('head')
    head.text = "\n"
    head.tail = "\n"
    component = xml.etree.ElementTree.Element('component')
    component.set("name", "HAnim")
    component.set("level", "3")
    component.text = "\n"
    component.tail = "\n"
    head.insert(0, component)
    finalX3D.append(head)
    scene = xml.etree.ElementTree.Element('Scene')
    scene.text = "\n"
    scene.tail = "\n"
    finalX3D.append(scene)

    humanoid = xml.etree.ElementTree.Element('HAnimHumanoid')
    humanoid.text = "\n"
    humanoid.tail = "\n"
    humanoid.set('DEF', "hanim_humanoid")
    humanoid.set('name', "humanoid")
    scene.insert(0, humanoid)
    humanoid_root = xml.etree.ElementTree.Element('HAnimJoint')
    humanoid_root.set("DEF", "hanim_root")
    humanoid_root.set("name", "root")
    humanoid_root.set("containerField", "skeleton")
    humanoid_root.text = "\n"
    humanoid_root.tail = "\n"
    humanoid.append(humanoid_root)
    humanoid_root_use = xml.etree.ElementTree.Element('HAnimJoint')
    humanoid_root_use.set("USE", "hanim_root")
    humanoid_root_use.set("containerField", "joints")
    humanoid_root_use.text = "\n"
    humanoid_root_use.tail = "\n"
    humanoid.append(humanoid_root_use)
    sacrum = xml.etree.ElementTree.Element('HAnimSegment')
    sacrum.text = "\n"
    sacrum.tail = "\n"
    sacrum.set('DEF', "hanim_sacrum")
    sacrum.set('name', "sacrum")
    humanoid_root.insert(0, sacrum)

    skullbase = xml.etree.ElementTree.Element('HAnimJoint')
    skullbase.set("DEF", "hanim_skullbase")
    skullbase.set("name", "skullbase")
    skullbase.text = "\n"
    skullbase.tail = "\n"
    humanoid_root.append(skullbase)

    skullbase_use = xml.etree.ElementTree.Element('HAnimJoint')
    skullbase_use.set("USE", "hanim_skullbase")
    skullbase_use.set("containerField", "joints")
    skullbase_use.text = "\n"
    skullbase_use.tail = "\n"
    humanoid.append(skullbase_use)

    def_prefixes = ["Hair", "__0", "__2", "__4", "Center_lower_vermillion_lip", "Chin", "Glabella", "Left_bulbar_conjunctiva", "Left_cheek", "Left_dorsum", "Left_ear", "Left_eyebrow", "Left_forehead", "Left_lower_eyelid", "Left_lower_vermillion_lip", "Left_nasolabial_cheek", "Left_nostril", "Left_pupil", "Left_temple", "Left_upper_cutaneous_lip", "Left_upper_eyelid", "Left_upper_vermillion_lip", "Left_upper_vermillion_lip001", "Lower_teeth", "Mid_forehead", "Mid_nasal_dorsum", "Mid_upper_vermillion_lip", "Nasal_tip", "Neck", "Occipital_scalp", "Philtrum", "Right_bulbar_conjunctiva", "Right_cheek", "Right_dorsum", "Right_ear", "Right_eyebrow", "Right_forehead", "Right_lower_eyelid", "Right_lower_vermillion_lip", "Right_nasolabial_cheek", "Right_nostril", "Right_pupil", "Right_temple", "Right_upper_cutaneous_lip", "Right_upper_eyelid", "Right_upper_vermillion_lip", "Tongue", "Upper_teeth"]

    seen_prefixes = []
    for prefix in def_prefixes:
        elements = find_segments_by_prefix(megaX3D, prefix)
        i = 0
        ts = 0
        for element in elements:
            if prefix not in seen_prefixes:
                print(f"Found segment {element.tag} {element.get('DEF')}")
                segment = xml.etree.ElementTree.Element('HAnimSegment')
                segment.text = "\n"
                segment.tail = "\n"
                segment.set('DEF', "hanim_"+prefix)
                segment.set('name', prefix)
                print(f"Adding {segment.tag}")
                skullbase.append(segment)
            for segment_child in element:
                if segment_child.tag == 'HAnimDisplacer':
                    print(f"Adding {segment_child.tag}")
                    segment_child.set("DEF", prefix+"_MorphInterpolator"+str(i))
                    i = i + 1
                    segment.append(segment_child)
                elif segment_child.tag == 'CoordinateInterpolator':
                    print(f"Adding {segment_child.tag}")
                    segment_child.set("DEF", prefix+"_MorphInterpolator"+str(i))
                    i = i + 1
                    segment.append(segment_child)
                elif segment_child.tag == 'TimeSensor':
                    pass
                elif not prefix in seen_prefixes:
                    print(f"Adding {segment_child.tag}")
                    segment.append(segment_child)
                else:
                    # print(f"Don't know what to do with {segment_child.tag}")
                    # segment.append(segment_child)
                    pass
            seen_prefixes.append(prefix)

        # CoordinateInterpolator
        routes = megaX3D.findall(".//ROUTE[@fromNode='"+prefix+"_MorphInterpolator'][@fromField='value_changed'][@toNode='"+prefix+"-COORD'][@toField='point']")
        i = 0
        for route in routes:
            route.set("fromNode", prefix+"_MorphInterpolator"+str(i))
            finalX3D.append(route)
            i += 1

        routes = megaX3D.findall(".//ROUTE[@fromNode='"+prefix+"_AnimationAdapter'][@fromField='value_changed'][@toNode='"+prefix+"_MorphInterpolator'][@toField='set_fraction']")
        i = 0
        for route in routes:
            route.set("fromNode", prefix+"_AnimationAdapter"+str(i))
            route.set("toNode", prefix+"_MorphInterpolator"+str(i))
            finalX3D.append(route)
            i += 1

        # HAnimDisplacer
        routes = megaX3D.findall(".//ROUTE[@fromNode='"+prefix+"_AnimationAdapter'][@fromField='value_changed'][@toNode='"+prefix+"_MorphInterpolator'][@toField='weight']")
        i = 0
        for route in routes:
            route.set("fromNode", prefix+"_AnimationAdapter"+str(i))
            route.set("toNode", prefix+"_MorphInterpolator"+str(i))
            finalX3D.append(route)
            i += 1

        routes = megaX3D.findall(".//ROUTE[@fromNode='"+prefix+"_Clock'][@fromField='fraction_changed'][@toNode='"+prefix+"_AnimationAdapter'][@toField='set_fraction']")
        i = 0
        for route in routes:
            time_sensor = xml.etree.ElementTree.Element('TimeSensor')
            time_sensor.text = "\n"
            time_sensor.tail = "\n"
            time_sensor.set('DEF', prefix+"_Clock"+str(i))
            time_sensor.set('cycleInterval', "4")
            time_sensor.set('enabled', "true")
            time_sensor.set('loop', "true")
            finalX3D.append(time_sensor)

            route.set("fromNode", prefix+"_Clock"+str(i))
            route.set("toNode", prefix+"_AnimationAdaper"+str(i))
            finalX3D.append(route)
            i += 1

    return finalX3D


files = glob.glob('../resources/FACS_AU*_Output.x3d')
#print(f"{files}")

megaX3D = xml.etree.ElementTree.Element('megaX3D')
for input_file in files:
    # print(f"{input_file}")
    megaX3D.append(process_file(input_file))

finalX3D = processMega(megaX3D)

header = '<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE X3D PUBLIC "ISO//Web3D//DTD X3D 4.0//EN" "https://www.web3d.org/specifications/x3d-4.0.dtd">'
xmlstr = xml.etree.ElementTree.tostring(finalX3D, encoding='unicode')
xmlString = f"{header}{xmlstr}"
file_output = os.path.join("../resources/",os.path.basename("ItsAFACSJack.x3d"))
with open(file_output, "w") as output_file:
    output_file.write(xmlString)
