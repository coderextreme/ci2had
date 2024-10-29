import xml.etree.ElementTree
# from lxml import etree as ElementTree
import os
import re

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

def process_file(file_input, file_output):
    print(f"Input file: {file_input.name}")
    X3D = xml.etree.ElementTree.parse(file_input)
    root = X3D.getroot()
    head = root.find('head')
    scene = root.find('Scene')
    component = xml.etree.ElementTree.Element('component')
    component.set("name", "HAnim")
    component.set("level", "3")
    component.text = None
    component.tail = "\n"
    head.insert(0, component)

    humanoid = xml.etree.ElementTree.Element('HAnimHumanoid')
    humanoid.text = "\n"
    humanoid.tail = "\n"
    humanoid.set('DEF', "hanim_humanoid")
    humanoid.set('name', "humanoid")
    scene.insert(0, humanoid)
    humanoid_root = xml.etree.ElementTree.Element('HAnimJoint')
    humanoid_root.set("DEF", "hanim_root")
    humanoid_root.set("name", "humanoid_root")
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

    for it in root.iter('ImageTexture'):
        url = it.get("url")
        if url is not None and not url.startswith('"') and not url.startswith('&quot;'):
                it.set("url", "\""+it.get("url")+"\"")
    for cis in root.iter('CoordinateInterpolator'):
        DEF = cis.get("DEF")
        # print(f"DEF={DEF}")
        keys = cis.get("key").split()
        keyValues = cis.get("keyValue").split()

        numKeys = len(keys)
        valuesPerKey = int(len(keyValues)/numKeys)
        # print("valuesPerKey", valuesPerKey)
        # print(keys)
        # print(keyValues)
        key = 0
        base = keyValues[valuesPerKey*key:valuesPerKey*(key+1)]
        key = numKeys - 1
        extension = keyValues[valuesPerKey*key:valuesPerKey*(key+1)]
        # print(base)
        # print(extension)

        displacements = []
        new_node = None
        non_zero_displacement = False
        for i in range(len(base)):
            difference = float(extension[i]) - float(base[i])
            displacements.append(str(round(difference, 4)))
            if new_node is None:
                # print (f"{DEF} {i}, {extension[i]}, {base[i]}")
                new_node = xml.etree.ElementTree.Element('HAnimDisplacer')
                new_node.text = "\n"
                new_node.tail = "\n"
            if non_zero(difference):
                non_zero_displacement = True
            #    print (f"{DEF} keyValue base point index (0 indexed) {i}, {extension[i]} - {base[i]} = {round(difference,4)}")
            if i % 3 == 0:
                v = int(i / 3)
                #print(f"[ \\vec{v} = ", end="")
                pass
            if i % 3 == 2:
                #print(f"({extension[i]} - {base[i]}, {extension[i-1]} - {base[i-1]}, {extension[i-2]} - {base[i-2]}) = ({displacements[-3]}, {displacements[-2]}, {displacements[-1]}) ]")
                pass

        if new_node is not None:
            new_node.set("DEF", DEF+"_"+findAnimation(file_output))
            new_node.set("name", DEF.lower())
            new_node.set("weight", "0")
            new_node.set("containerField", "displacers")

        parent = find_parent(root, cis)
        if parent is not None:
            index = get_node_index(parent, cis)
            if index is not None:
                # Add the HAnimDisplacer to the 'sacrum' segment
                if new_node is not None:
                    sacrum.append(new_node)
                    # CoordinateInterpolator changed to HAnimDisplacer
                    routes = root.findall(".//ROUTE[@fromField='value_changed'][@toField='set_fraction'][@toNode='"+DEF+"']")
                    # Replace set_fraction with weight
                    for route in routes:
                        route.set("fromNode", route.get("fromNode")+"_"+findAnimation(file_output))
                        route.set("toField", "weight")
                        route.set("toNode", DEF+"_"+findAnimation(file_output))

                    # Replace value_changed with weight
                    routes = root.findall(".//ROUTE[@fromField='value_changed'][@fromNode='"+DEF+"']")
                    for route in routes:
                        # Set coordIndex of the new HAnimDisplacer node.
                        COORDDEF = route.get("toNode")
                        coords = root.findall(".//*[@DEF='"+COORDDEF+"']")
                        for coord in coords:
                            ifs = find_parent(root, coord)
                            if ifs is not None:
                                coordinate_node = ifs.find("Coordinate")
                                points = coordinate_node.get("point").split()
                                pointsMatrix = split_every_third(points)
                                baseMatrix = split_every_third(base)
                                displacementsMatrix = split_every_third(displacements)
                                coordIndex = []
                                newDisplacements = []
                                for i, point in enumerate(pointsMatrix): # Loop through Coordinate points
                                    for j, base_point in enumerate(baseMatrix):
                                        if point == base_point and (non_zero(displacementsMatrix[i][0]) or non_zero(displacementsMatrix[i][1]) or non_zero(displacementsMatrix[i][2])):
                                        #if point == base_point:
                                            coordIndex.append(str(i))
                                            dis = " ".join(displacementsMatrix[i])
                                            newDisplacements.append(dis)
                                            # break # Assume a base point only maps to one point
                                coordIndex = " ".join(coordIndex)
                                newDisplacements = ", ".join(newDisplacements)
                                if non_zero_displacement:
                                    new_node.set("coordIndex", coordIndex)
                                    new_node.set("displacements", newDisplacements)
                                # print(f"coordIndex {coordIndex} displacement {newDisplacements}\n")
                                #new_node.set("displacements", " ".join(displacements))
                        # remove route from CoordinateInterpolator to Coordinate
                        par = find_parent(root, route)
                        par.remove(route)

                        parent.remove(cis)
        # parent.remove(cis)
    # Clock to Adapter
    routes = scene.findall(".//ROUTE[@fromField='fraction_changed'][@toField='set_fraction']")
    for route in routes:
        route.set("toNode", route.get("toNode")+"_"+findAnimation(file_output))

    scinterpolators = root.findall(".//ScalarInterpolator")
    for scinterpolator in scinterpolators:
        scinterpolator.set("DEF", scinterpolator.get("DEF")+"_"+findAnimation(file_output))


    # Move other elements into the 'sacrum' segment
    for element in list(scene):
        if not element.tag in ("HAnimHumanoid", "HAnimJoint", "HAnimSegment", "HAnimDisplacer") and element.tag != "ROUTE":
            sacrum.append(element)
            scene.remove(element)
        #elif element.tag == 'ROUTE':
        #    scene.remove(element)
        #    scene.append(element)

    def_prefixes = ["Hair", "__0", "__2", "__4", "Center_lower_vermillion_lip", "Chin", "Glabella", "Left_bulbar_conjunctiva", "Left_cheek", "Left_dorsum", "Left_ear", "Left_eyebrow", "Left_forehead", "Left_lower_eyelid", "Left_lower_vermillion_lip", "Left_nasolabial_cheek", "Left_nostril", "Left_pupil", "Left_temple", "Left_upper_cutaneous_lip", "Left_upper_eyelid", "Left_upper_vermillion_lip", "Left_upper_vermillion_lip001", "Lower_teeth", "Mid_forehead", "Mid_nasal_dorsum", "Mid_upper_vermillion_lip", "Nasal_tip", "Neck", "Occipital_scalp", "Philtrum", "Right_bulbar_conjunctiva", "Right_cheek", "Right_dorsum", "Right_ear", "Right_eyebrow", "Right_forehead", "Right_lower_eyelid", "Right_lower_vermillion_lip", "Right_nasolabial_cheek", "Right_nostril", "Right_pupil", "Right_temple", "Right_upper_cutaneous_lip", "Right_upper_eyelid", "Right_upper_vermillion_lip", "Tongue", "Upper_teeth"]

    for prefix in def_prefixes:
        elements = find_elements_by_prefix(root, prefix)
        segment = xml.etree.ElementTree.Element('HAnimSegment')
        segment.text = "\n"
        segment.tail = "\n"
        segment.set('DEF', "hanim_"+prefix)
        segment.set('name', prefix.lower())
        skullbase.append(segment)
        for element in elements:
            par = find_parent(root, element)
            if element.tag == 'CoordinateInterpolator':
                comment = xml.etree.ElementTree.Comment(str(xml.etree.ElementTree.tostring(element))[2:-3])
                comment.tail = "\n"
                #segment.append(comment)
                par.remove(element)
                segment.append(element)
            elif not element.tag in ('IndexedFaceSet', 'Coordinate', 'TextureCoordinate'):
                par.remove(element)
                segment.append(element)
            elif element.tag == 'Coordinate':
                coordinate = xml.etree.ElementTree.Element('Coordinate')
                coordinate.set("USE", element.get("DEF"))
                coordinate.set("containerField", "coord")
                coordinate.text = "\n"
                coordinate.tail = "\n"
                segment.append(coordinate)
            elif element.tag == 'ScalarInterpolator':
                element.set("DEF", element.get("DEF")+"_"+findAnimation(file_output))
                
        # Move displacer to end
        for element in list(segment):
            if element.tag == "HAnimDisplacer":
                segment.remove(element)
                segment.append(element)

    # Remove the HAnimDisplacer from 'sacrum' after moving elements 
    for displacer in list(sacrum):
        if displacer.tag == "HAnimDisplacer":
            sacrum.remove(displacer)

    for view in root.iter('Viewpoint'):
            par = find_parent(root, view)
            scene.insert(0, view)
            par.remove(view)
