import xml.etree.ElementTree
# from lxml import etree as ElementTree
import os
import re
import glob
import sys
import time



# use helper scripts

# test to see if a number is close to 0
epsilon = sys.float_info.epsilon

def non_zero(num):
    if abs(float(num)) > epsilon:
        return True
    else:
        return False

# find the parent of a child
def find_parent(root, child):
    for parent in root.iter():
        if child in parent:
            return parent
    return None

# find the segments by prefix
def find_segments_by_prefix(root, prefix):
    matched_elements = []
    for elem in root.iter():
        def_value = elem.get("DEF")
        if def_value and elem.tag == 'HAnimSegment':
            if def_value.startswith("hanim"):
                def_value = def_value[6:]
            if prefix == def_value:
                #print(f"looking at {def_value} {prefix} {elem.tag}")
                matched_elements.append(elem)
            else:
                #print(f"missed at {def_value} {prefix} {elem.tag}")
                pass
    return matched_elements

# get the animation from the input file name
def findAnimation(input_filename):
    return input_filename.replace("../resources", "")[1:-4]

# Segment prefixes for related nodes
def_prefixes = ["Lower_teeth", "Hair", "__0", "__2", "__4", "Center_lower_vermillion_lip", "Chin", "Glabella", "Left_bulbar_conjunctiva", "Left_cheek", "Left_dorsum", "Left_ear", "Left_eyebrow", "Left_forehead", "Left_lower_eyelid", "Left_lower_vermillion_lip", "Left_nasolabial_cheek", "Left_nostril", "Left_pupil", "Left_temple", "Left_upper_cutaneous_lip", "Left_upper_eyelid", "Left_upper_vermillion_lip", "Left_upper_vermillion_lip001", "Mid_forehead", "Mid_nasal_dorsum", "Mid_upper_vermillion_lip", "Nasal_tip", "Neck", "Occipital_scalp", "Philtrum", "Right_bulbar_conjunctiva", "Right_cheek", "Right_dorsum", "Right_ear", "Right_eyebrow", "Right_forehead", "Right_lower_eyelid", "Right_lower_vermillion_lip", "Right_nasolabial_cheek", "Right_nostril", "Right_pupil", "Right_temple", "Right_upper_cutaneous_lip", "Right_upper_eyelid", "Right_upper_vermillion_lip", "Tongue", "Upper_teeth"]


# process scenes to create a single scene
def process_scene_list(scene_list):
    SCENE = 0
    for scene_index, scene_element in enumerate(scene_list):
        if scene_index == SCENE:
            # This is the trasform for the head
            transform = xml.etree.ElementTree.Element('Transform')
            transform.text = "\n"
            transform.tail = "\n"
            transform.set("translation", "-37 -20 0")
            transform.set("scale", "2 2 2")
            humanoid = xml.etree.ElementTree.Element('HAnimHumanoid')
            humanoid.text = "\n"
            humanoid.tail = "\n"
            humanoid.set('DEF', "hanim"+str(scene_index)+"_humanoid")
            humanoid.set('name', "humanoid")
            transform.insert(0, humanoid)
            humanoid_root = xml.etree.ElementTree.Element('HAnimJoint')
            humanoid_root.set("DEF", "hanim"+str(scene_index)+"_humanoid_root")
            humanoid_root.set("name", "humanoid_root")
            humanoid_root.set("containerField", "skeleton")
            humanoid_root.text = "\n"
            humanoid_root.tail = "\n"
            humanoid.append(humanoid_root)
            humanoid_root_use = xml.etree.ElementTree.Element('HAnimJoint')
            humanoid_root_use.set("USE", "hanim"+str(scene_index)+"_humanoid_root")
            humanoid_root_use.set("containerField", "joints")
            humanoid_root_use.text = ""
            humanoid_root_use.tail = "\n"
            humanoid.append(humanoid_root_use)
            sacrum = xml.etree.ElementTree.Element('HAnimSegment')
            sacrum.text = "\n"
            sacrum.tail = "\n"
            sacrum.set('DEF', "hanim"+str(scene_index)+"_sacrum")
            sacrum.set('name', "sacrum")
            humanoid_root.insert(0, sacrum)

            skullbase = xml.etree.ElementTree.Element('HAnimJoint')
            skullbase.set("DEF", "hanim"+str(scene_index)+"_skullbase")
            skullbase.set("name", "skullbase")
            skullbase.text = "\n"
            skullbase.tail = "\n"
            humanoid_root.append(skullbase)

            skullbase_use = xml.etree.ElementTree.Element('HAnimJoint')
            skullbase_use.set("USE", "hanim"+str(scene_index)+"_skullbase")
            skullbase_use.set("containerField", "joints")
            skullbase_use.text = ""
            skullbase_use.tail = "\n"
            humanoid.append(skullbase_use)

        segments = scene_element.findall(".//HAnimSegment")
        for segment in segments:
            if scene_index == SCENE:
                skullbase.append(segment)
                for scene_index2, scene_element2 in enumerate(scene_list):
                    segments2 = scene_element2.findall(".//HAnimSegment")
                    for segment2 in segments2:
                        if segment.get('DEF') == segment2.get('DEF') and segment != segment2:
                            displacer = segment2.find("HAnimDisplacer")
                            if displacer is not None:
                                segment.append(displacer)

    return transform


