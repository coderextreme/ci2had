import xml.etree.ElementTree
# from lxml import etree as ElementTree
import os
import re
import glob
import sys
import time

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
            if def_value.startswith("hanim_"):
                def_value = def_value[6:]
            if prefix == def_value:
                #print(f"looking at {def_value} {prefix} {elem.tag}")
                matched_elements.append(elem)
            else:
                #print(f"missed at {def_value} {prefix} {elem.tag}")
                pass
    return matched_elements

def findAnimation(input_filename):
    return input_filename.replace("../resources", "")[1:-4]

def_prefixes = ["Hair", "__0", "__2", "__4", "Center_lower_vermillion_lip", "Chin", "Glabella", "Left_bulbar_conjunctiva", "Left_cheek", "Left_dorsum", "Left_ear", "Left_eyebrow", "Left_forehead", "Left_lower_eyelid", "Left_lower_vermillion_lip", "Left_nasolabial_cheek", "Left_nostril", "Left_pupil", "Left_temple", "Left_upper_cutaneous_lip", "Left_upper_eyelid", "Left_upper_vermillion_lip", "Left_upper_vermillion_lip001", "Lower_teeth", "Mid_forehead", "Mid_nasal_dorsum", "Mid_upper_vermillion_lip", "Nasal_tip", "Neck", "Occipital_scalp", "Philtrum", "Right_bulbar_conjunctiva", "Right_cheek", "Right_dorsum", "Right_ear", "Right_eyebrow", "Right_forehead", "Right_lower_eyelid", "Right_lower_vermillion_lip", "Right_nasolabial_cheek", "Right_nostril", "Right_pupil", "Right_temple", "Right_upper_cutaneous_lip", "Right_upper_eyelid", "Right_upper_vermillion_lip", "Tongue", "Upper_teeth"]


def process_scene_list(scene_list):
    switch = xml.etree.ElementTree.Element('Switch')
    switch.text = ""
    switch.tail = "\n"
    switch.set('DEF', "SceneSwitcher")
    switch.set('whichChoice', "0")
    for scene_index, scene_element in enumerate(scene_list):
        group = xml.etree.ElementTree.Element('Group')
        group.text = ""
        group.tail = "\n"
        switch.append(group)
        humanoid = xml.etree.ElementTree.Element('HAnimHumanoid')
        humanoid.text = ""
        humanoid.tail = "\n"
        humanoid.set('DEF', "hanim_humanoid"+str(scene_index))
        humanoid.set('name', "humanoid")
        group.insert(0, humanoid)
        humanoid_root = xml.etree.ElementTree.Element('HAnimJoint')
        humanoid_root.set("DEF", "hanim_humanoid_root"+str(scene_index))
        humanoid_root.set("name", "humanoid_root")
        humanoid_root.set("containerField", "skeleton")
        humanoid_root.text = ""
        humanoid_root.tail = "\n"
        humanoid.append(humanoid_root)
        humanoid_root_use = xml.etree.ElementTree.Element('HAnimJoint')
        humanoid_root_use.set("USE", "hanim_humanoid_root"+str(scene_index))
        humanoid_root_use.set("containerField", "joints")
        humanoid_root_use.text = ""
        humanoid_root_use.tail = "\n"
        humanoid.append(humanoid_root_use)
        sacrum = xml.etree.ElementTree.Element('HAnimSegment')
        sacrum.text = ""
        sacrum.tail = "\n"
        sacrum.set('DEF', "hanim_sacrum"+str(scene_index))
        sacrum.set('name', "sacrum")
        humanoid_root.insert(0, sacrum)

        skullbase = xml.etree.ElementTree.Element('HAnimJoint')
        skullbase.set("DEF", "hanim_skullbase"+str(scene_index))
        skullbase.set("name", "skullbase")
        skullbase.text = ""
        skullbase.tail = "\n"
        humanoid_root.append(skullbase)

        skullbase_use = xml.etree.ElementTree.Element('HAnimJoint')
        skullbase_use.set("USE", "hanim_skullbase"+str(scene_index))
        skullbase_use.set("containerField", "joints")
        skullbase_use.text = ""
        skullbase_use.tail = "\n"
        humanoid.append(skullbase_use)

        for prefix in def_prefixes:
            elements = find_segments_by_prefix(scene_element, prefix)
            segment = xml.etree.ElementTree.Element('HAnimSegment')
            segment.text = ""
            segment.tail = "\n"
            segment.set('DEF', "hanim_"+prefix+str(scene_index))
            segment.set('name', prefix.lower())
            skullbase.append(segment)
            if len(elements) == 0:
                print(f"{prefix} has no elements")
            else:
                print(f"{prefix} has some elements")
            for element in elements:
                print(f"Found element {element.tag} {element.get('DEF')}")
                for segment_child in element:
                    print(f"2Adding {segment_child.tag}")
                    segment.append(segment_child)
        # ts_list = []
        for scene_element in scene_list:
            #time_sensors = scene_element.findall(".//TimeSensor")
            #if len(time_sensors) <= 0:
            #    print(f"Could not find TimeSensors")
            #for time_sensor in time_sensors:
            #    group.append(time_sensor)
            #    ts_list.append(time_sensor)
            #    print(f"Adding {time_sensor.tag} {time_sensor.get('DEF')}")

            proximity_sensors = scene_element.findall(".//ProximitySensor")
            if len(proximity_sensors) <= 0:
                print(f"Could not find ProximitySensor")
            else:
                for proximity_sensor in proximity_sensors:
                    group.append(proximity_sensor)
                    print(f"Adding {proximity_sensor.tag} {proximity_sensor.get('DEF')}")


    #        for t, time_sensor in enumerate(ts_list):
    #            # print("Time", t)
    #            for other_t, other_time_sensor in enumerate(ts_list):
    #                if time_sensor != other_time_sensor:
    #                    route = xml.etree.ElementTree.Element('ROUTE')
    #                    route.text = ""
    #                    route.tail = "\n"
    #                    route.set("fromNode", time_sensor.get('DEF'))
    #                    route.set("fromField", "startTime")
    #                    route.set("toNode", other_time_sensor.get('DEF'))
    #                    route.set("toField", "stopTime")
    #                    group.append(route)
    #                #print("Other", other_t)

    return switch


