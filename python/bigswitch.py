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

def process_file(file_input, findex):
    print(f"Input file: {file_input}")
    X3D = xml.etree.ElementTree.parse(file_input)
    root = X3D.getroot()
    scene = root.find("Scene")

    time_sensors = scene.findall(".//TimeSensor")
    for time_sensor in time_sensors:
        par = find_parent(scene, time_sensor)
        par.remove(time_sensor)
        print(f"Removed TimeSensor, DEF is {time_sensor.get('DEF')}")

    time_sensor = xml.etree.ElementTree.Element('TimeSensor')
    time_sensor.text = "\n"
    time_sensor.tail = "\n"
    animation = findAnimation(file_input)
    clock_name = animation+"_Clock"
    time_sensor.set('DEF', clock_name)
    time_sensor.set('cycleInterval', "4")
    time_sensor.set('loop', "false")
    time_sensor.set('enabled', "true")
    if len(scene) >= 0:
        scene.insert(0, time_sensor)
        print(f"Added clock name is {clock_name}")
    else:
        print(f"Not Added clock name is {clock_name}")
    if findex == 0:
        proximity_sensor = xml.etree.ElementTree.Element('ProximitySensor')
        if proximity_sensor is not None:
            proximity_sensor.text = "\n"
            proximity_sensor.tail = "\n"
            proximity_sensor.set('DEF', "Fire_"+clock_name)
            proximity_sensor.set("size", "10000 10000 10000")
            scene.append(proximity_sensor)
            print(f"Added proximity is {proximity_sensor.get('DEF')}")
        else:
            print(f"Couldn't Add proximity")

        route = xml.etree.ElementTree.Element('ROUTE')
        route.text = "\n"
        route.tail = "\n"
        route.set("fromNode", proximity_sensor.get('DEF'))
        route.set("fromField", "enterTime")
        route.set("toNode", time_sensor.get('DEF'))
        route.set("toField", "startTime")
        scene.append(route)

    return scene


def processMega(scene_list, files):
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
    head.append(component)

    meta = xml.etree.ElementTree.Element('meta')
    meta.text = "\n"
    meta.tail = "\n"
    meta.set("name", "title")
    meta.set("content", "YehudiMenuJin.x3d")
    head.append(meta)

    meta = xml.etree.ElementTree.Element('meta')
    meta.text = "\n"
    meta.tail = "\n"
    meta.set("name", "description")
    meta.set("content", "X3D scene with alternate facial animations controlled by a menu")
    head.append(meta)

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
    humanoid_root.set("DEF", "hanim_humanoid_root")
    humanoid_root.set("name", "humanoid_root")
    humanoid_root.set("containerField", "skeleton")
    humanoid_root.text = "\n"
    humanoid_root.tail = "\n"
    humanoid.append(humanoid_root)
    humanoid_root_use = xml.etree.ElementTree.Element('HAnimJoint')
    humanoid_root_use.set("USE", "hanim_humanoid_root")
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
    seen_prefixes = []
    for scene_element in scene_list:
        for prefix in def_prefixes:
            elements = find_segments_by_prefix(scene_element, prefix)
            if len(elements) == 0:
                print(f"{prefix} has no elements")
            for element in elements:
                print(f"Found element {element.tag} {element.get('DEF')}")
                if prefix not in seen_prefixes:
                    print(f"2Found segment {element.tag} {element.get('DEF')}")
                    segment = xml.etree.ElementTree.Element('HAnimSegment')
                    segment.text = "\n"
                    segment.tail = "\n"
                    segment.set('DEF', "hanim_"+prefix)
                    segment.set('name', prefix.lower())
                    print(f"Adding {segment.tag}")
                    skullbase.append(segment)
                else:
                    print(f"2Didn't find segment {element.tag} {element.get('DEF')}")
                for segment_child in element:
                    if segment_child.tag in ('HAnimDisplacer', 'ScalarInterpolator'):
                        # print(f"Adding {segment_child.tag}")
                        segment.append(segment_child)
                    elif not prefix in seen_prefixes:
                        print(f"2Don't know {segment_child.tag} {element.get('DEF')}")
                        segment.append(segment_child)  # append first Transform and Coordinate
                    else:
                        print(f"2Don't know what to do with {segment_child.tag}")
                        # segment.append(segment_child)
                seen_prefixes.append(prefix)
    ts_list = []
    for scene_element in scene_list:
        time_sensors = scene_element.findall(".//TimeSensor")
        if len(time_sensors) <= 0:
            print(f"Could not find TimeSensors")
        for time_sensor in time_sensors:
            scene.append(time_sensor)
            ts_list.append(time_sensor)
            print(f"Adding {time_sensor.tag} {time_sensor.get('DEF')}")

        proximity_sensors = scene_element.findall(".//ProximitySensor")
        if len(proximity_sensors) <= 0:
            print(f"Could not find ProximitySensor")
        else:
            for proximity_sensor in proximity_sensors:
                scene.append(proximity_sensor)
                print(f"Adding {proximity_sensor.tag} {proximity_sensor.get('DEF')}")

        routes = scene_element.findall(".//ROUTE")
        if len(routes) <= 0:
            print(f"Could not find ROUTEs")
        for route in routes:
            scene.append(route)
            # print(f"Adding {route.tag}")

        for t, time_sensor in enumerate(ts_list):
            # print("Time", t);
            for other_t, other_time_sensor in enumerate(ts_list):
                if time_sensor != other_time_sensor:
                    route = xml.etree.ElementTree.Element('ROUTE')
                    route.text = "\n"
                    route.tail = "\n"
                    route.set("fromNode", time_sensor.get('DEF'))
                    route.set("fromField", "startTime")
                    route.set("toNode", other_time_sensor.get('DEF'))
                    route.set("toField", "stopTime")
                    scene.append(route)
                #print("Other", other_t);

    return finalX3D