#    sensor = xml.etree.ElementTree.Element('ProximitySensor')
#    sensor.text = "\n"
#    sensor.tail = "\n"
#    sensor.set("DEF", "MainSensor")
#    sensor.set("size", "1000000 1000000 1000000")
#    scene.append(sensor)

    for ts in root.iter('TimeSensor'):
        export = xml.etree.ElementTree.Element('EXPORT')
        export.text = "\n"
        export.tail = "\n"
        export.set("localDEF", ts.get("DEF"))
        export.set("AS", ts.get("DEF"))
        scene.append(export)
#        route = xml.etree.ElementTree.Element('ROUTE')
#        route.text = "\n"
#        route.tail = "\n"
#        route.set("fromNode", "MainSensor")
#        route.set("fromField", "enterTime")
#        route.set("toNode", ts.get("DEF"))
#        route.set("toField", "set_startTime")
#        scene.append(route)


    header = '<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE X3D PUBLIC "ISO//Web3D//DTD X3D 4.0//EN" "https://www.web3d.org/specifications/x3d-4.0.dtd">'
    xmlstr = xml.etree.ElementTree.tostring(root, encoding='unicode')
    xmlString = f"{header}{xmlstr}"
    with open(file_output, "w") as output_file:
        output_file.write(xmlString)

