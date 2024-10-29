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

def findAnimation(input_filename):
    return input_filename.replace("../resources", "")[1:-4]

files = glob.glob('../resources/Jin*.x3d')

def_prefixes = ["Hair", "__0", "__2", "__4", "Center_lower_vermillion_lip", "Chin", "Glabella", "Left_bulbar_conjunctiva", "Left_cheek", "Left_dorsum", "Left_ear", "Left_eyebrow", "Left_forehead", "Left_lower_eyelid", "Left_lower_vermillion_lip", "Left_nasolabial_cheek", "Left_nostril", "Left_pupil", "Left_temple", "Left_upper_cutaneous_lip", "Left_upper_eyelid", "Left_upper_vermillion_lip", "Left_upper_vermillion_lip001", "Lower_teeth", "Mid_forehead", "Mid_nasal_dorsum", "Mid_upper_vermillion_lip", "Nasal_tip", "Neck", "Occipital_scalp", "Philtrum", "Right_bulbar_conjunctiva", "Right_cheek", "Right_dorsum", "Right_ear", "Right_eyebrow", "Right_forehead", "Right_lower_eyelid", "Right_lower_vermillion_lip", "Right_nasolabial_cheek", "Right_nostril", "Right_pupil", "Right_temple", "Right_upper_cutaneous_lip", "Right_upper_eyelid", "Right_upper_vermillion_lip", "Tongue", "Upper_teeth"]

def processAFile(input_file, item_number):
    menu_str = '''
    <Group>
    <Script DEF="Choice'''+str(item_number)+'''">
      <field name="touchTime" type="SFTime" accessType="inputOnly"/>
      <field name="choice" type="SFInt32" accessType="outputOnly"/>
      <![CDATA[
      ecmascript:
      function set_touchTime(value) {
          choice = '''+str(item_number)+''';
      }
      function touchTime(value) {
          choice = '''+str(item_number)+''';
      }
      ]]>
    </Script>
'''
    output_file = os.path.basename(input_file)
    if output_file.endswith(".x3d"):
        output_file = output_file[:-4]+".x3d"
        output_file = os.path.join("../resources/",os.path.basename(output_file))
        try:
            menu_str += '<Inline DEF="'+findAnimation(output_file)+'" url=\'"'+output_file+'" "'+(output_file.replace("../resources/", ""))+'"\'/>\n';
            #for prefix in def_prefixes:
                #menu_str += '<IMPORT inlineDEF="'+findAnimation(output_file)+'" importedDEF="'+prefix+'_Clock" AS="'+prefix+'_Clock"/>\n'

        except xml.etree.ElementTree.ParseError:
            print(f"The file {output_file} has a parse error")
    menu_str += '''</Group>\n'''
    return menu_str
item = 0
menu = ""
for input_file in files:
    if input_file.endswith(".x3d"):
        menu += processAFile(input_file, item)
        item += 1

with open("../resources/MenuJin.x3d", "w") as menu_file:
    menu_str = '''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE X3D PUBLIC "ISO//Web3D//DTD X3D 4.0//EN" "https://www.web3d.org/specifications/x3d-4.0.dtd"><X3D xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" profile="Immersive" version="4.0" xsi:noNamespaceSchemaLocation="http://www.web3d.org/specifications/x3d-4.0.xsd">
  <head>
    <meta content="Menu.x3d" name="title"/>
    <meta content="X3D scene with a Switch of Inlines controlled by a menu" name="description"/>
  </head>
  <Scene>
    <!-- Viewpoint and any other scene setup -->
    <Viewpoint position="0 20 110" />
      <Group>
      <Switch DEF="SceneSwitcher" whichChoice="0">
'''
    menu_str +=  menu
    menu_str += '''</Switch>
'''
    ifs_start = 1
    increment = -1/12
    for file_index, input_file in enumerate(files):
        if input_file.endswith(".x3d"):
            menu_str += '<Transform translation="48 '+str(ifs_start*36+27.4)+' 0">\n'
            menu_str += '<TouchSensor description="TS'+findAnimation(input_file)+'" DEF="'+findAnimation(input_file)+'_Sensor"/>\n'
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
        ifs_start += increment
        menu_str += '<ROUTE fromNode="'+findAnimation(input_file)+'_Sensor" fromField="touchTime" toNode="Choice'+str(file_index)+'" toField="touchTime"/>\n'
        menu_str += '<ROUTE fromNode="Choice'+str(file_index)+'" fromField="choice" toNode="SceneSwitcher" toField="whichChoice"/>\n'
    menu_str += '''
    </Group>
  </Scene>
</X3D>
'''
    menu_file.write(menu_str)