def process_scene(scene, file):
    seen_prefixes = []
    animation = findAnimation(file)
    for prefix in def_prefixes:
        elements = find_segments_by_prefix(scene, prefix)
        if len(elements) == 0:
            print(f"{prefix} has not one element")
        for element in elements:
            if prefix not in seen_prefixes:
                print(f"Found segment {element.tag} {element.get('DEF')}")
            else:
                print(f"Didn't find segment {element.tag} {element.get('DEF')}")
            for segment_child in element:
                if segment_child.tag == 'HAnimDisplacer':
                    print(f"Setting {segment_child.tag}")
                    segment_child.set("DEF", prefix+"_MorphInterpolator_"+animation)
                elif segment_child.tag == 'ScalarInterpolator':
                    print(f"Setting {segment_child.tag}")
                    segment_child.set("DEF", prefix+"_AnimationAdapter_"+animation)
                #elif segment_child.tag == 'CoordinateInterpolator':
                #    print(f"Setting {segment_child.tag}")
                #    segment_child.set("DEF", prefix+"_MorphInterpolator_"+animation)
                elif not prefix in seen_prefixes:
                    print(f"Don't know {segment_child.tag} {element.get('DEF')}")
                    # segment_child.set("DEF", prefix+f"_{segment_child.tag}_"+animation)
                else:
                    print(f"Don't know what to do with {segment_child.tag}")
                    # segment.append(segment_child)
                    pass
            seen_prefixes.append(prefix)

        # CoordinateInterpolator
        routes = scene.findall(".//ROUTE[@fromNode='"+prefix+"_MorphInterpolator'][@fromField='value_changed'][@toNode='"+prefix+"-COORD'][@toField='point']")
        for route in routes:
            route.set("fromNode", prefix+"_MorphInterpolator_"+animation)

        routes = scene.findall(".//ROUTE[@fromNode='"+prefix+"_AnimationAdapter'][@fromField='value_changed'][@toNode='"+prefix+"_MorphInterpolator'][@toField='set_fraction']")
        for route in routes:
            route.set("fromNode", prefix+"_AnimationAdapter_"+animation)
            route.set("toNode", prefix+"_MorphInterpolator_"+animation)

        # HAnimDisplacer
        routes = scene.findall(".//ROUTE[@fromNode='"+prefix+"_AnimationAdapter'][@fromField='value_changed'][@toNode='"+prefix+"_MorphInterpolator'][@toField='weight']")
        for route in routes:
            route.set("fromNode", prefix+"_AnimationAdapter_"+animation)
            route.set("toNode", prefix+"_MorphInterpolator_"+animation)

        # Both
        routes = scene.findall(".//ROUTE[@fromNode='"+prefix+"_Clock'][@fromField='fraction_changed'][@toNode='"+prefix+"_AnimationAdapter'][@toField='set_fraction']")
        for route in routes:
            clock_name = animation+"_Clock"
            print(f"Got route for {prefix} {animation}, clock name is {clock_name}")
            route.set("fromNode", clock_name)
            route.set("toNode", prefix+"_AnimationAdapter_"+animation)

        # Both
        routes = scene.findall(".//ROUTE[@fromField='enterTime'][@toField='startTime']")
        for route in routes:
            print(f"Got NEW ROUTE")

    return scene


files = glob.glob('../resources/Jin*.x3d')
#print(f"{files}")

megaX3D = xml.etree.ElementTree.Element('megaX3D')
scene_list = []
for findex, input_file in enumerate(files):
    # print(f"{input_file}")
    scene = process_file(input_file, findex)
    time_sensors = scene.findall(".//TimeSensor")
    if len(time_sensors) > 0:
        for time_sensor in time_sensors:
            # scene.append(time_sensor)
            print(f"Found TimeSensor {time_sensor.tag} {time_sensor.get('DEF')}")
    else:
        print("Could not find TimeSensor")
    scene = process_scene(scene, input_file)
    scene_list.append(scene)

finalX3D = processMega(scene_list, files)