files = os.scandir("C:/Users/jcarl/Downloads/Jin_Facs_au_x3d_240219-20240909T023418Z-001/Jin_Facs_au_x3d_240219/")

def processAFile(input_file, menu_file, item_number):
    output_file = os.path.basename(input_file)
    output_file = output_file.replace("FACS_AU", "").replace("(", "").replace(")", "").replace("_", "").replace("Morpher", "")
    if output_file[1:2] == "J":
        output_file = "0"+output_file
    output_file = output_file[2:]
    if output_file.endswith(".x3d"):
        output_file = output_file[:-4]+".x3d"
        output_file = os.path.join("../resources/",os.path.basename(output_file))
        print(f"Output file is {output_file}")
        try:
            process_file(input_file, output_file)
            menu_file.write("<Inline DEF=\"OPTION"+str(item_number)+"\" url='\""+output_file+"\" \""+(output_file.replace("../resources/", ""))+"\"'/>\n")
        except xml.etree.ElementTree.ParseError:
            print(f"The file {output_file} has a parse error")
    return output_file

with open("../resources/Menu.x3d", "w") as menu_file:
    menu_file.write('''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE X3D PUBLIC "ISO//Web3D//DTD X3D 4.0//EN" "https://www.web3d.org/specifications/x3d-4.0.dtd"><X3D xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" profile="Immersive" version="4.0" xsi:noNamespaceSchemaLocation="http://www.web3d.org/specifications/x3d-4.0.xsd">
  <head>
    <meta content="Menu.x3d" name="title"/>
    <meta content="X3D scene with a Switch of Inlines controlled by a menu" name="description"/>
  </head>
  <Scene>
    <!-- Viewpoint and any other scene setup -->
    <Viewpoint position="0 20 110" />

    <!-- Menu prototype declaration -->
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
                <Coordinate point='25 36 -0.01, -25 36 -0.01, -25 -51 -0.01, 25 -51 -0.01'/>
             </IndexedFaceSet>
          </Shape>
        </Transform>

      <Switch DEF="SceneSwitcher" whichChoice="0">\n''')
    item = 1
    menu = ""
    for input_file in files:
        if input_file.name.endswith(".x3d"):
            output_file = processAFile(input_file, menu_file, item)
            item += 1
            menu += '"'+output_file.replace("../resources/", "")+'" '

    menu_file.write('''</Switch>

    <!-- Script to handle selection logic -->
    <Script DEF="MenuScript">
      <field name="menuItems" type="MFString" accessType="initializeOnly"/>
      <field name="selection" type="SFInt32" accessType="outputOnly"/>
      <field name="touchPoint" type="SFVec3f" accessType="inputOnly"/>
      <field name="spacing" type="SFFloat" accessType="initializeOnly" value="1.2"/>
      <field name="size" type="SFFloat" accessType="initializeOnly" value="2.4"/>
      <field name="menuCenterY" type="SFFloat" accessType="initializeOnly"/>
      <field name="itemHeight" type="SFFloat" accessType="initializeOnly"/>

      <![CDATA[ecmascript:
        function initialize() {
          selection = 0;
          var spacingBetweenGlyphs = size * spacing - size; // Spacing calculation
          var menuHeight = (size + spacingBetweenGlyphs) * menuItems.length;
          menuCenterY = menuHeight / 2;
          itemHeight = menuHeight / menuItems.length;
        }

        function touchPoint(value) {
          Browser.print("Hit "+value+" "+selection+"\\n");
          var index = Math.floor((menuCenterY - value.y) / itemHeight - 0.5);

          selection = index - 2;
          if (selection >= 0 && selection < menuItems.length) {
            Browser.print("Selected "+value+" "+selection+" "+menuItems[selection]+"\\n");
          }
        }
      ]]>
      <IS>
         <connect nodeField="menuItems" protoField="menuItems"/>
      </IS>
    </Script>

     <!-- ROUTEs to connect everything -->
     <ROUTE fromNode="MenuTouchSensor"   fromField="hitPoint_changed" toNode="MenuScript" toField="touchPoint"/>
     <ROUTE fromNode="MenuScript" fromField="selection" toNode="SceneSwitcher" toField="whichChoice"/>
      </Group>
      </ProtoBody>
    </ProtoDeclare>
    <ProtoInstance DEF='MainMenu' name='Menu'>
      <fieldValue name='menuItems' value=\''''+menu+'''\'/>
    </ProtoInstance>
  </Scene>
</X3D>
''')

#processAFile("C:/Users/jcarl/Downloads/Jin_Facs_au_x3d_240219-20240909T023418Z-001/Jin_Facs_au_x3d_240219/FACS_AU9(Jin)_Nose_Wrinkler_Morpher.x3d")
#processAFile("../resources/FACS47.x3d")


