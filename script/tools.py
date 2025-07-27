import xml.etree.ElementTree as ET
import re
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import hashlib
from copy import deepcopy
from collections import Counter
import os
import subprocess
os.environ.setdefault("OPENAI_API_KEY", "sk-NEI39Ft0cx0sezU8914aE7D447114662817cC404106984Ea")
os.environ.setdefault("OPENAI_BASE_URL", "https://oneapi.xty.app/v1")
class Node:
    def __init__(self):
        self.classname = ''
        self.text = ''
        self.resource_id = ''
        self.content_desc = ''
        self.bounds = ''
        self.clickable = ''
        self.html = ''

class Widget:
    def __init__(self):
        self.resource_id = ''
        self.classname = ''
        self.width = 0   # 组件的大小
        self.height = 0
        self.actions = []  # 当前组件可以执行的操作

activities = []  # 程序的所有活动
widgets_op = []  # 可以进行操作的widgets
def traverse_xml(viewtree_path):
    tree = ET.parse(viewtree_path)
    root = tree.getroot()
    results = ''
    id = 0

    for node in root.findall('.//node'):
        result = ''
        if 'ImageView' in node.get('class'):
            node_type = 'img'
        elif 'Button' in node.get('class') or node.get('clickable') == "true":
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
            # if node.get('resource-id') != '':
            #     resource_id = node.get('resource-id')
            result = '<{}{}{}{}> {} </{}>\n'.format(
                node_type,
                ' id={}'.format(id),
                ' class="{}"'.format(node.get('resource-id')) if node.get('resource-id') else '',
                ' alt="{}"'.format(node.get('content-desc')) if node.get('content-desc') else '',
                '{}, '.format(node.get('text')) if node.get('text') else '',
                html_close_tag,
            )
            id = id + 1
            results += result

    return results

def traverse_json(viewtree_path):
    with open(viewtree_path,'r') as file:
        data = (json.load(file))["views"]
    results = ''
    id = 0
    for node in data:
        result = ''
        if 'ImageView' in node["class"]:
            node_type = 'img'
        elif 'Button' in node["class"] or node["clickable"] == "true":
            node_type = 'button'
        #elif node["text"]"按钮" in node["text"] or "按钮" in node["content_desc"]:
            #node_type = 'button'
        elif 'EditText' in node["class"]:
            node_type = 'input'
        elif 'TextView' in node["class"]:
            node_type = 'p'
        else:
            node_type = 'div'
        #if node.is_leaf and node.visible:
        #if len(list(node)) == 0:
        html_close_tag = node_type
        if node["resource_id"] != None or node["content_description"] != None or node["text"] != None:
            if node["resource_id"] != None and 'com.lemon.lvoverseas:id' in node["resource_id"]:
                node["resource_id"] = node["resource_id"][24:]
            result = '<{}{}{}{}> {} </{}>\n'.format(
                node_type,
                ' id={}'.format(id),
                ' class="{}"'.format(' '.join(node["resource_id"]))
                if node["resource_id"]
                else '',
                ' alt="{}"'.format(node["content_description"]) if node["content_description"] else '',
                '{}, '.format(node["text"]) if node["text"] else '',
                html_close_tag,
            )
            id = id + 1
            results += result
        '''
        else:
            children_results = ''
            for child in node:
                id = id + 1
                re = traverse_xml(child,id)
                if re:
                    children_results += re
                results += children_results
        '''
    return results
def coordinate_max(viewtree_path):
    file = open(viewtree_path, 'r', encoding='utf-8')
    str = file.read()
    coordinate_max = re.findall(r'\[0,0\]\[(\d+),(\d+)\]', str)
    if len(coordinate_max) != 0:
        x_max = int(coordinate_max[0][0])
        y_max = int(coordinate_max[0][1])
    file.close()
    return x_max,y_max

def tap_coordinate(widget_coordinate):
    matches = re.findall(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]', widget_coordinate)
    a = int((int(matches[0][0]) + int(matches[0][2])) / 2)
    b = int((int(matches[0][1]) + int(matches[0][3])) / 2)
    # 确定组件的相对坐标
    return a,b

def page(source,page_num,p):
    page_name = 'GUI\\' + str(page_num) + '.xml'
    f = open(page_name, 'w', encoding='utf-8')
    f.write(source)
    f.close()
    message, coordinate = traverse_html(source,p)
    print(message)
    #x_max, y_max = coordinate_max(page_name)
    x_max = 1080
    y_max = 2280
    return message,coordinate,x_max,y_max