header = '<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE X3D PUBLIC "ISO//Web3D//DTD X3D 4.0//EN" "https://www.web3d.org/specifications/x3d-4.0.dtd">'
xmlstr = xml.etree.ElementTree.tostring(finalX3D, encoding='unicode')

menu_str = '''
    <!-- Viewpoint and any other scene setup -->
    <Viewpoint position="0 20 110" />
    <ProtoDeclare name="Menu">
      <ProtoInterface>
        <field name="menuItems" type="MFString" accessType="initializeOnly"/>
      </ProtoInterface>
      <ProtoBody>
      <Group>
        <Transform DEF="TextMenuTransform" translation="48 27 0">
         <TouchSensor DEF="MenuTouchSensor"/>
          <Shape>
            <Appearance>
              <Material diffuseColor="1 1 1"/>
            </Appearance>
            <Text DEF="MenuText">
              <IS>
                <connect nodeField="string" protoField="menuItems"/>
              </IS>
              <FontStyle size="2.4" spacing="1.2" justify='"MIDDLE" "MIDDLE"'/>
            </Text>
          </Shape>
          <Shape>
            <Appearance>
              <Material diffuseColor="0 0 1"/>
            </Appearance>
            <IndexedFaceSet DEF='Backing' coordIndex='0 1 2 3 -1'>
                <Coordinate point='25 36 -0.1, -25 36 -0.1, -25 -52 -0.1, 25 -52 -0.1'/>
             </IndexedFaceSet>
          </Shape>
        </Transform>

    <!-- Script to handle selection logic -->
    <Script DEF="MenuScript">
      <field name="menuItems" type="MFString" accessType="initializeOnly"/>
      <field name="selection" type="SFInt32" accessType="outputOnly"/>
      <field name="touchPoint" type="SFVec3f" accessType="inputOnly"/>
      <field name="spacing" type="SFFloat" accessType="initializeOnly" value="1.2"/>
      <field name="size" type="SFFloat" accessType="initializeOnly" value="2.4"/>
      <field name="menuCenterY" type="SFFloat" accessType="initializeOnly"/>
      <field name="itemHeight" type="SFFloat" accessType="initializeOnly"/>
      <field name="oldSelection" type="SFInt32" accessType="inputOutput"/>

      <![CDATA[ecmascript:
        function initialize() {
          selection = 0;
          oldSelection = 0;
          var spacingBetweenGlyphs = size * spacing - size; // Spacing calculation
          var menuHeight = (size + spacingBetweenGlyphs) * menuItems.length;
          menuCenterY = menuHeight / 2;
          itemHeight = menuHeight / menuItems.length;
          var sel = 0;
          for (sel = 0; sel < menuItems.length; sel++) {
            var node = Browser.currentScene.getNamedNode(menuItems[sel]);
            if (node) {
                node.getField("stopTime").setValue(0);
            } else {
                Browser.println("Can't get menu node, duh!");
            }
          }
        }

        function touchPoint(value, tm) {
          Browser.println("Hit "+value+" "+selection);
          var index = Math.floor((menuCenterY - value.y) / itemHeight - 0.5);

          selection = index - 2;
          if (selection >= 0 && selection < menuItems.length) {
            /*
            var nodes = Browser.currentScene.rootNodes;
            for (var n = 0; n < nodes.length; n++) {
              try {
                if (nodes[n].DEF) {
                    Browser.println("DEF "+nodes[n].DEF);
                } else {
                    Browser.println("no DEF "+JSON.stringify(nodes[n]));
                }
              } catch (e) {
                Browser.print(e);
              }
            }
            */

            var node = Browser.currentScene.getNamedNode(menuItems[selection]+"_Clock");
            if (node) {
                node.startTime = tm;
                node.enabled = true;
            } else {
                Browser.println(node+" Couldn't enable "+menuItems[selection]+"_Clock");
            }

            oldSelection = selection;
            Browser.println("Selected "+selection+" "+menuItems[selection]);
          }
        }
      ]]>
      <IS>
         <connect nodeField="menuItems" protoField="menuItems"/>
      </IS>
    </Script>

     <!-- ROUTEs to connect everything -->
     <ROUTE fromNode="MenuTouchSensor"   fromField="hitPoint_changed" toNode="MenuScript" toField="touchPoint"/>
     <!--
     <ROUTE fromNode="MenuScript" fromField="selection" toNode="SceneSwitcher" toField="whichChoice"/>
     -->
      </Group>
      </ProtoBody>
    </ProtoDeclare>
    <ProtoInstance DEF='MainMenu' name='Menu'>
      <fieldValue name='menuItems' value=\''''
for input_file in files:
    if input_file.endswith(".x3d"):
        menu_str += '"'+findAnimation(input_file)+'" '
menu_str += '''\'/>
    </ProtoInstance>
  </Scene>
</X3D>
'''
xmlString = f"{header}{xmlstr[:-16]}{menu_str}"
file_output = os.path.join("../resources/",os.path.basename("YehudiMenuJin.x3d"))
with open(file_output, "w") as output_file:
    output_file.write(xmlString)