def process_scene(scene, file):
    animation = findAnimation(file)
    for prefix in def_prefixes:
        elements = find_segments_by_prefix(scene, prefix)
        if len(elements) == 0:
            print(f"{prefix} has not one element")
        for element in elements:
            for segment_child in element:
                if segment_child.tag == 'HAnimDisplacer':
                    print(f"Setting {segment_child.tag}")
                    segment_child.set("DEF", prefix+"_MorphInterpolator_"+animation)
                elif segment_child.tag == 'ScalarInterpolator':
                    print(f"Setting {segment_child.tag}")
                    segment_child.set("DEF", "AnimationAdapter_"+animation)
                #elif segment_child.tag == 'CoordinateInterpolator':
                #    print(f"Setting {segment_child.tag}")
                #    segment_child.set("DEF", prefix+"_MorphInterpolator_"+animation)
                elif segment_child.tag in ('Coordinate'):
                    print(f"Setting {segment_child.tag}")
                    segment_child.set('USE', segment_child.get('USE')+"_"+animation)
                elif segment_child.tag in ('Transform'):
                    print(f"Setting {segment_child.tag}")
                    for node in segment_child.iter():
                        if node.get('DEF'):
                            print(f"Setting {node.tag}")
                            node.set('DEF', node.get('DEF')+"_"+animation)
                elif segment_child.get('DEF'):
                    print(f"Setting {segment_child.tag}")
                    segment_child.set('DEF', segment_child.get('DEF')+"_"+animation)

        # CoordinateInterpolator
        #routes = scene.findall(".//ROUTE[@fromNode='"+prefix+"_MorphInterpolator'][@fromField='value_changed'][@toNode='"+prefix+"-COORD'][@toField='point']")
        #for route in routes:
        #    route.set("fromNode", prefix+"_MorphInterpolator_"+animation)
        #    # remove ROUTE
        #    par = find_parent(scene, route)
        #    par.remove(route)

        #routes = scene.findall(".//ROUTE[@fromNode='"+prefix+"_AnimationAdapter'][@fromField='value_changed'][@toNode='"+prefix+"_MorphInterpolator'][@toField='set_fraction']")
        #for route in routes:
        #    route.set("fromNode", prefix+"_AnimationAdapter_"+animation)
        #    route.set("toNode", prefix+"_MorphInterpolator_"+animation)
        #    # remove ROUTE
        #    par = find_parent(scene, route)
        #    par.remove(route)

        # HAnimDisplacer
        routes = scene.findall(".//ROUTE[@fromNode='AnimationAdapter_"+animation+"'][@fromField='value_changed'][@toNode='"+prefix+"_MorphInterpolator_"+animation+"'][@toField='weight']")
        for route in routes:
            print(f"setting from AnimationAdapter_{animation} to {prefix}_MorphInterpolator_{animation}")

        # Both
        routes = scene.findall(".//ROUTE[@fromNode='"+prefix+"_Clock'][@fromField='fraction_changed'][@toNode='"+prefix+"_AnimationAdapter_"+animation+"'][@toField='set_fraction']")
        for route in routes:
            clock_name = animation+"_Clock"
            print(f"Got route for {prefix} {animation}, clock name is {clock_name}")
            route.set("fromNode", clock_name)
            route.set("toNode", prefix+"_AnimationAdapter_"+animation)

        # Both
        #routes = scene.findall(".//ROUTE[@fromField='enterTime'][@toField='startTime']")
        #for route in routes:
        #    print(f"Got NEW ROUTE")

    return scene