def traverse_html(source,p):
    # p==1 代表处理textview元素
    #tree = ET.parse(viewtree_path)
    #root = tree.getroot()
    results = ''
    id = 0
    id_to_coordinate = {}
    nodes = []

    for element in re.findall(r"\<android.*\>", source):
        # 筛选掉visiable为false（不可见）的组件
        #if re.findall(r'visiable=\"(.*?)\"',element)[0] == 'false':
        #    continue
        # 处理元素
        node = Node()
        node.text = re.findall(r'text=\"(.*?)\"',element)[0] if re.findall(r'text=\"(.*?)\"',element) else ''
        node.classname = re.findall(r'class=\"(.*?)\"', element)[0] if len(re.findall(r'class=\"(.*?)\"', element)) else ''
        node.resource_id = re.findall(r'resource-id=\"(.*?)\"', element)[0] if len(re.findall(r'resource-id=\"(.*?)\"', element)) else ''
        node.clickable = re.findall(r'clickable=\"(.*?)\"', element)[0] if len(re.findall(r'clickable=\"(.*?)\"', element)) else ''
        node.bounds = re.findall(r'bounds=\"(.*?)\"', element)[0] if len(re.findall(r'bounds=\"(.*?)\"', element)) else ''
        node.content_desc = re.findall(r'content-desc=\"(.*?)\"', element)[0] if len(re.findall(r'content-desc=\"(.*?)\"', element)) else ''
        flag = 0
        for n in nodes:
            if n.text == node.text and n.classname == node.classname and n.content_desc == node.content_desc:
                flag = 1
                break
        if flag == 0:
            nodes.append(deepcopy(node))
        else:
            continue

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
            '''
            if node.resource_id != '':
                result = '<{}{}{}> </{}>\n'.format(
                    node_type,
                    ' id={}'.format(id),
                    ' class="{}"'.format(' '.join(node.resource_id))
                    if node.resource_id
                    else '',
                    html_close_tag,
                )
                id = id + 1
                results += result
            '''
            if 'com.zhiliaoapp.musically' in node.resource_id:
                node.resource_id = ''
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
        node.text = re.findall(r'text=\"(.*?)\"',element)[0] if re.findall(r'text=\"(.*?)\"',element) else ''
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
            '''
            if node.resource_id != '':
                result = '<{}{}{}> </{}>\n'.format(
                    node_type,
                    ' id={}'.format(id),
                    ' class="{}"'.format(' '.join(node.resource_id))
                    if node.resource_id
                    else '',
                    html_close_tag,
                )
                id = id + 1
                results += result
            '''
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

def get_activity_names(manifest_file):
    activity_names = []
    tree = ET.parse(manifest_file)
    root = tree.getroot()

    # 定义 Android 的命名空间
    ns = {'android': 'http://schemas.android.com/apk/res/android'}

    # 查找所有的 activity 元素
    for activity in root.findall('.//activity'):
        # 获取 activity 的名称属性值
        activity_name = activity.get('{http://schemas.android.com/apk/res/android}name')
        # 将 activity 名称添加到列表中
        activity_names.append(activity_name)
    for activity in activity_names:
        print(activity)
    return activity_names

def tap_coordinate(widget_coordinate):
    matches = re.findall(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]', widget_coordinate)
    a = int((int(matches[0][0]) + int(matches[0][2])) / 2)
    b = int((int(matches[0][1]) + int(matches[0][3])) / 2)
    # 确定组件的相对坐标
    return a,b


def find_all_paths(graph, start, end, path=[]):
    path = path + [start]
    if start == end:
        return [path]
    if start not in graph:
        return []
    paths = []
    for node in graph[start]:
        if node not in path:
            new_paths = find_all_paths(graph, node, end, path)
            for new_path in new_paths:
                paths.append(new_path)
    return paths



def text_similarity(text1, text2):
    text1 = text1.replace(" ", "")
    text2 = text2.replace(" ", "")
    # 使用TF-IDF向量化文本
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([text1, text2])

    # 计算余弦相似度
    cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix)[0][1]

    return cosine_sim

def widget_width_height(bounds):
    matches = re.findall(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]', bounds)
    width = int(matches[0][2]) - int(matches[0][0])
    height = int(matches[0][3]) - int(matches[0][1])
    return width,height

