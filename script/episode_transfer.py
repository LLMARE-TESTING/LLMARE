import llm4mobile.common as cm
import xml.etree.ElementTree as ET
from llm4mobile import episode_pb2
import re

screen_node_list = []
object_list = []
timestep_list = []

viewtree_path = "F:\\project\\UI\\png_viewtree_weather\\.MainActivity.xml"
tree = ET.parse(viewtree_path)
root = tree.getroot()
#id = 0
index = 0

for node in root.findall('.//node'):
    screen_node_list.append(node)
    # DomPosition = episode_pb2.DomPosition()
    BoundingBox = episode_pb2.BoundingBox()
    bounds = node.get('bounds')
    it = re.findall(r"\d+",bounds)
    BoundingBox.left = int(it[0])
    BoundingBox.top = int(it[1])
    BoundingBox.right = int(it[2])
    BoundingBox.bottom = int(it[3])

    object = episode_pb2.Object()
    object.index = screen_node_list.index(node)
    #if node.getparent() is not None:
    #    parent_node = node.getparent()   # 父节点index
    #    object.parent_index = screen_node_list.index(parent_node)
    #else:
    #    object.parent_index = -1
    object.android_class = node.get('class')
    object.android_package = node.get('package')
    object.text = node.get('text')
    object.resource_id = node.get('resource-id')
    object.content_desc = node.get('content-desc')
    if node.get('clickable') == 'true':
        object.clickable = True
    else:
        object.clickable = False
    if node.get('enabled') == 'true':
        object.enabled = True
    else:
        object.enabled = False
    if node.get('focusable') == 'true':
        object.focusable = True
    else:
        object.focusable = False
    if node.get('focused') == 'true':
        object.focused = True
    else:
        object.focused = False
    if node.get('scrollable') == 'true':
        object.scrollable = True
    else:
        object.scrollable = False
    if node.get('long_clickable') == 'true':
        object.long_clickable = True
    else:
        object.long_clickable = False
    if node.get('selected') == 'true':
        object.selected = True
    else:
        object.selected = False
    if node.get('checkable') == 'true':
        object.checkable = True
    else:
        object.checkable = False
    if node.get('checked') == 'true':
        object.checked = True
    else:
        object.checked = False
    if len(list(node)) == 0 :
        object.is_leaf = True
    else :
        object.is_leaf = False
    object_list.append(object)



Observation = episode_pb2.Observation()
Observation.objects.extend(object_list)
Observation.debug_vh_filepath = viewtree_path
timestep = episode_pb2.TimeStep()
timestep.observation.CopyFrom(Observation)
timestep_list.append(timestep)

episode = episode_pb2.Episode()
episode.time_steps.extend(timestep_list)

result = cm.parse_episode_proto(episode.SerializeToString())
print(result[0])
