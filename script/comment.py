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
from commands import command,command1,command2,example1,example2,command6,get_scenarios, example_select_action
import chromadb
from transformers import BertTokenizer, BertModel
import torch
import gc
from sklearn.metrics.pairwise import cosine_similarity
import shutil
from copy import deepcopy

# 加载预训练的BERT模型和tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

class Record:
    def __init__(self,comment):
        self.comment = comment   # 用户评论的内容
        self.scenario = []   # 用户评论中包括的所有可以进行复现的场景
        self.key_sentence = ''   # 关键语句，可以根据关键语句判断当前正在复现的场景
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
    deviceName='9A221FFAZ003FC',
    appPackage='com.google.android.apps.photos',
    appActivity='com.google.android.apps.photos.home.HomeActivity',
    # appPackage='com.zhiliaoapp.musically',
    # appActivity='com.ss.android.ugc.aweme.splash.SplashActivity',
    # appPackage='com.spotify.music',
    # appActivity='.MainActivity',
    # appPackage='com.pinterest',
    # appActivity='.activity.task.activity.MainActivity',
    # appPackage='com.lemon.lvoverseas',
    # appActivity='com.vega.main.MainActivity',
    # appPackage='com.google.android.apps.translate',
    # appActivity='com.google.android.apps.translate.TranslateActivity',
    # appPackage = 'com.android.chrome',
    # appActivity = 'com.google.android.apps.chrome.Main',
    # appPackage = 'com.instagram.android',
    # appActivity = 'com.instagram.mainactivity.InstagramMainActivity',
    forceAppLaunch='true',
    shouldTerminateApp='true',
    noReset='true',
    newCommandTimeout='6000'
)

os.environ.setdefault("OPENAI_API_KEY", "sk-LrEiXN7X1I40C9dCBc46D01eB950408bA42e12F423F3Da69")
os.environ.setdefault("OPENAI_BASE_URL", "https://oneapi.xty.app/v1")
#chroma_client = chromadb.Client()
#collection = chroma_client.create_collection(name="my_collection")
appium_server_url = 'http://127.0.0.1:4723'
app_name = 'photos_activity'
log = open(f"..\\app\\{app_name}\\output\\log.txt", 'a', encoding='utf-8')
log_sc = open(f"..\\app\\{app_name}\\output\\log_sc.txt", 'a', encoding='utf-8')
is_finished = 0  # 同一条评论的最多执行次数
page_num = 1
history_action = []  # 记录执行过的历史动作
comment_num = 40
test_comment_num = 301  # 测试的用户评论的数量
screenshot_dir = f'..\\app\\{app_name}\\output\\screenshot'
comment = ''
max_actions = 25   # 最多执行动作数
# 根据comment确定初始activity
# 从文件中随机获取用户评论
df = pd.read_excel("D:\\project\\MemoDroid\\app\\LLMARE_data.xlsx",sheet_name=3)
key_sentence = ''
re_action = {}
ob = []

