import xml.etree.ElementTree
import os

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
        if def_value and def_value.startswith(prefix):
            matched_elements.append(elem)
    return matched_elements

def process_file(file_input, file_output):
    X3D = xml.etree.ElementTree.parse(file_input)
    root = X3D.getroot()
    head = root.find('head')
    scene = root.find('Scene')
    component = xml.etree.ElementTree.Element('component')
    component.set("name", "HAnim")
    component.set("level", "3")
    component.text = "\n"
    component.tail = "\n"
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
    sacrum.set('DEF', "sacrum")
    humanoid_root.insert(0, sacrum)

    skullbase = xml.etree.ElementTree.Element('HAnimJoint')
    skullbase.set("DEF", "skullbase")
    skullbase.text = "\n"
    skullbase.tail = "\n"
    humanoid_root.append(skullbase)

    skullbase_use = xml.etree.ElementTree.Element('HAnimJoint')
    skullbase_use.set("USE", "skullbase")
    skullbase_use.set("containerField", "joints")
    skullbase_use.text = "\n"
    skullbase_use.tail = "\n"
    humanoid.append(skullbase_use)

    for it in root.iter('ImageTexture'):
        it.set("url", "\""+it.get("url")+"\"")
    for cis in root.iter('CoordinateInterpolator'):
        DEF = cis.get("DEF")
        # print(DEF)
        keys = cis.get("key").split()
        keyValues = cis.get("keyValue").split()

        numKeys = len(keys)
        valuesPerKey = int(len(keyValues)/numKeys)
        # print(keys)
        # print(keyValues)
        key = 0
        base = keyValues[valuesPerKey*key:valuesPerKey*(key+1)]
        key = numKeys - 1
        extension = keyValues[valuesPerKey*key:valuesPerKey*(key+1)]
        # print(base)
        # print(extension)

        new_node = xml.etree.ElementTree.Element('HAnimDisplacer')
        new_node.text = "\n"
        new_node.tail = "\n"
        displacements = []
        for i in range(len(base)):
            displacements.append(str(float(extension[i]) - float(base[i])))
        # print(displacements)
        parent = find_parent(root, cis)
        new_node.set("displacements", " ".join(displacements))
        new_node.set("DEF", DEF)

        if parent is not None:
            index = get_node_index(parent, cis)
            if index is not None:
                # Add the HAnimDisplacer to the 'sacrum' segment
                sacrum.append(new_node)

                # Replace set_fraction with weight
                routes = root.findall(".//ROUTE[@toField='set_fraction'][@toNode='"+DEF+"']")
                for route in routes:
                    route.set("toField", "weight")

                # Replace value_changed with weight
                routes = root.findall(".//ROUTE[@fromField='value_changed'][@fromNode='"+DEF+"']")
                for route in routes:
                    # route.set("fromField", "weight")
                    # Set coordIndex of the new HAnimDisplacer node.
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
                            for i, point in enumerate(pointsMatrix): # Loop through Coordinate points
                                for j, base_point in enumerate(baseMatrix):
                                    if point == base_point:
                                        coordIndex.append(str(i))
                                        # break # Assume a base point only maps to one point
                            new_node.set("coordIndex", " ".join(coordIndex))
                    # Remove the unnecessary ROUTE
                    # TODO
                    par = find_parent(root, route)
                    par.remove(route)

                # Remove the CoordinateInterpolator
                # parent.remove(cis)

    # Move other elements into the 'sacrum' segment
    for element in list(scene):
        if not element.tag in ("HAnimHumanoid", "HAnimJoint", "HAnimSegment", "HAnimDisplacer") and element.tag != "ROUTE":
            sacrum.append(element)
            scene.remove(element)
        elif element.tag == 'ROUTE':
            scene.remove(element)
            scene.append(element)

    def_prefixes = ["Hair", "__0", "__2", "__4", "Center_lower_vermillion_lip", "Chin", "Glabella", "Left_bulbar_conjunctiva", "Left_cheek", "Left_dorsum", "Left_ear", "Left_eyebrow", "Left_forehead", "Left_lower_eyelid", "Left_lower_vermillion_lip", "Left_nasolabial_cheek", "Left_nostril", "Left_pupil", "Left_temple", "Left_upper_cutaneous_lip", "Left_upper_eyelid", "Left_upper_vermillion_lip", "Left_upper_vermillion_lip001", "Lower_teeth", "Mid_forehead", "Mid_nasal_dorsum", "Mid_upper_vermillion_lip", "Nasal_tip", "Neck", "Occipital_scalp", "Philtrum", "Right_bulbar_conjunctiva", "Right_cheek", "Right_dorsum", "Right_ear", "Right_eyebrow", "Right_forehead", "Right_lower_eyelid", "Right_lower_vermillion_lip", "Right_nasolabial_cheek", "Right_nostril", "Right_pupil", "Right_temple", "Right_upper_cutaneous_lip", "Right_upper_eyelid", "Right_upper_vermillion_lip", "Tongue", "Upper_teeth"]

    for prefix in def_prefixes:
        elements = find_elements_by_prefix(root, prefix)
        segment = xml.etree.ElementTree.Element('HAnimSegment')
        segment.text = "\n"
        segment.tail = "\n"
        segment.set('DEF', prefix+"_segment")
        skullbase.append(segment)
        for element in elements:
            par = find_parent(root, element)
            if element.tag == 'CoordinateInterpolator':
                par.remove(element)
                comment = xml.etree.ElementTree.Comment(xml.etree.ElementTree.tostring(element))
                segment.append(comment)
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

    # Remove the HAnimDisplacer from 'sacrum' after moving elements 
    for displacer in list(sacrum):
        if displacer.tag == "HAnimDisplacer":
            sacrum.remove(displacer)

    mainClock = xml.etree.ElementTree.Element('TimeSensor')
    mainClock.text = "\n"
    mainClock.tail = "\n"
    mainClock.set("DEF", "MainClock")
    mainClock.set("cycleInterval", "10")
    mainClock.set("enabled", "true")
    scene.append(mainClock)

    sensor = xml.etree.ElementTree.Element('ProximitySensor')
    sensor.text = "\n"
    sensor.tail = "\n"
    sensor.set("DEF", "MainSensor")
    sensor.set("size", "1000000 1000000 1000000")
    scene.append(sensor)

    sensorToClock = xml.etree.ElementTree.Element('ROUTE')
    sensorToClock.text = "\n"
    sensorToClock.tail = "\n"
    sensorToClock.set("fromNode", "MainSensor")
    sensorToClock.set("fromField", "enterTime")
    sensorToClock.set("toNode", "MainClock")
    sensorToClock.set("toField", "set_startTime")
    scene.append(sensorToClock)

    for ts in root.iter('TimeSensor'):
        route = xml.etree.ElementTree.Element('ROUTE')
        route.text = "\n"
        route.tail = "\n"
        route.set("fromNode", "MainClock")
        route.set("fromField", "startTime")
        route.set("toNode", ts.get("DEF"))
        route.set("toField", "set_startTime")
        scene.append(route)

    X3D.write(file_output)

files = os.scandir("C:/Users/jcarl/Downloads/Jin_Facs_au_x3d_240219-20240909T023418Z-001/Jin_Facs_au_x3d_240219/")

for input_file in files:
    output_file = os.path.join("../resources/",os.path.basename(input_file))
    if output_file.endswith(".x3d"):
        output_file = output_file[:-4]+"_Output.x3d"
        try:
            process_file(input_file, output_file)
        except xml.etree.ElementTree.ParseError:
            print(f"The file {output_file} has a parse error")