# prcoess elements in a scene setting good DEF and USE values
def process_scene(scene, file):
    animation = findAnimation(file)
    for prefix in def_prefixes:
        elements = find_segments_by_prefix(scene, prefix)
        if len(elements) == 0:
            print(f"{prefix} has not one element")
        for element in elements:
            for segment_child in element:
                if segment_child.tag == 'HAnimDisplacer':
                    #print(f"Setting {segment_child.tag}")
                    segment_child.set("DEF", prefix+"_MorphInterpolator_"+animation)
                elif segment_child.tag == 'ScalarInterpolator':
                    #print(f"Setting {segment_child.tag}")
                    segment_child.set("DEF", "AnimationAdapter_"+animation)
                #elif segment_child.tag == 'CoordinateInterpolator':
                #    print(f"Setting {segment_child.tag}")
                #    segment_child.set("DEF", prefix+"_MorphInterpolator_"+animation)
                elif segment_child.tag in ('Coordinate'):
                    #print(f"Setting {segment_child.tag}")
                    segment_child.set('USE', segment_child.get('USE')+"_"+animation)
                elif segment_child.tag in ('Transform'):
                    #print(f"Setting {segment_child.tag}")
                    for node in segment_child.iter():
                        if node.get('DEF'):
                            node.set('DEF', node.get('DEF')+"_"+animation)
                        if node.get('USE'):
                            node.set('USE', node.get('USE')+"_"+animation)
                elif segment_child.get('DEF'):
                    #print(f"Setting {segment_child.tag}")
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
        #for route in routes:
        #    print(f"Got animation route for {prefix} {animation}")

        # Both
        #routes = scene.findall(".//ROUTE[@fromNode='"+animation+"_Clock'][@fromField='fraction_changed'][@toNode='AnimationAdapter_"+animation+"'][@toField='set_fraction']")
        #for route in routes:
        #    par = find_parent(scene, route)
        #    par.remove(route)

            # Both
            #routes = scene.findall(".//ROUTE[@fromField='enterTime'][@toField='startTime']")
            #for route in routes:
            #    print(f"Got NEW ROUTE")

    return scene


# create a list of scenes from Jin* files
files = glob.glob('../resources/Jin*.x3d')
#print(f"{files}")