while True:
    if test_comment_num == 302:
        break
    #comment = df.iloc[comment_num]['comment']
    comment = '''Since last week I have been unable to use the app. I always have it set to not auto back up or sync anything when I open the app.when I press do not turn on back up it just spins forever and doesn't let me into my photos at all.'''
    print(comment)
    #scenarios = [''' Use the app in airplane mode and try to play downloaded songs, where it sometimes fails to play them even in offline mode.''']
    # 获取用户评论中所有不连续的场景
    scenarios = get_scenarios(app_name[:-9], comment)
    log_sc.write(comment + '\n' + str(scenarios) + '\n')
    if len(scenarios) == 0:
        comment_num += 1
        continue
    record = Record(comment)
    # 判断场景是否可以复现，并将所有可以复现的场景保存到record中
    for sc in scenarios:
        record.scenario.append(sc)
    screenshot_path = screenshot_dir + '\\comment' + str(test_comment_num)
    if not os.path.exists(screenshot_path):  # 创建保存屏幕截图的目录
        os.mkdir(screenshot_path)
    result_path = f'..\\app\\{app_name}\\output\\record\\comment' + str(test_comment_num)
    if not os.path.exists(result_path):  # 创建保存复现过程的目录
        os.mkdir(result_path)
    else:
        # If the directory exists, remove all files within it
        path = result_path
        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)  # Remove the file or link
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # Remove the directory
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")
        print(f"All files deleted in the directory: {path}")

    # 构建有向图,有向图的节点是state
    utg_node = {}
    utg_event = {}
    # 构建有向图
    G = nx.DiGraph()

    with open(f"..\\app\\{app_name}\\activity_function.json") as js_file:
        activity_function = json.load(js_file)

    # with open(f"..\\app\\{app_name}\\state_widgets.json") as js_file:
    #    state_widgets = json.load(js_file)

    with open(f"..\\app\\{app_name}\\utg.js", "r") as js_file:
        js_code = js_file.read()
        for element in re.findall(r'"activity": "(.+?)".+?"state_str": "(.+?)"', js_code, re.DOTALL):
            if element[0] not in utg_node:
                utg_node[(element[0])] = []
                utg_node[(element[0])].append(element[1])
            else:
                if element[1] in utg_node[(element[0])]:
                    continue
                else:
                    utg_node[(element[0])].append(element[1])
        for element in re.findall(r'"from": "(.+?)".+?"to": "(.+?)".+?"event_str": "(.+?)"', js_code, re.DOTALL):  # 添加边
            if G.has_edge(element[0], element[1]):
                continue
            else:
                G.add_edge(element[0], element[1])
                utg_event[(element[0], element[1])] = element[2]

    # utg补充（人工手动）
    with open(f'..\\app\\{app_name}\\utg_add.js', "r", encoding='utf-8') as js_file:
        js_code = js_file.read()
        for element in re.findall(r'"activity": "(.+?)".+?"state_str": "(.+?)"', js_code, re.DOTALL):
            if element[0] not in utg_node:
                utg_node[(element[0])] = []
                utg_node[(element[0])].append(element[1])
            else:
                if element[1] in utg_node[(element[0])]:
                    continue
                else:
                    utg_node[(element[0])].append(element[1])
        for element in re.findall(r'"from": "(.+?)".+?"to": "(.+?)".+?"event_str": "(.+?)"', js_code, re.DOTALL):  # 添加边
            if G.has_edge(element[0], element[1]):
                continue
            else:
                G.add_edge(element[0], element[1])
                utg_event[(element[0], element[1])] = element[2]

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

    with open(f"..\\app\\{app_name}\\state_task.json", 'r', encoding='utf-8') as file:
        state_task = json.load(file)

    # 依次复现用户评论中可以复现的场景
    for k in range(len(record.scenario)):
        ob = []
        record.node = []
        record.op = []
        # 创建相关目录
        if not os.path.exists(screenshot_path + '\\scene' + str(k)):
            os.mkdir(screenshot_path + '\\scene' + str(k))
        else:
            # If the directory exists, remove all files within it
            path = screenshot_path + '\\scene' + str(k)
            for filename in os.listdir(path):
                file_path = os.path.join(path, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)  # Remove the file or link
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)  # Remove the directory
                except Exception as e:
                    print(f"Failed to delete {file_path}. Reason: {e}")
            print(f"All files deleted in the directory: {path}")
        sc_screenshot_path = screenshot_path + '\\scene' + str(k)
        scene_path = result_path + '\\scene' + str(k)
        is_finished = 0
        #record.key_sentence = ask_gpt4(command6 + "Comment:" + record.scenario[k])
        record.key_sentence = record.scenario[k]
        while is_finished < 2:
            history_action = []
            i = 1
            #选择目标activity
            while True:
                if len(activity_function) <= 4:
                    message = ''
                    for key, value in activity_function.items():
                        message = message + key + ':' + value + '\ntask list:' + str(page_function[key]) + '\n\n'
                    content = command + "Here are task lists for some activities:\n" + message + "\nYou need to determine which activity the following scenario describes:" + record.key_sentence
                    print(content)
                    while True:
                        try:
                            DestPage = ask_gpt_activity(content)  # 确定目标activity
                            log.write(content + "\n" + DestPage)
                            break
                        except Exception as e:
                            print(e)
                            pass
                else:
                    #query = comment + "key sentence:" + key_sentence + "Which activity is the comment describe?"
                    #print(vectorstore._collection.count())
                    #docs = vectorstore.similarity_search(query, k=vectorstore._collection.count())
                    #temp = []
                    #for doc in docs:
                    #   temp.append(doc.page_content)
                    #docs = list(set(temp))
                    query = record.key_sentence
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
                    content = command + "Here are task lists for some activities:\n" + message + "\nYou need to determine which activity the following scenario describes:" + record.key_sentence + "\nIf you think none of the activities is the scenario describes, please output 'none'. "
                    print(content)
                    while True:
                        try:
                            DestPage = ask_gpt_activity(content).split('\n')[0]  # 确定目标activity
                            log.write(content + "\n" + DestPage)
                            break
                        except:
                            pass
                    if 'none' in DestPage or 'None' in DestPage or 'NONE' in DestPage:
                        i += 1
                        if (i - 1) * 4 > len(docs):
                            i = 0
                            break
                        continue
                while DestPage not in utg_node.keys():
                    while True:
                        try:
                            DestPage = ask_gpt_activity('"'+ DestPage + '" is not an activity name,please select again.' + content)
                            log.write('"'+ DestPage + '" is not an activity name,please select again.' + content + "\n" + DestPage)
                            break
                        except:
                            pass
                    time.sleep(5)
                if DestPage in utg_node.keys():
                    break
            if i==0:
                with open(scene_path + '.json', 'w') as f:
                    ob = [{"comment": record.comment, "key sentence": record.key_sentence, "target activity": '',
                         "the function of activity": '', "target state": '',
                         "the sub-task list of state": '', "nodes": [], "operations": [],
                         "Final answer": ''}]
                    json.dump(ob, f, indent=4, separators=(',', ': '))
                    is_finished += 1
                continue
            record.targetac = DestPage
            record.acfunction = activity_function[DestPage]
            time.sleep(5)

            states = []
            for state_end in utg_node[DestPage]:
                try:
                    states.append(state_end + ":" + str(state_task[state_end]))
                except:
                    pass
            # 确定目标state
            if len(states) > 3:
                #query = comment + "key information:" + key_sentence + "Which state is the key information about?"
                query = record.key_sentence
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
                    content = command2 + "Here is a task list for states. The name of the state is in front of the list, and the list is a list of subtasks that can be completed in this state. \n" + message + "\nYou need to determine which state the following scenario describes:" + record.key_sentence + "\nIf you think this scenario does not describe any of the listed states, please output 'none'. "
                    while True:
                        try:
                            DestState = ask_gpt_state(content)
                            log.write(content + "\n" + DestState)
                            break
                        except:
                            pass
                    if 'none' in DestState or 'None' in DestState or 'NONE' in DestState:
                        i += 1
                        continue
                    if DestState not in content:
                        continue
                    while not G.has_node(DestState):
                        while True:
                            try:
                                DestState = ask_gpt_state('This in not an state name,please select again.' + content)
                                log.write('This in not an state name,please select again.' + content + "\n" + DestState)
                                break
                            except:
                                pass
                        time.sleep(5)
                    while DestState not in utg_node[DestPage]:
                        while True:
                            try:
                                DestState = ask_gpt_state('This in not an state of activity' + DestPage + ',please select again.' + content)
                                log.write('This in not an state of activity' + DestPage + ',please select again.' + content + "\n" + DestState)
                                break
                            except:
                                pass
                        time.sleep(5)
                    if G.has_node(DestState) and DestState in utg_node[DestPage]:
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
                content = command2 + "Here is a task list for states. The name of the state is in front of the list, and the list is a list of subtasks that can be completed in this state. \n" + message + "\nYou need to determine which state the following scenario describes:"  + record.key_sentence
                while True:
                    try:
                        DestState = ask_gpt_state(content)
                        log.write(content + "\n" + DestState)
                        break
                    except:
                        pass
            elif len(states) == 1:
                DestState = state_end
            if i == 0:
                #is_finished -= 1
                with open(scene_path + '.json', 'w') as f:
                    ob = [{"comment": record.comment, "key sentence": record.key_sentence, "target activity": record.targetac,
                           "the function of activity": record.acfunction, "target state": '',
                           "the sub-task list of state": '', "nodes":[], "operations": [],
                           "Final answer":''}]
                    json.dump(ob, f, indent=4, separators=(',', ': '))
                    is_finished += 1
                    #comment_num += 1
                    # df.drop(index=random_index)  # 在原始数据文件中删除此条评论
                continue
            print(content)
            while not G.has_node(DestState):
                while True:
                    try:
                        DestState = ask_gpt_state('This is not a state name, please choose again.' + content)
                        log.write('This is not a state name, please choose again.' + content + "\n" + DestState)
                        break
                    except:
                        pass
            record.targetst = DestState
            record.statelist = str(state_task[DestState])

            driver = webdriver.Remote(appium_server_url,options=UiAutomator2Options().load_capabilities(capabilities))  # 开启driver
            time.sleep(5)  # 等待开启广告
            begin_list = {"instagram_activity": "52e92cce957416c52f0c11fa5490fd56", "chrome_activity": "4e5cd78cfbca801ea96edfce1920b231", "photos_activity": "fdedbaae0d7db088bdc1a119bf22aa84", "pinterest_activity": "ba5f165ac71b67896bd0c28f07857be5", "tiktok_activity": "86ad15cba4ecd2166c92cbbf7eddfa20", "translate_activity": "1e0a8968f43dbb61fd758c305c65c40a", "spotify_activity": "a17e568448adcdbafe37f9f618f3f5ca", "capcut_activity": "b3c2b8cf7b8f3959cd3c2bd09dbce71a"}
            CurrentPage = begin_list[app_name]
            image_path = tools.get_screenshot(sc_screenshot_path + '\\' + CurrentPage + '.png')
            activity_name = tools.get_activity()
            if activity_name is None:
                activity_name = ''
            node = {"image": image_path, "activity": activity_name , "state_str": CurrentPage}
            record.node.append(node)
            # 用appium到达目标页面
            if CurrentPage != DestState:
                path = nx.shortest_path(G, CurrentPage, DestState)
                print(path)
                i = 0
                while i < len(path) - 1:
                    e = utg_event[(path[i], path[i + 1])]  # explore阶段执行的动作，作为提示信息提供给大模型
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
                        image_path = tools.get_screenshot(sc_screenshot_path + '\\' + path[i+1] + '.png')
                        activity_name = tools.get_activity()
                        if activity_name is None:
                            activity_name = ''
                        node = {"image": image_path, "activity": activity_name,"state_str": path[i + 1]}
                        record.node.append(node)
                    elif 'click' in e or "TouchEvent" in e:
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
                        try:
                            driver.tap([(int(a / x_max * x), int(b / y_max * y))], 100)
                        except:
                            # click(android.widget.TextView-Theme:[28,400][1052,654])
                            matches = re.findall(r'click\((.+?)-(.+?):\[(\d+),(\d+)\]\[(\d+),(\d+)\]\)',e)
                            class_name = matches[0][0]
                            text = matches[0][1]
                            driver.find_element(by=AppiumBy.XPATH, value=f"//{class_name}[@text=\"{text}\"]").click()
                        time.sleep(5)
                        history_action.append(e)
                        action = {'from': path[i], 'to': path[i + 1], 'event': e}
                        record.op.append(action)
                        image_path = tools.get_screenshot(sc_screenshot_path + '\\' + path[i + 1] + '.png')
                        activity_name = tools.get_activity()
                        if activity_name is None:
                            activity_name = ''
                        node = {"image": image_path, "activity": activity_name, "state_str": path[i + 1]}
                        record.node.append(node)
                        # i += 1
                    elif 'input' in e or "InputEvent" in e:
                        matches = re.findall(r'input\((.+?)-(.+?):\[(\d+),(\d+)\]\[(\d+),(\d+)\]\)\((.+?)\)',e)
                        xpath = '//android.widget.EditText[@resource-id=\"' + matches[0][1] + '\"]'
                        search_text = driver.find_element(by=AppiumBy.XPATH, value=xpath)
                        search_text.send_keys(matches[0][6])
                        time.sleep(5)
                        history_action.append(e)
                        action = {'from': path[i], 'to': path[i + 1], 'event': e}
                        record.op.append(action)
                        image_path = tools.get_screenshot(sc_screenshot_path + '\\' + path[i+1] + '.png')
                        activity_name = tools.get_activity()
                        if activity_name is None:
                            activity_name = ''
                        node = {"image": image_path, "activity": activity_name,"state_str": path[i+1]}
                        record.node.append(node)
                        # i += 1
                    elif 'scroll-up' in e:
                        width = driver.get_window_size()['width']
                        height = driver.get_window_size()['height']
                        driver.swipe(start_x=width * 0.5, start_y=height * 0.2, end_x=width * 0.5,end_y=height * 0.8, duration=1000)
                        time.sleep(5)
                        history_action.append(e)
                        action = {'from': path[i], 'to': path[i + 1], 'event': e}
                        record.op.append(action)
                        image_path = tools.get_screenshot(sc_screenshot_path + '\\' + path[i+1] + '.png')
                        activity_name = tools.get_activity()
                        if activity_name is None:
                            activity_name = ''
                        node = {"image": image_path, "activity": activity_name,"state_str": path[i + 1]}
                        record.node.append(node)
                        # i += 1
                    elif 'scroll-down' in e:
                        width = driver.get_window_size()['width']
                        height = driver.get_window_size()['height']
                        driver.swipe(start_x=width * 0.5, start_y=height * 0.8, end_x=width * 0.5, end_y=height * 0.2, duration=1000)
                        time.sleep(5)
                        history_action.append(e)
                        action = {'from': path[i], 'to': path[i + 1], 'event': e}
                        record.op.append(action)
                        image_path = tools.get_screenshot(sc_screenshot_path + '\\' + path[i+1] + '.png')
                        activity_name = tools.get_activity()
                        if activity_name is None:
                            activity_name = ''
                        node = {"image": image_path, "activity": activity_name,"state_str": path[i + 1]}
                        record.node.append(node)
                    elif 'scroll-left' in e:
                        width = driver.get_window_size()['width']
                        height = driver.get_window_size()['height']
                        a, b = tools.tap_coordinate(e)
                        driver.swipe(start_x=width * 0.9, start_y=b, end_x=width * 0.3, end_y=b, duration=1000)
                        time.sleep(5)
                        history_action.append(e)
                        action = {'from': path[i], 'to': path[i + 1], 'event': e}
                        record.op.append(action)
                        image_path = tools.get_screenshot(sc_screenshot_path + '\\' + path[i+1] + '.png')
                        activity_name = tools.get_activity()
                        if activity_name is None:
                            activity_name = ''
                        node = {"image": image_path, "activity": activity_name, "state_str": path[i + 1]}
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
                    #print(driver.page_source)
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
            content = example2 + '''Before you make a judgment, please think about the detailed steps required to complete the UI context reproduction firstly, and refer to the examples we provide. Then decide whether the following UI Context is reproduced.
             When you think that all the actions that need to be performed have been executed, you can output 'YES' to end it, without repeatedly performing the same actions. Output:YES/NO\n''' + \
                      '''comment:''' + comment + '''\nThe key sentence of the comment:''' + record.key_sentence + '''\nThe actions we have completed include:\n''' + actions + '''\nthe current status information:''' + CurrentPageHTML
            time.sleep(5)
            while True:
                try:
                    result = ask_gpt_4(content)
                    log.write(content + "\n" + result)
                    break
                except:
                    pass
            print(content + "\n" + result)
            if 'YES' in result or 'Yes' in result or 'yes' in result:
                flag = 1
                is_finished += 1
            elif 'NO' in result or 'No' in result or 'no' in result:
                flag = 0
            begin = DestState
            while not flag:
                CurrentPageSource = driver.page_source
                CurrentPageHTML, coordinate, x_max, y_max = tools.page(CurrentPageSource, page_num, 1)  # 当前页面的HTML presentation
                actions = ''
                for action in history_action:
                    actions = actions + action + '\n'
                content = example_select_action + 'User comment:' + comment + '\nThe key words of the comment:' + record.key_sentence + '\nWidgets information of current state:\n' + CurrentPageHTML + "\nThe actions we have done:\n" + actions + \
                          '\noutput format:\nThe steps to reproduce the Ui context:\n.....\nThe next action:\n"click ui_index" or "input ui_index input-text" or "scroll up/down or "long-click ui_index".Example:\nclick 1\ninput 1 "123"\nscroll up\nlong-click 2\n"scroll down" means sliding from the top of the page to the bottom. Note that only one action is output at a time. If you think the current page is wrong or want to return to the previous page, please output "back".'
                time.sleep(5)
                while True:
                    try:
                        result = ask_gpt_4(content)
                        log.write(content + "\n" + result)
                        break
                    except:
                        pass
                print(content + "\n" + result)
                # 获取LLM思考的执行步骤
                match = re.match(r'The steps to reproduce the UI context:\n(.+?)\nThe next action', result)
                # = 0  # 是否得到下一个要执行的动作
                while True:
                    if result in re_action.keys() and re_action[result] > 4:
                        is_finished += 1
                        flag = 1  # 本次复现结束
                        log.write("\n选择动作时陷入循环：" + comment + '\n' + record.key_sentence + '\n')
                        break
                    elif result not in re_action.keys():
                        re_action[result] = 0
                    # 判断动作是否已经执行过
                    if 'long-click' in result:
                        format = re.compile(r'long-click (\d+)')
                        try:
                            id = int(format.findall(result)[0])
                        except:  # 输出格式错误
                            result = ask_gpt4('Please output in right format.' + content)
                            log.write('Please output in right format.' + content + "\n" + result + '\n')
                            continue
                        if 'long-click' in re_action.keys() and re_action['long-click'] > 4:
                            is_finished += 1
                            flag = 1  # 本次复现结束
                            log.write("\n选择动作时陷入循环：" + comment + '\n' + record.key_sentence + '\n')
                            re_action['long-click'] = 0
                            break
                        elif 'long-click' not in re_action.keys():
                            re_action['long-click'] = 1
                        else:
                            re_action['long-click'] += 1
                        if len(history_action) != 0 and ('long-click' + coordinate[id].html == history_action[len(history_action) - 1]):
                            result = ask_gpt4('The action "long-click has been done.' + content)
                            log.write('The action "long-click has been done.' + content + "\n" + result + '\n')
                            continue
                    elif 'click' in result:
                        format = re.compile(r'click (\d+)')
                        try:
                            id = int(format.findall(result)[0])
                        except:  # 输出格式错误
                            result = ask_gpt4('Please output in right format.' + content)
                            log.write('Please output in right format.' + content + "\n" + result + '\n')
                            continue
                        if id not in range(len(coordinate)):
                            result = ask_gpt4('There is not a widget with id=' + str(id) + '.' + content)
                            log.write('There is not a widget with id=' + str(id) + '.' + content + "\n" + result + '\n')
                            continue

                        if 'click ' + str(id) in re_action.keys() and re_action['click ' + str(id)] > 4:
                            is_finished += 1
                            flag = 1  # 本次复现结束
                            log.write("\n选择动作时陷入循环：" + comment + '\n' + record.key_sentence + '\n')
                            re_action['click ' + str(id)] = 0
                            break
                        elif 'click ' + str(id) not in re_action.keys():
                            re_action['click ' + str(id)] = 1
                        else:
                            re_action['click ' + str(id)] += 1
                        # if len(history_action) != 0 and ('click' + coordinate[id].html == history_action[len(history_action) - 1]):
                        #     result = ask_gpt4('The action "click" ' + str(id) + '" has been done.' + content)
                        #     log.write('The action "click" ' + str(id) + '" has been done.' + content + "\n" + result + '\n')
                        #     continue
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

                        if 'input ' + str(id) in re_action.keys() and re_action['input ' + str(id)] > 4:
                            is_finished += 1
                            flag = 1  # 本次复现结束
                            log.write("\n选择动作时陷入循环：" + comment + '\n' + record.key_sentence + '\n')
                            re_action['input ' + str(id)] = 0
                            break
                        elif 'input ' + str(id) not in re_action.keys():
                            re_action['input ' + str(id)] = 1
                        else:
                            re_action['input ' + str(id)] += 1
                        if len(history_action) != 0 and ('input' + coordinate[id].html + text in history_action):
                            result = ask_gpt4('The action "input ' + str(id) + ' ' + text + '" has been done.' + content)
                            log.write('The action "input ' + str(id) + ' ' + text + '" has been done.' + content + "\n" + result + '\n')
                            continue
                    elif 'back' in result:
                        if 'back' in re_action.keys() and re_action['back'] > 4:
                            is_finished += 1
                            flag = 1  # 本次复现结束
                            log.write("\n选择动作时陷入循环：" + comment + '\n' + record.key_sentence + '\n')
                            re_action['back'] = 0
                            break
                        elif 'back' not in re_action.keys():
                            re_action['back'] = 1
                        else:
                            re_action['back'] += 1
                        if len(history_action) != 0 and history_action[len(history_action) - 1] == 'back':
                            result = ask_gpt4('The "back" action has been done.' + content)
                            log.write('The "back" action has been done.' + content + "\n" + result + '\n')
                            continue
                    try:  # 执行对应动作
                        if 'long-click' in result:
                            format = re.compile(r'long-click (\d+)')
                            try:
                                id = int(format.findall(result)[0])
                            except:
                                result = ask_gpt4('Please output in right format.' + content)
                                log.write('Please output in right format.' + content + "\n" + result + '\n')
                                continue
                            widget_coordinate = coordinate[id].bounds
                            a, b = tools.tap_coordinate(widget_coordinate)
                            # 获取当前屏幕大小
                            x = driver.get_window_size()['width']
                            y = driver.get_window_size()['height']
                            driver.tap([(int(a / x_max * x), int(b / y_max * y))], 2000)
                            time.sleep(5)
                            CurrentPageSource = driver.page_source
                            history_action.append('long-click' + coordinate[id].html)
                            action = {'from': begin, 'to': str(hash(CurrentPageSource)), 'event': 'long-click'}
                            record.op.append(action)
                            begin = action['to']
                            image_path = tools.get_screenshot(sc_screenshot_path + '\\' + str(hash(CurrentPageSource)) + '.png')
                            activity_name = tools.get_activity()
                            if activity_name is None:
                                activity_name = ''
                            node = {"image": image_path, "activity": activity_name, "state_str": str(hash(CurrentPageSource))}
                            record.node.append(node)
                            re_action['long-click'] = 0
                            break
                        elif 'click' in result:
                            format = re.compile(r'click (\d+)')
                            try:
                                id = int(format.findall(result)[0])
                            except:
                                result = ask_gpt4('Please output in right format.' + content)
                                log.write('Please output in right format.' + content + "\n" + result + '\n')
                                continue

                            widget_coordinate = coordinate[id].bounds
                            a, b = tools.tap_coordinate(widget_coordinate)
                            # 获取当前屏幕大小
                            x = driver.get_window_size()['width']
                            y = driver.get_window_size()['height']
                            driver.tap([(int(a / x_max * x), int(b / y_max * y))], 100)
                            time.sleep(5)
                            history_action.append('click' + coordinate[id].html)
                            CurrentPageSource = driver.page_source
                            action = {'from': begin, 'to': str(hash(CurrentPageSource)),'event': 'click' + coordinate[id].html}
                            record.op.append(action)
                            begin = action['to']
                            image_path = tools.get_screenshot(sc_screenshot_path + '\\' + str(hash(CurrentPageSource)) + '.png')
                            activity_name = tools.get_activity()
                            if activity_name is None:
                                activity_name = ''
                            node = {"image": image_path, "activity": activity_name, "state_str": str(hash(CurrentPageSource))}
                            record.node.append(node)
                            #re_action['click ' + str(id)] = 0
                            break

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
                            xpath = '//android.widget.EditText[@resource-id=\"' + coordinate[id].resource_id + '\"]'
                            search_text = driver.find_element(by=AppiumBy.XPATH, value=xpath)
                            search_text.click()
                            search_text.send_keys(text)
                            history_action.append('input' + coordinate[id].html + text)
                            time.sleep(5)
                            CurrentPageSource = driver.page_source
                            action = {'from': begin, 'to': str(hash(CurrentPageSource)),
                                      'event': 'input' + coordinate[id].html + text}
                            record.op.append(action)
                            begin = action['to']
                            image_path = tools.get_screenshot(sc_screenshot_path + '\\' + str(hash(CurrentPageSource)) + '.png')
                            activity_name = tools.get_activity()
                            if activity_name is None:
                                activity_name = ''
                            node = {"image": image_path, "activity": activity_name, "state_str": str(hash(CurrentPageSource))}
                            record.node.append(node)
                            re_action['input ' + str(id)] = 0
                            break
                        elif 'scroll' in result:
                            if 'up' in result:
                                size = driver.get_window_size()
                                height = driver.get_window_size().get('height')
                                weight = driver.get_window_size().get('width')
                                driver.swipe(start_x=weight * 0.5, start_y=height * 0.7, end_x=weight * 0.5, end_y=height * 0.3, duration=1000)
                                history_action.append('scroll up')
                                time.sleep(10)
                                CurrentPageSource = driver.page_source
                                action = {'from': begin, 'to': str(hash(CurrentPageSource)), 'event': 'scroll up'}
                                record.op.append(action)
                                begin = action['to']
                                image_path = tools.get_screenshot(sc_screenshot_path + '\\' + str(hash(CurrentPageSource)) + '.png')
                                activity_name = tools.get_activity()
                                if activity_name is None:
                                    activity_name = ''
                                node = {"image": image_path, "activity": activity_name, "state_str": str(hash(CurrentPageSource))}
                                record.node.append(node)
                            elif 'down' in result:
                                size = driver.get_window_size()
                                height = driver.get_window_size().get('height')
                                weight = driver.get_window_size().get('width')
                                driver.swipe(start_x=weight * 0.5, start_y=height * 0.3, end_x=weight * 0.5, end_y=height * 0.7, duration=1000)
                                history_action.append('scroll down')
                                time.sleep(10)
                                CurrentPageSource = driver.page_source
                                action = {'from': begin, 'to': str(hash(CurrentPageSource)), 'event': 'scroll down'}
                                record.op.append(action)
                                begin = action['to']
                                image_path = tools.get_screenshot(sc_screenshot_path + '\\' + str(hash(CurrentPageSource)) + '.png')
                                activity_name = tools.get_activity()
                                if activity_name is None:
                                    activity_name = ''
                                node = {"image": image_path, "activity": activity_name, "state_str": str(hash(CurrentPageSource))}
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
                            image_path = tools.get_screenshot(sc_screenshot_path + '\\' + str(hash(CurrentPageSource)) + '.png')
                            activity_name = tools.get_activity()
                            if activity_name is None:
                                activity_name = ''
                            node = {"image": image_path, "activity": activity_name, "state_str": str(hash(CurrentPageSource))}
                            record.node.append(node)
                            re_action['back'] = 0
                            break
                        else:
                            result = ask_gpt4(content)
                    except:
                        is_finished += 1
                        flag = 1  # 本次复现结束
                        log.write("\nappium阶段失败：" + comment)
                        break

                if len(history_action) < max_actions and flag == 0:
                    # 判断是否完成评论复现
                    actions = ''
                    for action in history_action:
                        actions = actions + action + '\n'
                    CurrentPageHTML, coordinate, x_max, y_max = tools.page(CurrentPageSource, page_num,1)  # 当前页面的HTML presentation
                    content = example2 + '''Please determine whether the following user comment UI context has been reproduced. When you think that all the actions that need to be performed have been executed, you can output 'YES' to end it, without repeatedly performing the same actions. Output:YES/NO\n''' +\
                              '''comment:''' + comment + '''\nThe key sentence of the comment:''' + record.key_sentence + '''\nThe actions we have completed include:\n''' + actions + '''\nthe current status information:''' + CurrentPageHTML
                    time.sleep(5)
                    result = ask_gpt4(content)
                    log.write(content + "\n" + result + '\n')
                    print(content + "\n" + result)
                    if 'YES' in result or 'Yes' in result or 'yse' in result:
                        flag = 1
                        is_finished += 1
                        break
                    elif 'NO' in result or 'No' in result or 'no' in result:
                        flag = 0
                elif len(history_action) > max_actions and flag == 0:
                    flag = 1
                    is_finished += 1
                    break

            ob.append(deepcopy({"round": is_finished, "comment": record.comment, "scenarios": record.scenario,
                                "key sentence": record.key_sentence, "target activity": record.targetac,
                                "the function of activity": record.acfunction, "target state": record.targetst,
                                "the sub-task list of state": deepcopy(record.statelist),
                                "nodes": deepcopy(record.node), "operations": deepcopy(record.op),
                                "Final answer": flag}))
            driver.keyevent(4)
            driver.keyevent(4)
            driver.keyevent(4)
            driver.quit()

        with open(scene_path + '.json', 'w') as f:
            json.dump(ob, f, indent=4, separators=(',', ': '))
    test_comment_num += 1
    comment_num += 1
log.close()
log_sc.close()




