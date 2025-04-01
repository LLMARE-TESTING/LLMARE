import xml.etree.ElementTree as ET
import re

class Node:
    def __init__(self):
        self.classname = ''
        self.text = ''
        self.resource_id = ''
        self.content_desc = ''
        self.bounds = ''
        self.clickable = ''
        self.html = ''

activities = []  # 程序的所有活动
widgets_op = []  # 可以进行操作的widgets


# 将xml viewtree转换为html格式，viewtree_path为页面状态xml文件的路径
def traverse_xml(viewtree_path):
    tree = ET.parse(viewtree_path)
    root = tree.getroot()
    results = ''
    id = 0

    for node in root.findall('.//node'):
        result = ''
        if 'ImageView' in node.get('class'):
            node_type = 'img'
        elif 'Button' in node.get('class') or node.get('clickable') == "true" or "按钮" in node.get('text') or "按钮" in node.get('content-desc'):
            node_type = 'button'
        elif 'EditText' in node.get('class'):
            node_type = 'input'
        elif 'TextView' in node.get('class'):
            node_type = 'p'
        else:
            node_type = 'div'
        #if node.is_leaf and node.visible:
        #if len(list(node)) == 0:
        html_close_tag = node_type
        if node.get('resource-id') != '' or node.get('content-desc') != '' or node.get('text') != '':
            result = '<{}{}{}{}> {} </{}>\n'.format(
                node_type,
                ' id={}'.format(id),
                ' class="{}"'.format(' '.join(node.get('resource-id')))
                if node.get('resource-id')
                else '',
                ' alt="{}"'.format(node.get('content-desc')) if node.get('content-desc') else '',
                '{}, '.format(node.get('text')) if node.get('text') else '',
                html_close_tag,
            )
            id = id + 1
            results += result

    return results


# 将通过Appium获取的pagesource转换为html格式
# 参数source为driver.pagesource的内容，格式为字符串；
# 参数p为1时输出结果包括TextView和ImageView组件，为0时不包括。
def traverse_html(source,p):
    # p==1 代表处理textview元素
    #tree = ET.parse(viewtree_path)
    #root = tree.getroot()
    results = ''
    id = 0
    id_to_coordinate = {}

    for element in re.findall(r"\<android.*\>", source):
        # 处理元素
        node = Node()
        node.text = re.findall(r'text=\"(.*?)\"',element)[0]
        node.classname = re.findall(r'class=\"(.*?)\"', element)[0] if len(re.findall(r'class=\"(.*?)\"', element)) else ''
        node.resource_id = re.findall(r'resource-id=\"(.*?)\"', element)[0] if len(re.findall(r'resource-id=\"(.*?)\"', element)) else ''
        node.clickable = re.findall(r'clickable=\"(.*?)\"', element)[0] if len(re.findall(r'clickable=\"(.*?)\"', element)) else ''
        node.bounds = re.findall(r'bounds=\"(.*?)\"', element)[0] if len(re.findall(r'bounds=\"(.*?)\"', element)) else ''
        node.content_desc = re.findall(r'content-desc=\"(.*?)\"', element)[0] if len(re.findall(r'content-desc=\"(.*?)\"', element)) else ''

        result = ''
        node_type = ''
        #if 'ImageView' in node.get('class'):
        #    node_type = 'img'
        if p == 1:
            if 'EditText' in node.classname:
                node_type = 'input'
            elif 'ImageView' in node.classname:
                node_type = 'img'
            elif 'Button' in node.classname or node.clickable == "true" or "按钮" in node.text or "按钮" in node.content_desc:
                node_type = 'button'
            elif 'TextView' in node.classname:
                node_type = 'p'
            else:
                node_type = 'div'
        if p == 0:
            if 'EditText' in node.classname:
                node_type = 'input'
            elif 'Button' in node.classname or node.clickable == "true" or "按钮" in node.text or "按钮" in node.content_desc:
                node_type = 'button'
        #elif node.get('scrollable') == "true":
        #    node_type = 'scroll'
        #else:
            #node_type = 'div'
        #html_close_tag = node_type
        if len(node_type):
            id_to_coordinate[id] = node
            html_close_tag = node_type

            if node.text != '' or node.content_desc != '' or node.resource_id != '':
                result = '<{}{}{}{}> {} </{}>\n'.format(
                    node_type,
                    ' id={}'.format(id),
                    ' class ="{}"'.format(node.resource_id) if node.resource_id else '',
                    ' alt="{}"'.format(node.content_desc) if (node.content_desc and node.content_desc != node.text) else '',
                    '{}, '.format(node.text) if node.text else '',
                    html_close_tag,
                )
                id = id + 1
                results += result
                node.html = result[:-1]
    for element in re.findall(r"\<com.*\>", source):
        # 处理元素
        node = Node()
        node.text = re.findall(r'text=\"(.*?)\"',element)[0]
        node.classname = re.findall(r'class=\"(.*?)\"', element)[0] if len(re.findall(r'class=\"(.*?)\"', element)) else ''
        node.resource_id = re.findall(r'resource-id=\"(.*?)\"', element)[0] if len(re.findall(r'resource-id=\"(.*?)\"', element)) else ''
        node.clickable = re.findall(r'clickable=\"(.*?)\"', element)[0] if len(re.findall(r'clickable=\"(.*?)\"', element)) else ''
        node.bounds = re.findall(r'bounds=\"(.*?)\"', element)[0] if len(re.findall(r'bounds=\"(.*?)\"', element)) else ''
        node.content_desc = re.findall(r'content-desc=\"(.*?)\"', element)[0] if len(re.findall(r'content-desc=\"(.*?)\"', element)) else ''

        result = ''
        node_type = ''
        #if 'ImageView' in node.get('class'):
        #    node_type = 'img'
        if p == 1:
            if 'EditText' in node.classname:
                node_type = 'input'
            elif 'ImageView' in node.classname:
                node_type = 'img'
            elif "按钮" in node.text or "按钮" in node.content_desc:
                node_type = 'button'
            elif 'UIView' in node.classname or 'UI':
                node_type = 'p'
            else:
                node_type = 'div'
        if p == 0:
            if 'EditText' in node.classname:
                node_type = 'input'
            elif "按钮" in node.text or "按钮" in node.content_desc:
                node_type = 'button'
        #elif node.get('scrollable') == "true":
        #    node_type = 'scroll'
        #else:
            #node_type = 'div'
        #html_close_tag = node_type
        if len(node_type):
            id_to_coordinate[id] = node
            html_close_tag = node_type

            if node.text != '' or node.content_desc != '' or node.resource_id != '':
                result = '<{}{}{}{}> {} </{}>\n'.format(
                    node_type,
                    ' id={}'.format(id),
                    ' class ="{}"'.format(node.resource_id) if node.resource_id else '',
                    ' alt="{}"'.format(node.content_desc) if (node.content_desc and node.content_desc != node.text) else '',
                    '{}, '.format(node.text) if node.text else '',
                    html_close_tag,
                )
                id = id + 1
                node.html = result[:-1]
                results += result

    return results,id_to_coordinate
