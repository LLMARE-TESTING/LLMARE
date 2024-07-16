import json
import sys

from gpt.gpt import ask_gpt, ask_gpt_4, ask_gpt_state, ask_gpt_info, ask_gpt_activity,ask_gpt4
import re
import tools
from appium import webdriver
from appium.options.android import UiAutomator2Options
import time
from appium.webdriver.common.appiumby import AppiumBy
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import os
import networkx as nx
import random
import pandas as pd
from commands import command,command1,command2,example1,command4,example2,command6
import chromadb
from transformers import BertTokenizer, BertModel
import torch
import gc
from sklearn.metrics.pairwise import cosine_similarity

# 加载预训练的BERT模型和tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

class Record:
    def __init__(self,comment,key_sentence):
        self.comment = comment   # 用户评论的内容
        self.key_sentence = key_sentence   # 关键语句
        #self.key_info = ''   # 关键信息
        self.targetac = ''   # 目标活动
        self.acfunction = ''  # 目标活动的功能
        self.targetst = ''  # 目标状态
        self.statelist = ''   # 目标状态的子任务列表
        self.node = []  # 复现过程中经历的节点
        self.op = []  # 整个复现过程完成的操作
        self.answer = ''


# 确定应用包名和launch activity
capabilities = dict(
    platformName='Android',
    automationName='uiautomator2',
    deviceName='99141FFAZ00ATK',
    #appPackage='com.google.android.apps.photos',
    #appActivity='com.google.android.apps.photos.home.HomeActivity',
    #appPackage='com.zhiliaoapp.musically',
    #appActivity='com.ss.android.ugc.aweme.splash.SplashActivity',
    #appPackage='com.spotify.music',
    #appActivity='.MainActivity',
    appPackage='com.pinterest',
    appActivity='.activity.task.activity.MainActivity',
    #appPackage='com.lemon.lvoverseas',
    #appActivity='com.vega.main.MainActivity',
    #appPackage='com.google.android.apps.translate',
    #appActivity='com.google.android.apps.translate.TranslateActivity',
    forceAppLaunch='true',
    shouldTerminateApp='true',
    noReset='true',
    newCommandTimeout='6000'
)

os.environ.setdefault("OPENAI_API_KEY", "sk-oh7AbfOOYzPLt23v2075Ec7f1eEc4e64A1Dd44865cFb8eDc")
os.environ.setdefault("OPENAI_BASE_URL", "https://oneapi.xty.app/v1")
#chroma_client = chromadb.Client()
#collection = chroma_client.create_collection(name="my_collection")
appium_server_url = 'http://127.0.0.1:4723'
app_name = 'pinterest_activity'
log = open(f"..\\app\\{app_name}\\output\\log.txt", 'a', encoding='utf-8')
is_finished = 0  # 同一条评论的最多执行次数
page_num = 1
history_action = []  # 记录执行过的历史动作
comment_num = 11
test_comment_num = 61  # 测试的用户评论的数量
screenshot_dir = f'..\\app\\{app_name}\\output\\screenshot-2'
comment = ''
max_actions = 10   # 最多执行动作数
# 根据comment确定初始activity
# 从文件中随机获取用户评论
df = pd.read_excel(f"..\\app\\{app_name}\\comments-2.xlsx")
key_sentence = ''