# 获取页面的组件信息
def xml_widgets(viewtree_path, flag=0):
    tree = ET.parse(viewtree_path)
    root = tree.getroot()
    widgets = []

    for node in root.findall('.//node'):
        w = Widget()
        w.classname = node.get('class')
        w.resource_id = node.get('resource-id')
        bounds = node.get('bounds')
        w.width, w.height = widget_width_height(bounds)
        if 'Button' in node.get('class') or node.get('clickable') == "true":
            w.actions.append(1)
        else:
            w.actions.append(0)

        if node.get('long-clickable') == 'true':
            w.actions.append(1)
        else:
            w.actions.append(0)

        if 'EditText' in node.get('class'):
            w.actions.append(1)
        else:
            w.actions.append(0)

        if node.get('scrollable') == 'true':
            w.actions.append(1)
        else:
            w.actions.append(0)

        if w.actions.count(1) > 0 :
            if flag == 0:
                widget = {'class': w.classname, 'resource-id': w.resource_id, 'actions': w.actions}
            else:
                widget = {'class': w.classname, 'resource-id': w.resource_id, 'actions': w.actions, 'width':w.width, 'height':w.height}
            widgets.append(widget)
    return widgets


def json_widgets(viewtree_path, flag=0):
    with open(viewtree_path, 'r') as file:
        data = (json.load(file))["views"]
    widgets = []
    for node in data:
        w = Widget()
        w.classname = node["class"]
        w.resource_id = node["resource_id"]
        bounds = node["bounds"]
        #w.width, w.height = widget_width_height(bounds)
        w.width = bounds[1][0] - bounds[0][0]
        w.height = bounds[1][1] - bounds[0][1]
        if 'Button' in node["class"] or node['clickable'] == "true":
            w.actions.append(1)
        else:
            w.actions.append(0)

        if node['long_clickable'] == 'true':
            w.actions.append(1)
        else:
            w.actions.append(0)

        if 'EditText' in node['class']:
            w.actions.append(1)
        else:
            w.actions.append(0)

        if node['scrollable'] == 'true':
            w.actions.append(1)
        else:
            w.actions.append(0)

        if w.actions.count(1) > 0:
            if flag == 0:
                widget = {'class': w.classname, 'resource-id': w.resource_id, 'actions': w.actions}
            else:
                widget = {'class': w.classname, 'resource-id': w.resource_id, 'actions': w.actions, 'width':w.width,'height':w.height}
            widgets.append(widget)

    return widgets

def source_widgets(source,flag=0):
    widgets = []
    for element in re.findall(r"\<android.*\>", source):
        # 处理元素
        w = Widget()
        w.classname = re.findall(r'class=\"(.*?)\"', element)[0] if len(re.findall(r'class=\"(.*?)\"', element)) else ''
        w.resource_id = re.findall(r'resource-id=\"(.*?)\"', element)[0] if len(re.findall(r'resource-id=\"(.*?)\"', element)) else ''
        bounds = re.findall(r'bounds=\"(.*?)\"', element)[0] if len(re.findall(r'bounds=\"(.*?)\"', element)) else ''
        w.width, w.height = widget_width_height(bounds)
        if 'Button' in w.classname or re.findall(r'clickable=\"(.*?)\"', element)[0] == "true":
            w.actions.append(1)
        else:
            w.actions.append(0)

        if re.findall(r'long-clickable=\"(.*?)\"', element)[0] == 'true':
            w.actions.append(1)
        else:
            w.actions.append(0)

        if 'EditText' in w.classname:
            w.actions.append(1)
        else:
            w.actions.append(0)

        if re.findall(r'scrollable=\"(.*?)\"', element)[0] == 'true':
            w.actions.append(1)
        else:
            w.actions.append(0)
        if w.actions.count(1) > 0:
            if flag == 0:
                widget = {'class': w.classname, 'resource-id': w.resource_id, 'actions': w.actions}
            else:
                widget = {'class': w.classname, 'resource-id': w.resource_id,'actions': w.actions, 'width': w.width, 'height': w.height}
            widgets.append(widget)
    return widgets


def dict_hash(dictionary):
    # 将词典转换为排序后的JSON字符串
    dict_str = json.dumps(dictionary, sort_keys=True)

    # 将JSON字符串转换为字节
    dict_bytes = dict_str.encode('utf-8')

    # 计算哈希值
    hash_object = hashlib.md5(dict_bytes)  # 你也可以使用其他哈希函数，如 hashlib.sha256
    hash_hex = hash_object.hexdigest()

    return hash_hex