scene_list = []
for findex, input_file in enumerate(files):

    # print(f"Input file: {input_file}")
    X3D = xml.etree.ElementTree.parse(input_file)
    root = X3D.getroot()
    scene = root.find("Scene")


    #time_sensors = scene.findall(".//TimeSensor")
    #for time_sensor in time_sensors:
    ##    par = find_parent(scene, time_sensor)
    ##    par.remove(tim_sensor)
    #    print(f"Inserted TimeSensor")
    #    scene.insert(0, time_sensor)

    scene = process_scene(scene, input_file)
    scene_list.append(scene)


# produce final output
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
component.text = ""
component.tail = "\n"
head.append(component)

meta = xml.etree.ElementTree.Element('meta')
meta.text = ""
meta.tail = "\n"
meta.set("name", "title")
meta.set("content", "ManyClocks.x3d")
head.append(meta)

meta = xml.etree.ElementTree.Element('meta')
meta.text = ""
meta.tail = "\n"
meta.set("name", "identifier")
meta.set("content", "https://coderextreme.net/X3DJSONLD/src/main/data/ManyClocks.x3d")
head.append(meta)

meta = xml.etree.ElementTree.Element('meta')
meta.text = ""
meta.tail = "\n"
meta.set("name", "description")
meta.set("content", "X3D scene with multiple facial animations controlled by a multi-selection menu")
head.append(meta)

meta = xml.etree.ElementTree.Element('meta')
meta.text = ""
meta.tail = "\n"
meta.set("name", "created")
meta.set("content", "12 December 2024")
head.append(meta)

meta = xml.etree.ElementTree.Element('meta')
meta.text = ""
meta.tail = "\n"
meta.set("name", "modified")
meta.set("content", "13 December 2024")
head.append(meta)

meta = xml.etree.ElementTree.Element('meta')
meta.text = ""
meta.tail = "\n"
meta.set("name", "creator")
meta.set("content", "John Carlson, Joe Williams, Gyu Ri Cho, Hyun Ho Chu, Min Joo Lee, Yujin Jung")
head.append(meta)

finalX3D.append(head)

scene = xml.etree.ElementTree.Element('Scene')
scene.text = "\n"
scene.tail = "\n"

animation = findAnimation(input_file)

emotions = {
  'HappinessJoy': ["CheekRaiser", "LipCornerPuller"],
  'Sadness': ["InnerBrowRaiser", "BrowLowerer", "LipCornerDepressor"],
  'Surprise': ["InnerBrowRaiser", "OuterBrowRaiser", "UpperLidRaiser", "JawDrop"],
  'Fear': ["InnerBrowRaiser", "OuterBrowRaiser", "BrowLowerer", "UpperLidRaiser", "LidTightener", "LipStretcher", "JawDrop"],
  'Anger': ["BrowLowerer", "UpperLidRaiser", "LidTightener", "LipTightener"],
  'Disgust': ["NoseWrinkler", "LipCornerDepressor", "LowerLipDepressor"],
  'Contempt': ["LipCornerPuller", "Dimpler"]
}

for scene_element in scene_list:
    time_sensors = scene_element.findall(".//TimeSensor")
    for time_sensor in time_sensors:
        time_sensor.set("enabled", "false")
        print(f"Inserted TimeSensor")
        scene.insert(0, time_sensor)

for emotion in emotions:
    time_sensor = xml.etree.ElementTree.Element('TimeSensor')
    time_sensor.text = ""
    time_sensor.tail = "\n"
    time_sensor.set("DEF", emotion+"_Clock")
    time_sensor.set("cycleInterval", "0.99")
    time_sensor.set("loop", "true")
    time_sensor.set("enabled", "false")
    print(f"Inserted TimeSensor")
    scene.insert(0, time_sensor)

time_sensor = xml.etree.ElementTree.Element('TimeSensor')
time_sensor.text = ""
time_sensor.tail = "\n"
time_sensor.set("DEF", "Reset_Clock")
time_sensor.set("cycleInterval", "0.01")
time_sensor.set("loop", "false")
time_sensor.set("enabled", "true")
print(f"Inserted TimeSensor")
scene.insert(0, time_sensor)