files = glob.glob('../resources/Jin*.x3d')
#print(f"{files}")

scene_list = []
for findex, input_file in enumerate(files):

    print(f"Input file: {input_file}")
    X3D = xml.etree.ElementTree.parse(input_file)
    root = X3D.getroot()
    scene = root.find("Scene")


#    time_sensors = scene.findall(".//TimeSensor")
#    for tim_sensor in time_sensors:
#        par = find_parent(scene, tim_sensor)
#        par.remove(tim_sensor)
#        print(f"Removed TimeSensor")

    scene = process_scene(scene, input_file)
    scene_list.append(scene)


finalX3D = xml.etree.ElementTree.Element('X3D')
finalX3D.text = ""
finalX3D.tail = "\n"
finalX3D.set("profile", "Immersive")
finalX3D.set("version", "4.0")
head = xml.etree.ElementTree.Element('head')
head.text = ""
head.tail = "\n"
component = xml.etree.ElementTree.Element('component')
component.set("name", "HAnim")
component.set("level", "3")
component.text = ""
component.tail = "\n"
head.append(component)

meta = xml.etree.ElementTree.Element('meta')
meta.text = ""
meta.tail = "\n"
meta.set("name", "title")
meta.set("content", "YehudiMenuJin.x3d")
head.append(meta)

meta = xml.etree.ElementTree.Element('meta')
meta.text = ""
meta.tail = "\n"
meta.set("name", "description")
meta.set("content", "X3D scene with alternate facial animations controlled by a menu")
head.append(meta)
finalX3D.append(head)

scene = xml.etree.ElementTree.Element('Scene')
scene.text = ""
scene.tail = "\n"

animation = findAnimation(input_file)
clock_name = animation+"_Clock"
proximity_sensor = xml.etree.ElementTree.Element('ProximitySensor')
proximity_sensor.text = ""
proximity_sensor.tail = "\n"
proximity_sensor.set('DEF', "Fire_"+clock_name)
proximity_sensor.set("size", "10000 10000 10000")
scene.insert(0, proximity_sensor)

for findex, input_file in enumerate(files):
    animation = findAnimation(input_file)
    clock_name = animation+"_Clock"
    time_sensor = xml.etree.ElementTree.Element('TimeSensor')
    time_sensor.text = ""
    time_sensor.tail = "\n"
    time_sensor.set('DEF', clock_name)
    time_sensor.set('cycleInterval',"4")
    time_sensor.set('loop', "false")
    time_sensor.set('enabled', "true")
    scene.append(time_sensor)