# 根据state的组件信息计算相似度
def state_similarity(state1,state2):
    hash1 = []  # state1的hash数组
    hash2 = []  # state2的hash数组
    for widget in state1:
        new_hash = dict_hash(widget)  # 比较时去除重复的组件
        if hash1.count(new_hash) == 0:
            hash1.append(new_hash)
    for widget in state2:
        new_hash = dict_hash(widget)  # 比较时去除重复的组件
        if hash2.count(new_hash) == 0:
            hash2.append(new_hash)

    # 比较状态的相似度
    # 统计每个列表中元素的出现次数
    counter1 = Counter(hash1)
    counter2 = Counter(hash2)

    # 计算每个元素在两个列表中的最小出现次数
    common_count = sum((counter1 & counter2).values())
    if len(hash1) > 0  and len(hash2) > 0 :
        similarity = (common_count/len(hash1) + common_count/len(hash2))/2
        return similarity
    else :
        return 0



# 获取当前的屏幕截图，返回屏幕截图保存的文件路径
def get_screenshot(file_path):
    try:
        os.system('adb shell screencap -p /sdcard/test' + '.png')
        os.system('adb pull /sdcard/test.png ' + file_path)
        return file_path
    except:
        return None


def get_activity():
    try:
        # 运行 adb 命令获取当前窗口的包名和 Activity
        result = subprocess.run(['adb', 'shell', 'dumpsys', 'window'], capture_output=True, text=True)
        #result = os.system('adb shell dumpsys window | findstr mCurrentFocus')
        output = result.stdout

        # 在输出中查找当前 Activity 信息
        for line in output.splitlines():
            if 'mCurrentFocus' in line or 'mFocusedApp' in line:
                current_activity = line.strip().split()[-1]
                match = re.match('(.+?)/',current_activity).end()
                current_activity = current_activity[match:]
                return current_activity
        #print('None')
        return ''

    except Exception as e:
        print(f"Error: {e}")
        return ''


from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from langchain_openai import OpenAIEmbeddings
import openai


def calculate_cosine_similarity(reference_sentence, sentences):
    # 将参考语句和其他语句组成一个新的列表
    all_sentences = [reference_sentence] + sentences

    # 使用 TfidfVectorizer 将文本转换为TF-IDF特征向量
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(all_sentences)

    # 计算参考语句与其他语句的余弦相似度
    cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

    # 将句子和相似度组合在一起，并按相似度排序
    sorted_sentences_with_scores = sorted(zip(sentences, cosine_similarities), key=lambda x: x[1], reverse=True)

    return sorted_sentences_with_scores

from transformers import BertModel, BertTokenizer
import torch

'''
def get_embedding(text, model, tokenizer):
    # 初始化分词器和模型
    #tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    #model = BertModel.from_pretrained('bert-base-uncased')
    # 编码文本
    encoded_input = tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=128)
    # 使用BERT模型
    with torch.no_grad():  # 不计算梯度
        output = model(**encoded_input)
    # 获取最后一层的隐藏状态
    hidden_states = output.last_hidden_state
    # 求平均获取句子级别的表示
    sentence_embedding = torch.mean(hidden_states, dim=1).squeeze()

    return sentence_embedding.numpy()
'''


# 定义获取文本嵌入的函数
def get_embedding(text, model, tokenizer):
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
    outputs = model(**inputs)
    cls_embedding = outputs.last_hidden_state[:, 0, :]
    return cls_embedding.detach().numpy()

# 定义计算相似度的函数
def calculate_similarity(text1, text2, model, tokenizer):
    embedding1 = get_embedding(text1, model, tokenizer)
    embedding2 = get_embedding(text2, model, tokenizer)
    #embedding1 = openai.Embedding.create(model="text-embedding-ada-002", document=text1)['data'][0]['embedding']
    #embedding2 = openai.Embedding.create(model="text-embedding-ada-002", document=text2)['data'][0]['embedding']
    similarity = cosine_similarity(embedding1, embedding2)[0][0]
    return similarity



#sorted_sentences = calculate_cosine_similarity(reference_sentence, sentences)


if __name__ == '__main__':
    # 示例状态列表
    states = ["state1", "state2", "state3"]
    comment = "This is a sample comment."
    key_sentence = "This is a key sentence."