for scene_element in scene_list:
    scalarInterpolators = scene_element.findall(".//ScalarInterpolator")
    if len(scalarInterpolators) <= 0:
        print(f"Could not find scalarInterpolators")
    for scalarInterpolator in scalarInterpolators:
        scene.append(scalarInterpolator)

scene.append(process_scene_list(scene_list))

for scene_element in scene_list:
    routes = scene_element.findall(".//ROUTE")
    #if len(routes) <= 0:
    #    print(f"Could not find ROUTEs")
    #else:
    #    print(f"Could find ROUTEs")
    for route in routes:
        # remove ROUTE
        par = find_parent(scene_element, route)
        par.remove(route)
        scene.append(route)
        # print(f"Adding {route.tag}")

finalX3D.append(scene)


header = '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE X3D PUBLIC "ISO//Web3D//DTD X3D 4.0//EN" "https://www.web3d.org/specifications/x3d-4.0.dtd">'
xmlstr = xml.etree.ElementTree.tostring(finalX3D, encoding='unicode')

# produce menu
menu_str = '''
    <!-- Viewpoint and any other scene setup -->
    <WorldInfo title="ManyClocks.x3d"/>
    <Viewpoint position="0 20 110" />
        <ProtoDeclare name="MenuItem">
        <ProtoInterface>
        <field name="translation" accessType="inputOutput" type="SFVec3f"/>
        <field name="textTranslation" accessType="inputOutput" type="SFVec3f"/>
        <field name="description" accessType="inputOutput" type="SFString"/>
        <field name="menuItemString" accessType="inputOutput" type="MFString"/>
        <field name="startTime" accessType="outputOnly" type="SFTime" value="-1"/>
        <field name="stopTime" accessType="outputOnly" type="SFTime" value="-1"/>
        <field name="enabled" accessType="outputOnly" type="SFBool" value="false"/>
        <field name="size" accessType="initializeOnly" type="SFVec2f" value="40.0 3.0"/>
        <field name="fontSize" accessType="inputOutput" type="SFFloat" value="2.4"/>
        <field name="spacing" accessType="initializeOnly" type="SFFloat" value="1.2"/>
        </ProtoInterface>
        <ProtoBody>
        <Group>
        <Transform>
          <IS>
              <connect nodeField="translation" protoField="translation"/>
          </IS>
          <TouchSensor DEF="StartStopAnimationUnit_Sensor">
            <IS>
              <connect nodeField="description" protoField="description"/>
            </IS>
          </TouchSensor>
        <Transform translation="0 0 0">
          <IS>
              <connect nodeField="translation" protoField="textTranslation"/>
          </IS>
          <Shape>
            <Appearance>
              <Material diffuseColor="1 1 1"/>
            </Appearance>
            <Text>
                <IS>
                    <connect nodeField="string" protoField="menuItemString"/>
                </IS>
              <FontStyle justify='"MIDDLE" "MIDDLE"'>
                <IS>
                    <connect nodeField="size" protoField="fontSize"/>
                    <connect nodeField="spacing" protoField="spacing"/>
                </IS>
              </FontStyle>
            </Text>
          </Shape>
        </Transform>
        <Transform translation="0 0 -0.01">
          <Switch DEF="itemMaterial" whichChoice="0">
          <Shape>
            <Appearance>
                <Material diffuseColor="0 0 1"/>
            </Appearance>
            <Rectangle2D size="40.0 3.0">
                <IS>
                    <connect nodeField="size" protoField="size"/>
                </IS>
            </Rectangle2D>
          </Shape>
          <Shape>
            <Appearance>
                <Material diffuseColor="0 1 0"/>
            </Appearance>
            <Rectangle2D size="40.0 3.0">
                <IS>
                    <connect nodeField="size" protoField="size"/>
                </IS>
            </Rectangle2D>
          </Shape>
          </Switch>
        </Transform>
        </Transform>
      <TimeTrigger DEF='startTime'>
            <IS>
            <connect nodeField='triggerTime' protoField='startTime'/>
            </IS>
      </TimeTrigger>
      <TimeTrigger DEF='stopTime'>
            <IS>
            <connect nodeField='triggerTime' protoField='stopTime'/>
            </IS>
      </TimeTrigger>
      <BooleanFilter DEF='veryTrue'>
            <IS>
            <connect nodeField='inputTrue' protoField='enabled'/>
            </IS>
      </BooleanFilter>
      <BooleanFilter DEF='veryFalse' />
      <BooleanSequencer DEF='clickBetweenStates' key='0 1' keyValue='true false'/>
      <IntegerSequencer DEF='toggler' key='0 1' keyValue='1 0' />

      <ROUTE fromNode='clickBetweenStates' fromField='value_changed' toNode='veryTrue' toField='set_boolean'></ROUTE>
      <ROUTE fromNode='veryTrue' fromField='inputTrue' toNode='startTime' toField='set_boolean'></ROUTE>
      <ROUTE fromNode='clickBetweenStates' fromField='value_changed' toNode='veryFalse' toField='set_boolean'></ROUTE>
      <ROUTE fromNode='veryFalse' fromField='inputFalse' toNode='stopTime' toField='set_boolean'></ROUTE>
      <ROUTE fromNode='StartStopAnimationUnit_Sensor' fromField='isActive' toNode='toggler' toField='next'></ROUTE>
      <ROUTE fromNode='toggler' fromField='value_changed' toNode='itemMaterial' toField='whichChoice'></ROUTE>

      <ROUTE fromNode='StartStopAnimationUnit_Sensor' fromField='isActive' toNode='clickBetweenStates' toField='next'></ROUTE>
      </Group>
      </ProtoBody>
      </ProtoDeclare>
'''
ifs_start = 1
increment = -1/12
for emotion, aus in emotions.items():
    menu_str += '<ProtoInstance DEF="'+emotion+'" name="MenuItem">\n'
    menu_str += '<fieldValue name="translation" value="24 '+str(ifs_start*33.4+30)+' 0"/>\n'
    menu_str += '<fieldValue name="textTranslation" value="0 0 0"/>\n'
    menu_str += '<fieldValue name="description" value="'+emotion+'"/>\n'
    menu_str += '<fieldValue name="menuItemString" value=\'"'+emotion+'"\'/>\n'
    menu_str += '<fieldValue name="size" value="40.0 3.0"/>\n'
    menu_str += '<fieldValue name="fontSize" value="2.4"/>\n'
    menu_str += '<fieldValue name="spacing" value="1.2"/>\n'
    #menu_str += '<fieldValue name="startTime"/>\n'
    #menu_str += '<fieldValue name="stopTime"/>\n'
    #menu_str += '<fieldValue name="enabled"/>\n'
    menu_str += '</ProtoInstance>\n'
    for au in aus:
        menu_str += '<ROUTE fromNode="'+emotion+'_Clock" fromField="fraction_changed" toNode="AnimationAdapter_Jin'+au+'" toField="set_fraction"/>\n'
    menu_str += '<ROUTE fromNode="'+emotion+'" fromField="startTime" toNode="'+emotion+'_Clock" toField="startTime"/>\n'
    menu_str += '<ROUTE fromNode="'+emotion+'" fromField="stopTime" toNode="'+emotion+'_Clock" toField="stopTime"/>\n'
    menu_str += '<ROUTE fromNode="'+emotion+'" fromField="enabled" toNode="'+emotion+'_Clock" toField="enabled"/>\n'

    ifs_start += increment