for scene_element in scene_list:
    scalarInterpolators = scene_element.findall(".//ScalarInterpolator")
    if len(scalarInterpolators) <= 0:
        print(f"Could not find scalarInterpolators")
    for scalarInterpolator in scalarInterpolators:
        scene.append(scalarInterpolator)

scene.append(process_scene_list(scene_list))

routes = scene_element.findall(".//ROUTE")
if len(routes) <= 0:
    print(f"Could not find ROUTEs")
else:
    print(f"Could find ROUTEs")
for route in routes:
    scene.append(route)
    # print(f"Adding {route.tag}")

print(f"Added proximity is {proximity_sensor.get('DEF')}")
route = xml.etree.ElementTree.Element('ROUTE')
route.text = ""
route.tail = "\n"
route.set("fromNode", proximity_sensor.get('DEF'))
route.set("fromField", "enterTime")
route.set("toNode", clock_name)
route.set("toField", "startTime")
scene.append(route)

finalX3D.append(scene)

header = '<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE X3D PUBLIC "ISO//Web3D//DTD X3D 4.0//EN" "https://www.web3d.org/specifications/x3d-4.0.dtd">'
xmlstr = xml.etree.ElementTree.tostring(finalX3D, encoding='unicode')

menu_str = '''
    <!-- Viewpoint and any other scene setup -->
    <Viewpoint position="0 20 110" />
      <Group>
      '''
ifs_start = 1
increment = -1/12
for file_index, input_file in enumerate(files):

    if input_file.endswith(".x3d"):
        menu_str += '''
    <Script DEF="Choice'''+str(file_index)+'''">
      <field name="touchTime" type="SFTime" accessType="inputOnly"/>
      <field name="choice" type="SFInt32" accessType="outputOnly"/>
      <![CDATA[
      ecmascript:
      function set_touchTime(value) {
          choice = '''+str(file_index)+''';
      }
      function touchTime(value) {
          choice = '''+str(file_index)+''';
      }
      ]]>
    </Script>
'''
        menu_str += '<Transform translation="48 '+str(ifs_start*36+27.4)+' 0">\n'
        menu_str += '<TouchSensor description="'+re.sub(r"([a-z])([A-Z])", r"\1 \2", findAnimation(input_file))+'" DEF="'+findAnimation(input_file)+'_Sensor"/>\n'
        menu_str += '''
          <Shape>
            <Appearance>
              <Material diffuseColor="1 1 1"/>
            </Appearance>
            '''
        menu_str += '<Text string=\'"'+findAnimation(input_file)+'"\'>\n'
        menu_str += '''
              <FontStyle size="2.4" spacing="1.2" justify='"MIDDLE" "MIDDLE"'/>
            </Text>
          </Shape>
          <Shape>
            <Appearance>
              <Material diffuseColor="0 0 1"/>
            </Appearance>
            <IndexedFaceSet coordIndex='0 1 2 3 -1'>
            '''
        ypos = - increment + 1.0
        xpos = 20
        menu_str += '<Coordinate point="'+str(xpos)+' '+str(ypos+0.3)+' -0.1, '+str(-xpos)+' '+str(ypos+0.3)+' -0.1, '+str(-xpos)+' '+str(ypos-2.7)+' -0.1, '+str(xpos)+' '+str(ypos-2.7)+' -0.1"/>\n'
        menu_str += '''
             </IndexedFaceSet>
          </Shape>
        </Transform>
'''
        menu_str += '<ROUTE fromNode="'+findAnimation(input_file)+'_Sensor" fromField="touchTime" toNode="Choice'+str(file_index)+'" toField="touchTime"/>\n'
        menu_str += '<ROUTE fromNode="Choice'+str(file_index)+'" fromField="choice" toNode="SceneSwitcher" toField="whichChoice"/>\n'
    ifs_start += increment
menu_str += '''
    </Group>
  </Scene>
</X3D>
'''
xmlString = f"{header}{xmlstr[:-16]}{menu_str}"
file_output = os.path.join("../resources/",os.path.basename("YehudiMenuJin.x3d"))
with open(file_output, "w") as output_file:
    output_file.write(xmlString)