#chroma = Chroma()
#vectorstore = chroma.from_texts(
#        texts,
#        embedding=OpenAIEmbeddings()
#)
while True:
    if comment_num == len(df):
        break
    if is_finished == 0:
        comment_num += 1
        is_finished = 5
        comment = df.iloc[comment_num]['comment']
        #comment = '''I don't know what to say. Spotify WAS my fav app. Ever since the new update came, we can't listen to a Playlist in order or start playing the song at a particular time, the experience has become literal trash. Even basic features have become premium options where we don't even feel like playing anything on this app. Please fix this problem so that we can actually enjoy listening to music on this platform.'''
        if df.iloc[comment_num]['test'] == 'YES':
            time.sleep(5)
            key_sentence = ask_gpt_4(command6 + comment)
            #key_sentence = df.iloc[comment_num]['key_sentence']
            #is_finished = 3
    #else:
        #comment_num += 1
        #is_finished = 5
        #continue
    #if 'YES' in result or 'yes' in result:
    #match = re.search(r'Key sentence:', result)
    #if match is None:
    #    match = re.search(r'Key sentences:', result)
    #key_sentence = result[(match.span())[1]:]
    record = Record(comment, key_sentence)
    history_action = []

    # 构建有向图,有向图的节点是state
    node = {}
    event = {}
    # 构建有向图
    G = nx.DiGraph()

    with open(f"..\\app\\{app_name}\\activity_function.json") as js_file:
        activity_function = json.load(js_file)

    #with open(f"..\\app\\{app_name}\\state_widgets.json") as js_file:
    #    state_widgets = json.load(js_file)

    with open(f"..\\app\\{app_name}\\utg.js", "r") as js_file:
        js_code = js_file.read()
        for element in re.findall(r'"activity": "(.+?)".+?"state_str": "(.+?)"', js_code, re.DOTALL):
            if element[0] not in node:
                node[(element[0])] = []
                node[(element[0])].append(element[1])
            else:
                if element[1] in node[(element[0])]:
                    continue
                else:
                    node[(element[0])].append(element[1])
        for element in re.findall(r'"from": "(.+?)".+?"to": "(.+?)".+?"event_str": "(.+?)"', js_code, re.DOTALL):  # 添加边
            if G.has_edge(element[0], element[1]):
                continue
            else:
                G.add_edge(element[0], element[1])
                event[(element[0], element[1])] = element[2]

    # utg补充（人工手动）
    with open(f'..\\app\\{app_name}\\utg_add.js', "r", encoding='utf-8') as js_file:
        js_code = js_file.read()
        for element in re.findall(r'"activity": "(.+?)".+?"state_str": "(.+?)"', js_code, re.DOTALL):
            if element[0] not in node:
                node[(element[0])] = []
                node[(element[0])].append(element[1])
            else:
                if element[1] in node[(element[0])]:
                    continue
                else:
                    node[(element[0])].append(element[1])
        for element in re.findall(r'"from": "(.+?)".+?"to": "(.+?)".+?"event_str": "(.+?)"', js_code, re.DOTALL):  # 添加边
            if G.has_edge(element[0], element[1]):
                continue
            else:
                G.add_edge(element[0], element[1])
                event[(element[0], element[1])] = element[2]


    # query = "task about " + key_info
    # query = comment + "key information:" + key_info + "Which activity is the comment describe?"
    # docs = vectorstore.similarity_search(query)
    # message = ''
    # for doc in docs:
    #    matches = re.findall(r'(.+):\[(.+)\]', doc.page_content)
    #    message = message + matches[0][0] + ':' + activity_function[matches[0][0]] + '\ntask list:' + matches[0][1] + '\n\n'
    # content = command + "Here are task lists for some activities:\n" + message + "\nYou need to determine which activity the following comment describes:" + comment + "\nThe key information of this comment: '" + key_info
    # print(content)
    # DestPage = ask_gpt_activity(content)  # 确定目标activity
    # log.write(content + "\n" + DestPage)
    with open(f"..\\app\\{app_name}\\activity_task.json", 'r', encoding='utf-8') as file:
        page_function = json.load(file)
        # 只用任务名称
        activities = []
        texts = []
        for key, value in page_function.items():
            activities.append(key)
            if len(value) != 0:
                texts.append(key + ":" + str(value))
    activity_num = len(activities)  # activity数量

    i = 1
    while True:
        if len(activity_function) <= 4:
            message = ''
            for key, value in activity_function.items():
                message = message + key + ':' + value + '\ntask list:' + str(page_function[key]) + '\n\n'
            content = command + "Here are task lists for some activities:\n" + message + "\nYou need to determine which activity the following comment describes:" + comment + "\nThe key sentence of this comment: '" + key_sentence
            print(content)
            DestPage = ask_gpt_activity(content)  # 确定目标activity
            log.write(content + "\n" + DestPage)
        else:
            #query = comment + "key sentence:" + key_sentence + "Which activity is the comment describe?"
            #print(vectorstore._collection.count())
            #docs = vectorstore.similarity_search(query, k=vectorstore._collection.count())
            #temp = []
            #for doc in docs:
            #   temp.append(doc.page_content)
            #docs = list(set(temp))
            query = key_sentence
            # 获取activity task
            docs = []
            for ac in texts:
                similarity = tools.calculate_similarity(query, ac, model, tokenizer)
                docs.append((ac, similarity))
             # 按相似度从大到小排序
            docs.sort(key=lambda x: x[1], reverse=True)
            message = ''
            end = len(docs) if i * 4 > len(docs) else i * 4
            for doc in docs[(i - 1) * 4: end]:
                matches = re.findall(r'(.+):\[(.+)\]', doc[0])
                message = message + matches[0][0] + ':' + activity_function[matches[0][0]] + '\ntask list:' + \
                          matches[0][1] + '\n\n'
            content = command + "Here are task lists for some activities:\n" + message + "\nYou need to determine which activity the following comment describes:" + comment + "\nThe key sentence of this comment: '" + key_sentence + "\nIf you think none of the activities is the comment describes, please output 'none'. "
            print(content)
            DestPage = ask_gpt_activity(content).split('\n')[0]  # 确定目标activity
            log.write(content + "\n" + DestPage)
            if 'none' in DestPage or 'None' in DestPage or 'NONE' in DestPage:
                i += 1
                if (i - 1) * 4 > len(docs):
                    i = 0
                    break
                continue
        while DestPage not in node.keys():
            DestPage = ask_gpt_activity('"'+ DestPage + '" is not an activity name,please select again.' + content)
            log.write('"'+ DestPage + '" is not an activity name,please select again.' + content + "\n" + DestPage)
            time.sleep(5)
        if DestPage in node.keys():
            break
    if i==0:
        with open(f'..\\app\\{app_name}\\output\\record-2\\comment' + str(test_comment_num) + '.json', 'w') as f:
            ob = [
                {"comment": record.comment, "key sentence": record.key_sentence, "target activity": '',
                 "the function of activity": '', "target state": '',
                 "the sub-task list of state": '', "nodes": [], "operations": [],
                 "Final answer": ''}]
            json.dump(ob, f, indent=4, separators=(',', ': '))
            is_finished -= 1
            test_comment_num += 1
            #comment_num += 1
            # df.drop(index=random_index)  # 在原始数据文件中删除此条评论
        continue
    record.targetac = DestPage
    record.acfunction = activity_function[DestPage]
    time.sleep(5)
    #del chroma
    #del vectorstore
    #gc.collect()

    # 确定目标state
    with open(f"..\\app\\{app_name}\\state_task.json", 'r', encoding='utf-8') as file:
        state_task = json.load(file)
        states = []
        for state_end in node[DestPage]:
            try:
                states.append(state_end + ":" + str(state_task[state_end]))
            except:
                pass
    if len(states) > 3:
        #query = comment + "key information:" + key_sentence + "Which state is the key information about?"
        query = key_sentence
        # 计算各个其他语句与标准语句的相似度
        '''
        docs_state = []
        for st in states:
            similarity = tools.calculate_similarity(query, st, model, tokenizer)
            docs_state.append((st, similarity))
        # 按相似度从大到小排序
        docs_state.sort(key=lambda x: x[1], reverse=True)
        '''
        #chroma = Chroma()
        #vectorstore_state = chroma.from_texts(
        #    states,
        #    embedding=OpenAIEmbeddings()
        #)

        i = 1
        #query = comment + "key information:" + key_sentence + "Which state is the comment describe?"
        #print(vectorstore_state._collection.count())
        #docs_state = vectorstore_state.max_marginal_relevance_search(query, k=vectorstore_state._collection.count())
        #temp = []
        #for doc_state in docs_state:
        #    temp.append(doc_state.page_content)
        #docs_state = list(set(temp))
        docs_state = tools.calculate_cosine_similarity(query, states)
        while True:
            if (i - 1) * 3 - len(states) >= 0:
                i = 0
                break
            message = ''
            end = len(docs_state) if i * 3 > len(docs_state) else i * 3
            for doc_state in docs_state[(i - 1) * 3: end]:
                flag = 0
                # 判断是否含有activity
                for key, value in activity_function.items():
                    if key in doc_state[0]:
                        flag = 1
                        break
                if flag == 0:
                    print(doc_state[0])
                    message = message + doc_state[0] + "\n"
            content = command2 + "Here is a task list for states:\n" + message + "\nYou need to determine which state the following comment describes:" + comment + "\nThe key sentence of this comment: '" + key_sentence + "\nIf you think this comment does not describe any of the listed states, please output 'none'. "
            DestState = ask_gpt_state(content)
            log.write(content + "\n" + DestState)
            if 'none' in DestState or 'None' in DestState or 'NONE' in DestState:
                i += 1
                continue
            if DestState not in content:
                continue
            while not G.has_node(DestState):
                DestState = ask_gpt_state('This in not an state name,please select again.' + content)
                log.write('This in not an state name,please select again.' + content + "\n" + DestState)
                time.sleep(5)
            while DestState not in node[DestPage]:
                DestState = ask_gpt_state('This in not an state of activity' + DestPage + ',please select again.' + content)
                log.write('This in not an state of activity' + DestPage + ',please select again.' + content + "\n" + DestState)
                time.sleep(5)
            if G.has_node(DestState) and DestState in node[DestPage]:
                #del vectorstore_state
                #del vectorstore
                #del chroma
                #gc.collect()
                break
    elif len(states) == 3 or len(states) == 2:
        message = ''
        for state in states:
            print(state)
            message = message + state + "\n"
        content = command2 + "Here is a task list for states:\n" + message + "\nYou need to determine which state the following comment describes:" + comment + "\nThe key sentence of this comment: '" + key_sentence
        DestState = ask_gpt_state(content)
        log.write(content + "\n" + DestState)
    elif len(states) == 1:
        DestState = state_end
    if i == 0:
        #is_finished -= 1
        with open(f'..\\app\\{app_name}\\output\\record-2\\comment' + str(test_comment_num) + '.json', 'w') as f:
            ob = [{"comment": record.comment, "key sentence": record.key_sentence, "target activity": record.targetac,
                   "the function of activity": record.acfunction, "target state": '',
                   "the sub-task list of state": '', "nodes":[], "operations": [],
                   "Final answer":''}]
            json.dump(ob, f, indent=4, separators=(',', ': '))
            test_comment_num += 1
            is_finished -= 1
            #comment_num += 1
            # df.drop(index=random_index)  # 在原始数据文件中删除此条评论
        continue
    print(content)
    while not G.has_node(DestState):
        DestState = ask_gpt_state('This is not a state name, please choose again.' + content)
        log.write('This is not a state name, please choose again.' + content + "\n" + DestState)
    record.targetst = DestState
    record.statelist = str(state_task[DestState])


    driver = webdriver.Remote(appium_server_url,options=UiAutomator2Options().load_capabilities(capabilities))  # 开启driver
    time.sleep(5)  # 等待开启广告

    # CurrentPage = driver.current_activity  # 当前页面activity
    #CurrentPage = "fdedbaae0d7db088bdc1a119bf22aa84"  # google photos的初始页面
    #CurrentPage = "a17e568448adcdbafe37f9f618f3f5ca"  # spotify的初始页面
    #CurrentPage = "86ad15cba4ecd2166c92cbbf7eddfa20"
    CurrentPage = "ba5f165ac71b67896bd0c28f07857be5"  # Pinterest
    # CurrentPage = "b3c2b8cf7b8f3959cd3c2bd09dbce71a"   # CapCut
    #CurrentPage = '1e0a8968f43dbb61fd758c305c65c40a'  # google translate
    if not os.path.exists(screenshot_dir + '\\comment' + str(test_comment_num)):
        os.mkdir(screenshot_dir + '\\comment' + str(test_comment_num))
    screenshot_path = tools.get_screenshot(screenshot_dir + '\\comment' + str(test_comment_num) + '\\' + CurrentPage + '.png')
    activity_name = tools.get_activity()
    if activity_name is None:
        activity_name = ''
    node = {"image": screenshot_path, "activity": activity_name , "state_str": CurrentPage}
    record.node.append(node)
    page_html_file = json.load(open(f"..\\app\\{app_name}\\page_html.json", 'r', encoding='utf-8'))
    # 用appium到达目标页面
    if CurrentPage != DestState:
        path = nx.shortest_path(G, CurrentPage, DestState)
        print(path)
        i = 0
        while i < len(path) - 1:
            e = event[(path[i], path[i + 1])]  # explore阶段执行的动作，作为提示信息提供给大模型
            if 'long-click' in e:
                a, b = tools.tap_coordinate(e)
                x_max = 1080
                y_max = 2280
                x = driver.get_window_size()['width']
                y = driver.get_window_size()['height']
                driver.tap([(int(a / x_max * x), int(b / y_max * y))], 1000)
                time.sleep(5)
                history_action.append(e)
                action = {'from': path[i], 'to': path[i + 1], 'event': e}
                record.op.append(action)
                screenshot_path = tools.get_screenshot(screenshot_dir + '\\comment' + str(test_comment_num) + '\\' + path[i+1] + '.png')
                activity_name = tools.get_activity()
                if activity_name is None:
                    activity_name = ''
                node = {"image": screenshot_path, "activity": activity_name,"state_str": path[i + 1]}
                record.node.append(node)
            elif 'click' in e:
                try:
                    coordinate = re.findall(r':x(\d+):y(\d+)', e)
                    a = int(coordinate[0][0])
                    b = int(coordinate[0][1])
                    x_max = 1080
                    y_max = 2280
                    # y_max = 2148
                except:
                    a, b = tools.tap_coordinate(e)
                    x_max = 1080
                    y_max = 2280
                    # y_max = 2148
                x = driver.get_window_size()['width']
                y = driver.get_window_size()['height']
                driver.tap([(int(a / x_max * x), int(b / y_max * y))], 100)
                time.sleep(10)
                history_action.append(e)
                action = {'from': path[i], 'to': path[i + 1], 'event': e}
                record.op.append(action)
                screenshot_path = tools.get_screenshot(
                    screenshot_dir + '\\comment' + str(test_comment_num) + '\\' + path[i + 1] + '.png')
                activity_name = tools.get_activity()
                if activity_name is None:
                    activity_name = ''
                node = {"image": screenshot_path, "activity": activity_name, "state_str": path[i + 1]}
                record.node.append(node)
                # i += 1
            elif 'input' in e:
                matches = re.findall(r'input\((.+?)-(.+?):\[(\d+),(\d+)\]\[(\d+),(\d+)\]\)\((.+?)\)',e)
                xpath = '//android.widget.EditText[@resource-id=\"' + matches[0][1] + '\"]'
                search_text = driver.find_element(by=AppiumBy.XPATH, value=xpath)
                search_text.send_keys(matches[0][6])
                time.sleep(5)
                history_action.append(e)
                action = {'from': path[i], 'to': path[i + 1], 'event': e}
                record.op.append(action)
                screenshot_path = tools.get_screenshot(screenshot_dir + '\\comment' + str(test_comment_num) + '\\' + path[i+1] + '.png')
                activity_name = tools.get_activity()
                if activity_name is None:
                    activity_name = ''
                node = {"image": screenshot_path, "activity": activity_name,"state_str": path[i+1]}
                record.node.append(node)
                # i += 1
            elif 'scroll-up' in e:
                width = driver.get_window_size()['width']
                height = driver.get_window_size()['height']
                driver.swipe(start_x=width * 0.5, start_y=height * 0.9, end_x=width * 0.5, end_y=height * 0.1,duration=1000)
                time.sleep(5)
                history_action.append(e)
                action = {'from': path[i], 'to': path[i + 1], 'event': e}
                record.op.append(action)
                screenshot_path = tools.get_screenshot(screenshot_dir + '\\comment' + str(test_comment_num) + '\\' + path[i+1] + '.png')
                activity_name = tools.get_activity()
                if activity_name is None:
                    activity_name = ''
                node = {"image": screenshot_path, "activity": activity_name,"state_str": path[i + 1]}
                record.node.append(node)
                # i += 1
            elif 'scroll-down' in e:
                width = driver.get_window_size()['width']
                height = driver.get_window_size()['height']
                driver.swipe(start_x=width / 2, start_y=height * 0.9, end_x=width / 2, end_y=height * 0.1, duration=1000)
                time.sleep(5)
                history_action.append(e)
                action = {'from': path[i], 'to': path[i + 1], 'event': e}
                record.op.append(action)
                screenshot_path = tools.get_screenshot(screenshot_dir + '\\comment' + str(test_comment_num) + '\\' + path[i+1] + '.png')
                activity_name = tools.get_activity()
                if activity_name is None:
                    activity_name = ''
                node = {"image": screenshot_path, "activity": activity_name,"state_str": path[i + 1]}
                record.node.append(node)
            elif 'scroll-left' in e:
                a, b = tools.tap_coordinate(e)
                driver.swipe(a, b, a + 1080, b)
                time.sleep(5)
                history_action.append(e)
                action = {'from': path[i], 'to': path[i + 1], 'event': e}
                record.op.append(action)
                screenshot_path = tools.get_screenshot(screenshot_dir + '\\comment' + str(test_comment_num) + '\\' + path[i+1] + '.png')
                activity_name = tools.get_activity()
                if activity_name is None:
                    activity_name = ''
                node = {"image": screenshot_path, "activity": activity_name, "state_str": path[i + 1]}
                record.node.append(node)

            '''
            # 动作完成后，判断是否到达下一个状态
            source = driver.page_source
            CurrentState, coordinate = tools.traverse_html(source, 1)
            current_widgets = tools.source_widgets(source)
            temp = i
            state_widgets[path[i + 1]]
            similarity = tools.state_similarity(current_widgets, state_widgets[path[i + 1]])
            if similarity > 0.7:
                i += 1
            else:
                for j in range(i, len(path)):
                    similarity = tools.state_similarity(current_widgets, state_widgets[path[j]])
                    if similarity > 0.7:
                        i = j
                        break
                if j == temp:  # 点击组件后页面状态未发生变化
                    print('到达目标状态时：点击组件页面未发生变化 ' + path[i] + ' to ' + path[i + 1])
                    driver.quit()
                    log.close()
                    exit(1)
                elif i == temp:  # 没有找到相似页面
                    print('未成功到达目标页面')
                    driver.quit()
                    log.close()
                    exit(1)
            '''
            i += 1
    time.sleep(5)
    # 到达目标页面后，大模型根据用户评论完成复现
    # 判断是否完成评论复现
    flag = 0  # 评论复现是否完成
    actions = ''
    for action in history_action:
        actions = actions + action + '\n'
    CurrentPageSource = driver.page_source
    CurrentPageHTML, coordinate, x_max, y_max = tools.page(CurrentPageSource, page_num, 1)  # 当前页面的HTML presentation
    content = 'This is the current status information. Please determine whether the entire process of reproducing a comment-described scenario has been completed.' + \
              'We only need to arrive at the scene described by the comment without completely reproducing the entire process of the comment.You need to focus on the actions we have completed.' + example2 + \
              'Please output:YES/NO\n' + 'comment:' + comment + "\nThe key words of the comment:" + key_sentence +\
              '\nThe actions we have completed include:\n' + actions + '\nthe current status information:' + CurrentPageHTML
    time.sleep(5)
    result = ask_gpt_4(content)
    log.write(content + "\n" + result)
    print(content + "\n" + result)
    # while ('YES' in result and 'NO' in result) or ('YES' not in result and 'NO' not in result):
    #    result = ask_gpt(content)
    if 'YES' in result or 'Yes' in result or 'yes' in result:
        flag = 1
    elif 'NO' in result or 'No' in result or 'no' in result:
        flag = 0
    begin = DestState
    while not flag:
        CurrentPageSource = driver.page_source
        CurrentPageHTML, coordinate, x_max, y_max = tools.page(CurrentPageSource, page_num, 1)  # 当前页面的HTML presentation
        actions = ''
        for action in history_action:
            actions = actions + action + '\n'
        content = 'You need to select an action and the index of the target UI element to reproduce a comment-described scenario.We only need to arrive at the scene described by the comment without completely reproducing the entire process of the comment.\n' + \
                    '''Be careful not to select actions that are irrelevant to the scenario described in the user's comment, as this will be considered redundant.\n''' +\
                  'User comment:' + comment + '\nThe key words of the comment:' + key_sentence + '\nWidgets information of current state:\n' + CurrentPageHTML + "\nThe actions we have done:\n" + actions + \
                  '\noutput format:"click ui_index" or "input ui_index input-text" or "scroll up/down or "long-click".Example:\nclick 1\ninput 1 "123"\nscroll up\nlong-click\nNote that only one action is output at a time.If you think the current page is wrong or want to return to the previous page, please output "back".'
                #'\noutput format:"click ui_index" or "input ui_index input-text" or "scroll up/down".Example:\nclick ui_index=1\ninput ui_index=1 "123"\nscroll up\nNote that only one action is output at a time'
        time.sleep(5)
        result = ask_gpt_4(content)
        log.write(content + "\n" + result)
        print(content + "\n" + result)
        # = 0  # 是否得到下一个要执行的动作
        while True:
            # 判断动作是否已经执行过
            if 'long-click' in result:
                if len(history_action) != 0 and ('long-click' == history_action[len(history_action) - 1]):
                    result = ask_gpt4('The action "long-click has been done.' + content)
                    log.write('The action "long-click has been done.'  + content + "\n" + result + '\n')
                    continue
            elif 'click' in result:
                format = re.compile(r'click (\d+)')
                try:
                    id = int(format.findall(result)[0])
                except:  # 输出格式错误
                    result = ask_gpt4('Please output in right format.' + content)
                    log.write('Please output in right format.' + content + "\n" + result)
                    continue
                if id not in range(len(coordinate)):
                    result = ask_gpt4('There is not a widget with id=' + str(id) + '.' + content)
                    log.write('There is not a widget with id=' + str(id) + '.' + content + "\n" + result + '\n')
                    continue
                if len(history_action) != 0 and ('click' + coordinate[id].html == history_action[len(history_action) - 1]):
                    result = ask_gpt4('The action "click" ' + str(id) +'" has been done.' + content)
                    log.write('The action "click" ' + str(id) +'" has been done.' + content + "\n" + result + '\n')
                    continue
            elif 'input' in result:
                format = re.compile(r'input (\d+) \"(.+?)\"')
                try:
                    matches = format.findall(result)
                    id = int(matches[0][0])
                    text = matches[0][1]
                except:
                    result = ask_gpt4('Please output in right format.' + content)
                    log.write('Please output in right format.' + content + "\n" + result + '\n')
                    continue
                if id not in range(len(coordinate)):
                    result = ask_gpt4('There is not a widget with id=' + str(id) + '.' + content)
                    log.write('There is not a widget with id=' + str(id) + '.' + content + "\n" + result + '\n')
                    continue
                if len(history_action) != 0 and ('input' + coordinate[id].html + text in history_action):
                    result = ask_gpt4('The action "input ' + str(id) + ' ' + text + '" has been done.' + content)
                    log.write('The action "input ' + str(id) + ' ' + text + '" has been done.' + content + "\n" + result + '\n')
                    continue
            elif 'back' in result:
                '''
                # 比较当前页面和初始页面的相似度
                source = driver.page_source
                CurrentState, coordinate = tools.traverse_html(source, 1)
                current_widgets = tools.source_widgets(source)
                similarity = tools.state_similarity(current_widgets, state_widgets[CurrentPage])
                print(similarity)
                if similarity > 0.9:
                    result = ask_gpt_4('You have returned to the initial interface of the application and cannot go back' + content)
                    log.write('You have returned to the initial interface of the application and cannot go back' + content + "\n" + result + '\n')
                    continue
                '''
                if len(history_action) != 0 and history_action[len(history_action)-1] == 'back':
                    result = ask_gpt4('The "back" action has been done.' + content)
                    log.write('The "back" action has been done.' + content + "\n" + result + '\n')
                    continue
            if 'long-click' in result:
                CurrentPageSource = driver.page_source
                x_max = 1080
                y_max = 2280
                x = driver.get_window_size()['width']
                y = driver.get_window_size()['height']
                a = int(x/2)
                b = int(y/2)
                driver.tap([(a, b)], 1000)
                time.sleep(5)
                history_action.append('long-click')
                action = {'from': begin, 'to': str(hash(CurrentPageSource)), 'event': 'long-click'}
                record.op.append(action)
                begin = action['to']
                screenshot_path = tools.get_screenshot(screenshot_dir + '\\comment' + str(test_comment_num) + '\\' + str(hash(CurrentPageSource)) + '.png')
                activity_name = tools.get_activity()
                if activity_name is None:
                    activity_name = ''
                node = {"image": screenshot_path, "activity": activity_name,"state_str": str(hash(CurrentPageSource))}
                record.node.append(node)
                break
            elif 'click' in result:
                format = re.compile(r'click (\d+)')
                try:
                    id = int(format.findall(result)[0])
                except:
                    result = ask_gpt4('Please output in right format.' + content)
                    log.write('Please output in right format.' + content + "\n" + result + '\n')
                    continue
                try:
                    widget_coordinate = coordinate[id].bounds
                    a, b = tools.tap_coordinate(widget_coordinate)
                    # 获取当前屏幕大小
                    x = driver.get_window_size()['width']
                    y = driver.get_window_size()['height']
                    driver.tap([(int(a / x_max * x), int(b / y_max * y))], 100)
                    time.sleep(10)
                    history_action.append('click' + coordinate[id].html)
                    CurrentPageSource = driver.page_source
                    action = {'from': begin, 'to': str(hash(CurrentPageSource)), 'event': 'click' + coordinate[id].html}
                    record.op.append(action)
                    begin = action['to']
                    screenshot_path = tools.get_screenshot(
                        screenshot_dir + '\\comment' + str(test_comment_num) + '\\' + str(
                            hash(CurrentPageSource)) + '.png')
                    activity_name = tools.get_activity()
                    if activity_name is None:
                        activity_name = ''
                    node = {"image": screenshot_path, "activity": activity_name,
                            "state_str": str(hash(CurrentPageSource))}
                    record.node.append(node)
                    break
                except:
                    continue
            elif 'input' in result:
                format = re.compile(r'input (\d+) \"(.+?)\"')
                try:
                    matches = format.findall(result)
                    id = int(matches[0][0])
                    text = matches[0][1]
                    if 'EditText' not in coordinate[id].classname:
                        result = ask_gpt4('The widget id=' + str(id) + ' can not be edited.' + content)
                except:
                    result = ask_gpt4('Please output in right format.' + content)
                    continue
                # if 'input' + coordinate[id].html + text in history_action:
                # ask_gpt('This action has been done.')
                # else:
                try:
                    xpath = '//android.widget.EditText[@resource-id=\"' + coordinate[id].resource_id + '\"]'
                    search_text = driver.find_element(by=AppiumBy.XPATH, value=xpath)
                    search_text.send_keys(text)
                    history_action.append('input' + coordinate[id].html + text)
                    time.sleep(10)
                    CurrentPageSource = driver.page_source
                    action = {'from': begin, 'to': str(hash(CurrentPageSource)),
                              'event': 'input' + coordinate[id].html + text}
                    record.op.append(action)
                    begin = action['to']
                    screenshot_path = tools.get_screenshot(
                        screenshot_dir + '\\comment' + str(test_comment_num) + '\\' + str(
                            hash(CurrentPageSource)) + '.png')
                    activity_name = tools.get_activity()
                    if activity_name is None:
                        activity_name = ''
                    node = {"image": screenshot_path, "activity": activity_name,
                            "state_str": str(hash(CurrentPageSource))}
                    record.node.append(node)
                    break
                except:
                    continue
            elif 'scroll' in result:
                if 'down' in result:
                    size = driver.get_window_size()
                    height = driver.get_window_size().get('height')
                    weight = driver.get_window_size().get('width')
                    driver.swipe(start_x=weight * 0.5, start_y=height * 0.1, end_x=weight * 0.5, end_y=height * 0.9, duration=1000)
                    history_action.append('scroll down')
                    time.sleep(10)
                    CurrentPageSource = driver.page_source
                    action = {'from': begin, 'to': str(hash(CurrentPageSource)), 'event': 'scroll down'}
                    record.op.append(action)
                    begin = action['to']
                    screenshot_path = tools.get_screenshot(screenshot_dir + '\\comment' + str(test_comment_num) + '\\' +  str(hash(CurrentPageSource)) + '.png')
                    activity_name = tools.get_activity()
                    if activity_name is None:
                        activity_name = ''
                    node = {"image": screenshot_path, "activity": activity_name,"state_str": str(hash(CurrentPageSource))}
                    record.node.append(node)
                elif 'up' in result:
                    size = driver.get_window_size()
                    height = driver.get_window_size().get('height')
                    weight = driver.get_window_size().get('width')
                    driver.swipe(start_x=weight * 0.5, start_y=height * 0.9, end_x=weight * 0.5, end_y=height * 0.1,duration=1000)
                    history_action.append('scroll up')
                    time.sleep(10)
                    CurrentPageSource = driver.page_source
                    action = {'from': begin, 'to': str(hash(CurrentPageSource)), 'event': 'scroll up'}
                    record.op.append(action)
                    begin = action['to']
                    screenshot_path = tools.get_screenshot(screenshot_dir + '\\comment' + str(test_comment_num) + '\\' +  str(hash(CurrentPageSource)) + '.png')
                    activity_name = tools.get_activity()
                    if activity_name is None:
                        activity_name = ''
                    node = {"image": screenshot_path, "activity": activity_name,"state_str": str(hash(CurrentPageSource))}
                    record.node.append(node)
                break
            elif 'back' in result:
                driver.keyevent(4)
                history_action.append('back')
                time.sleep(10)
                CurrentPageSource = driver.page_source
                action = {'from': begin, 'to': hash(CurrentPageSource), 'event': 'back'}
                record.op.append(action)
                begin = action['to']
                screenshot_path = tools.get_screenshot(screenshot_dir + '\\comment' + str(test_comment_num) + '\\' + str(hash(CurrentPageSource)) + '.png')
                activity_name = tools.get_activity()
                if activity_name is None:
                    activity_name = ''
                node = {"image": screenshot_path, "activity": activity_name, "state_str": str(hash(CurrentPageSource))}
                record.node.append(node)
                break
            else:
                result = ask_gpt_4(content)

        if len(history_action) < max_actions:
            # 判断是否完成评论复现
            actions = ''
            for action in history_action:
                actions = actions + action + '\n'
            CurrentPageHTML, coordinate, x_max, y_max = tools.page(CurrentPageSource, page_num,1)  # 当前页面的HTML presentation
            content = 'This is the current status information. Please determine whether the entire process of reproducing a comment-described scenario has been completed.' + \
              'We only need to arrive at the scene described by the comment without completely reproducing the entire process of the comment.You need to focus on the actions we have completed.' + example2 + \
              'Please output:YES/NO\n' + 'comment:' + comment + "\nThe key sentence of the comment:" + key_sentence +\
              '\nThe actions we have completed include:\n' + actions + '\nthe current status information:' + CurrentPageHTML
            time.sleep(5)
            result = ask_gpt4(content)
            log.write(content + "\n" + result)
            print(content + "\n" + result)
            # while ('YES' in result and 'NO' in result) or ('YES' not in result and 'NO' not in result):
            #    result = ask_gpt(content)
            if 'YES' in result or 'Yes' in result or 'yse' in result:
                flag = 1
            elif 'NO' in result or 'No' in result or 'no' in result:
                flag = 0
        else:
            break

    # 将记录的内容提供给LLM，判断整个复现过程是否完成
    command5 = f'''I am reproducing the scenario described in the user's comment. I will give you information about the entire reproduction process. Please use the information to determine whether the scenario described in the user's comment has been reproduced.\n''' +\
        f'''User review content:{record.comment}\nYou need to pay special attention to these sentences:{record.key_sentence}\n\n''' + \
        f'''The actions completed during the entire reproduction process:\n{actions}\n\nWe only need to arrive at the scene described by the comment without completely reproducing the entire process of the comment.You need to focus on the actions we have completed.{example2}If the review describes multiple scenarios, reaching one scenario is considered complete.If you think the reproduction is complete, please output YES, otherwise output NO.'''
    while True:
        time.sleep(5)
        result = ask_gpt4(command5)
        log.write(command5 + "\n" + result)
        if 'YES' in result:
            record.answer = 'YES'
            #is_finished = 0
            break
        elif 'NO' in result:
            record.answer = 'NO'
            #is_finished -= 1
            break

    #if is_finished == 0:
    with open(f'..\\app\\{app_name}\\output\\record-2\\comment' + str(test_comment_num) + '.json', 'w') as f:
        ob = [{"comment": record.comment, "key sentence": record.key_sentence, "target activity": record.targetac,"the function of activity": record.acfunction, "target state": record.targetst,
                "the sub-task list of state": record.statelist, "nodes": record.node, "operations": record.op, "Final answer": record.answer}]
        json.dump(ob, f, indent=4, separators=(',', ': '))
        test_comment_num += 1
        #comment_num += 1
        #df.drop(index=random_index)  # 在原始数据文件中删除此条评论
        is_finished -= 1
        driver.quit()
log.close()