menu_str += '<ProtoInstance DEF="Reset" name="MenuItem">\n'
menu_str += '<fieldValue name="translation" value="24 '+str(ifs_start*33.4+30)+' 0"/>\n'
menu_str += '<fieldValue name="textTranslation" value="0 0 0"/>\n'
menu_str += '<fieldValue name="description" value="Reset"/>\n'
menu_str += '<fieldValue name="menuItemString" value=\'"Reset"\'/>\n'
menu_str += '<fieldValue name="size" value="40.0 3.0"/>\n'
menu_str += '<fieldValue name="fontSize" value="2.4"/>\n'
menu_str += '<fieldValue name="spacing" value="1.2"/>\n'
#menu_str += '<fieldValue name="startTime"/>\n'
#menu_str += '<fieldValue name="stopTime"/>\n'
#menu_str += '<fieldValue name="enabled"/>\n'
menu_str += '</ProtoInstance>\n'
for emotion, aus in emotions.items():
    for au in aus:
        menu_str += '<ROUTE fromNode="Reset_Clock" fromField="fraction_changed" toNode="AnimationAdapter_Jin'+au+'" toField="set_fraction"/>\n'
menu_str += '<ROUTE fromNode="Reset" fromField="startTime" toNode="Reset_Clock" toField="startTime"/>\n'
menu_str += '<ROUTE fromNode="Reset" fromField="stopTime" toNode="Reset_Clock" toField="stopTime"/>\n'
menu_str += '<ROUTE fromNode="Reset" fromField="enabled" toNode="Reset_Clock" toField="enabled"/>\n'

for file_index, input_file in enumerate(files):
    menu_str += '<ROUTE fromNode="Reset_Clock" fromField="fraction_changed" toNode="AnimationAdapter_'+findAnimation(input_file)+'" toField="set_fraction"/>\n'

ifs_start = 1
increment = -1/12
for file_index, input_file in enumerate(files):

    menu_str += '<ProtoInstance DEF="AU'+findAnimation(input_file)+'" name="MenuItem">\n'
    menu_str += '<fieldValue name="translation" value="65 '+str(ifs_start*36+27.4)+' 0"/>\n'
    menu_str += '<fieldValue name="textTranslation" value="0 0 0"/>\n'
    menu_str += '<fieldValue name="description" value="'+re.sub(r"([a-z])([A-Z])", r"\1 \2", findAnimation(input_file))+'"/>\n'
    menu_str += '<fieldValue name="menuItemString" value=\'"'+findAnimation(input_file)+'"\'/>\n'
    menu_str += '<fieldValue name="size" value="40.0 3.0"/>\n'
    menu_str += '<fieldValue name="fontSize" value="2.4"/>\n'
    menu_str += '<fieldValue name="spacing" value="1.2"/>\n'
    #menu_str += '<fieldValue name="startTime"/>\n'
    #menu_str += '<fieldValue name="stopTime"/>\n'
    #menu_str += '<fieldValue name="enabled"/>\n'
    menu_str += '</ProtoInstance>\n'
    menu_str += '<ROUTE fromNode="'+findAnimation(input_file)+'_Clock" fromField="fraction_changed" toNode="AnimationAdapter_'+findAnimation(input_file)+'" toField="set_fraction"/>\n'
    menu_str += '<ROUTE fromNode="AU'+findAnimation(input_file)+'" fromField="startTime" toNode="'+findAnimation(input_file)+'_Clock" toField="startTime"/>\n'
    menu_str += '<ROUTE fromNode="AU'+findAnimation(input_file)+'" fromField="stopTime" toNode="'+findAnimation(input_file)+'_Clock" toField="stopTime"/>\n'
    menu_str += '<ROUTE fromNode="AU'+findAnimation(input_file)+'" fromField="enabled" toNode="'+findAnimation(input_file)+'_Clock" toField="enabled"/>\n'

    ifs_start += increment

menu_str += '''
  </Scene>
</X3D>
'''
xmlString = f"{header}{xmlstr[:-16]}{menu_str}"
file_output = os.path.join("../resources/",os.path.basename("ManyClocks.x3d"))
with open(file_output, "w") as output_file:
    output_file.write(xmlString)
