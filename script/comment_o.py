import json
from gpt.gpt import ask_gpt,ask_gpt_4,ask_gpt_state,ask_gpt_info,ask_gpt_activity
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
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin

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
    forceAppLaunch='true',
    shouldTerminateApp='true',
    noReset='true',
    newCommandTimeout='6000'
)

os.environ.setdefault("OPENAI_API_KEY", "sk-NEI39Ft0cx0sezU8914aE7D447114662817cC404106984Ea")
os.environ.setdefault("OPENAI_BASE_URL", "https://oneapi.xty.app/v1")
# 开启driver
appium_server_url = 'http://127.0.0.1:4723'
driver = webdriver.Remote(appium_server_url, options=UiAutomator2Options().load_capabilities(capabilities))
log = open("log.txt", 'a', encoding='utf-8')
data_list = []
#manifest_file = "D:\\project\\MemoDroid\\\\AndroidManifest.xml"
page_index = 0
page_num = 1
history_action = []  # 记录执行过的历史动作
'''
with open("D:\\project\\appcrawler2\\GooglePlayCrawler-master\\test.csv", 'r', newline='') as comment_file:
    reader = csv.reader(comment_file)
    for row in reader:
        comment = row[2]
        if comment != 'Review':
                     data = [{'日期': row[0], 'score': row[1], 'comment': row[2], 'key information': key_info, 'activity': DestPage}]
                data = pd.DataFrame(data)
                data_list.append(copy.deepcopy(data))
    merged_df = pd.concat(data_list).drop_duplicates()
    merged_df.to_excel("comment_activity.xlsx", index=False)
'''
# command = "请你从这些用户评论中筛选出包含移动应用页面信息或组件信息的差评，以便我用来测试移动应用。"
# 根据comment确定初始activity
comment = '''I'll always love Pinterest. However, when attempting to pin to a board it's very slow to load, especially when selecting the section within a board, then again slow to load when pinning to the section. My internet is top of the range, so that's not the issue. I hardly use it anymore because of this frustration!'''
#comment = 'I have Google One subscription. When I open my photo from the Google photo and choose magic eraser, it will give a loading page for about 3 seconds, and then the app is closed. This is disappointing, as the core feature that I want to try after purchasing the Google One subscription is the magic eraser feature from the Google Photo. Please fix it. '
#comment = 'Flood your for you page with clips you arent interested in and will recycle them even when you click on the not interested button.'
#comment = "Love this app but I one thing I hate is that some features aren't available for everyone. I have tried everything to get photo mode to work and no matter what I do it's not available for me. It's available for friends in my area and every creator I follow. It's really frustrating because I'm a content creator myself and would like the opportunity to utilize these posts! There is no technical support either which is extremely frustrating"
#comment = " To name a few issues that I notice the most: the search engine is inaccurate."
#comment = "Good app and all EXCEPT how some different device types have more features. The one thing that I want is to be able to post a photo in a comment. I have a Google pixel and I'm not sure which type of phone (I'm pretty sure it's apple) that can post pictures in the comments but I would like that on every phone type. Overall, its a pretty good app. Would recommend if your fine with a few less features then others."
#comment = "For 2 months, I have not received notifications from the creators I have selected to get all notifications from. All my settings for notifications are set properly. Nothing has been turned off. I uninstalled and reinstalled with no change to receiving notification. Submitted screen shots to tiktok help, only for them to ask for more screen shots of the same pics I already submitted. Is anyone else having this problem?"
command = "Based on the user comment and the functions of each activity in application, determine which activity the comment describes.Only output activity name.(e.g. .uioverrides.QuickstepLauncher)"
command1 = "Please extract the mobile application page information or component information mentioned in the comment.The key information should be the name of a page or component of the application.Only output one phrase."
command2 = 'Based on the user comment and the functions of each state in application, determine which state the comment describes.Only output state name.(e.g.state1/45b7f0f22a9dbb70bd79a2785ca109fc)'
example1 = "\nExample:\ncomment:THE worst part is when I share a tiktok with someone, I have to scroll back and forth between tiktoks to make the share menu go away and the share menu freezes in place making it frustrating and impossible to share videos with people. key information:share menu"

# 构建有向图,有向图的节点是state
#graph = {}
node = {}
event = {}
# 构建有向图
G = nx.DiGraph()

with open("..\\app\\Pinterest_activity\\activity_function.json") as js_file:
    activity_function = json.load(js_file)

with open("..\\app\\Pinterest_activity\\state_widgets.json") as js_file:
    state_widgets = json.load(js_file)

with open("..\\app\\Pinterest_activity\\utg.js", "r") as js_file:
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
    for element in re.findall(r'"from": "(.+?)".+?"to": "(.+?)".+?"event_str": "(.+?)"', js_code, re.DOTALL):     # 添加边
        '''
        if element[0] not in graph:
            graph[(element[0])] = []
            graph[(element[0])].append(element[1])
            event[(element[0], element[1])] = element[2]
        else:
            if element[1] in graph[(element[0])]:
                continue
            else:
                graph[(element[0])].append(element[1])
                event[(element[0], element[1])] = element[2]
        '''
        if G.has_edge(element[0], element[1]):
            continue
        else:
            G.add_edge(element[0], element[1])
            event[(element[0], element[1])] = element[2]

# utg补充（人工手动）
with open('..\\app\\Pinterest_activity\\utg_add.js', "r", encoding='utf-8') as js_file:
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
        '''
        if element[0] not in graph:
            graph[(element[0])] = []
            graph[(element[0])].append(element[1])
            event[(element[0], element[1])] = element[2]
        else:
            if element[1] in graph[(element[0])]:
                continue
            else:
                graph[(element[0])].append(element[1])
                event[(element[0], element[1])] = element[2]
        '''
        if G.has_edge(element[0], element[1]):
            continue
        else:
            G.add_edge(element[0], element[1])
            event[(element[0], element[1])] = element[2]

# 获取activity task
with open("..\\app\\Pinterest_activity\\page_task.json", 'r', encoding='utf-8') as file:
    page_function = json.load(file)
    # 只用任务名称
    t = ''
    activities = []
    texts = []
    for key,value in page_function.items():
        t = t + key + ":"
        activities.append(key)
        if len(value) != 0:
            texts.append(key + ":" + str(value))
        for v in value:
            t = t + v["name"] + ","
        t = t + "\n"

activity_num = len(activities)  # activity数量
ac = ''
for activity in activities:
    ac = ac + activity + "\n"

# 提取应用的关键信息
content = command1 + example1 + "\nYou need to extract the key information of the following comment:" + comment
print(content)
key_info = ask_gpt(content)

# embedding
# 存入向量数据库
vectorstore = Chroma.from_texts(
    texts,
    embedding=OpenAIEmbeddings()
)
#query = "task about " + key_info
query = comment + "key information:" + key_info + "Which activity is the comment describe?"
docs = vectorstore.similarity_search(query)
message = ''
for doc in docs:
    matches = re.findall(r'(.+):\[(.+)\]', doc.page_content)
    message = message + matches[0][0] + ':' + activity_function[matches[0][0]] + '\ntask list:' + matches[0][1] + '\n\n'
example = command + \
          "\nExample:comment:Flood your for you page with clips you arent interested in and will recycle them even when you click on the not interested button.\n" + \
            "comment key information:not interested button\n" + \
            "\nthought:the task 'Not interested' in 'com.ss.android.ugc.aweme.splash.SplashActivity' is related to the comment key information,so the activity the comment describes is 'com.ss.android.ugc.aweme.splash.SplashActivity'.\n" + \
            "output:com.ss.android.ugc.aweme.splash.SplashActivity\n"
content = command + "Here is a task list for some activities:\n" + message + "\nYou need to determine which activity the following comment describes:" + comment + "\nThe key information of this comment: '" + key_info
print(content)
DestPage = ask_gpt_activity(content)  # 确定目标activity
log.write(content + "\n" + DestPage)
while DestPage not in node.keys():
    DestPage = ask_gpt_activity('This in not an activity name,please select again.' + content)
    time.sleep(5)

# 确定目标state
with open("..\\app\\Pinterest_activity\\state_task.json", 'r', encoding='utf-8') as file:
    state_task = json.load(file)
    states = []
    for state_end in node[DestPage]:
        try:
            states.append(state_end + ":" + str(state_task[state_end]))
        except:
            pass
if len(states) > 3:
    vectorstore_state = Chroma()
    vectorstore_state = vectorstore_state.from_texts(
        states,
        embedding=OpenAIEmbeddings()
    )
    #query = "task about " + key_info
    query = comment + "key information:" + key_info + "Which state is the comment describe?"
    docs_state = vectorstore_state.similarity_search(query, k=3)
    message = ''
    for doc_state in docs_state:
        flag = 0
        # 判断是否含有activity
        for key, value in activity_function.items():
            if key in doc_state.page_content:
                flag = 1
                break
        if flag == 0:
            print(doc_state.page_content)
            message = message + doc_state.page_content + "\n"
    content = command2 + "Here is a task list for states:\n" + message + "\nYou need to determine which state the following comment describes:" + comment + "\nThe key information of this comment: '" + key_info
    DestState = ask_gpt_state(content)
    log.write(content + "\n" + DestState)
elif len(states) == 3 or len(states) == 2:
    message = ''
    for state in states:
        print(state)
        message = message + state + "\n"
    content = command2 + "Here is a task list for states:\n" + message + "\nYou need to determine which state the following comment describes:" + comment + "\nThe key information of this comment: '" + key_info
    DestState = ask_gpt_state(content)
    log.write(content + "\n" + DestState)
else:
    DestState = state_end
print(content)
while not G.has_node(DestState):
    DestState = ask_gpt_state('This is not a state name, please choose again.' + content)
    #print(DestState)
#DestPage = "com.ss.android.ugc.aweme.splash.SplashActivity"
# 用prompt到达确定的activity页面
#activities = transfer.get_activity_names(manifest_file)  # 获取应用所有activity名称

#CurrentPage = driver.current_activity  # 当前页面activity
#CurrentPage = "fdedbaae0d7db088bdc1a119bf22aa84"  # google photos的初始页面
#CurrentPage = "a17e568448adcdbafe37f9f618f3f5ca"  # spotify的初始页面
#CurrentPage = "86ad15cba4ecd2166c92cbbf7eddfa20"
CurrentPage = "ba5f165ac71b67896bd0c28f07857be5"  # Pinterest
page_html_file = json.load(open("..\\app\\Pinterest_activity\\page_html.json", 'r', encoding='utf-8'))
# 用appium到达目标页面
if CurrentPage != DestState:
    path = nx.shortest_path(G, CurrentPage, DestState)
    print(path)
    i = 0
    while i < len(path)-1:
        e = event[(path[i], path[i + 1])]   # explore阶段执行的动作，作为提示信息提供给大模型
        if 'TouchEvent' in e:
            try:
                coordinate = re.findall(r':x(\d+):y(\d+)', e)
                a = int(coordinate[0][0])
                b = int(coordinate[0][1])
                x_max = 1080
                y_max = 2280
                #y_max = 2148

            except:
                a, b = tools.tap_coordinate(e)
                x_max = 1080
                y_max = 2280
                #y_max = 2148
            x = driver.get_window_size()['width']
            y = driver.get_window_size()['height']
            driver.tap([(int(a / x_max * x), int(b / y_max * y))], 100)
            time.sleep(10)
            history_action.append(e)
            #i += 1
        elif 'input' in e:
            matches = re.findall(r'Input\((.+?)-(.+?):\[(\d+),(\d+)\]\[(\d+),(\d+)\]\)(.+?)')
            xpath = '//android.widget.EditText[@resource-id=\"' + matches[1] + '\"]'
            search_text = driver.find_element(by=AppiumBy.XPATH, value=xpath)
            search_text.send_keys(matches[6])
            time.sleep(5)
            history_action.append(e)
        elif 'long-click' in e:
            a, b = tools.tap_coordinate(e)
            x_max = 1080
            y_max = 2280
            x = driver.get_window_size()['width']
            y = driver.get_window_size()['height']
            driver.tap([(int(a / x_max * x), int(b / y_max * y))], 1000)
            time.sleep(5)
            history_action.append(e)
            #i += 1
        elif 'Scroll-up' in e:
            width = driver.get_window_size()['width']
            height = driver.get_window_size()['height']
            driver.swipe(width / 2, height * 3 / 4, width / 2, height / 4, 1000)
            #driver.swipe(width / 2, height * 3 / 4, width / 3, height * 3 / 4, 1000);

            #a, b = tools.tap_coordinate(e)
            # Scroll-up(android.view.View-com.google.android.apps.photos:id/handle:[0,1895][1080,1906])
            #widgets = re.findall(r'.+\((.+?)-.+:(.+?)\)', e)
            #elmt = driver.find_element(by=AppiumBy.XPATH, value="//" + widgets[0][0] + "[@bounds='" + widgets[0][1] + "']")
            # 向下滚动
            #scroll_origin = ScrollOrigin.from_element(elmt)
            #ActionChains(driver).scroll_from_origin(scroll_origin, 0, 300000).perform()

            #a,b = tools.tap_coordinate(e)
            #driver.swipe(a, b, a, b+100)
            # 滑动元素
            #elmt = driver.find_element(by=AppiumBy.XPATH, value="//" + widgets[0][0] + "[@bounds='" + widgets[0][1] + "']")
            # 目标位置元素
            #dest_ele = driver.find_element(by=AppiumBy.XPATH, value='//android.view.ViewGroup[@bounds="[0,812][1080,1010]"]')
            #action = TouchAction(driver)
            # 长按日期元素滑动至确定按钮元素位置，然后释放
            #action.long_press(elmt).move_to(dest_ele).release().perform()
            time.sleep(5)
            history_action.append(e)
            #i += 1
        elif 'Scroll-left' in e:
            a,b = tools.tap_coordinate(e)
            driver.swipe(a, b, a+1080, b)
            time.sleep(5)
            history_action.append(e)
        # 动作完成后，判断是否到达下一个状态
        source = driver.page_source
        CurrentState, coordinate = tools.traverse_html(source,1)
        current_widgets = tools.source_widgets(source)
        temp = i
        state_widgets[path[i+1]]
        similarity = tools.state_similarity(current_widgets, state_widgets[path[i+1]])
        if similarity > 0.7:
            i += 1
        else:
            for j in range(i, len(path)):
                similarity = tools.state_similarity(current_widgets,state_widgets[path[j]])
                if similarity > 0.7:
                    i = j
                    break
            if j == temp:   # 点击组件后页面状态未发生变化
                print('到达目标状态时：点击组件页面未发生变化 ' + path[i] + ' to ' + path[i+1])
                driver.quit()
                log.close()
                exit(1)
            elif i == temp:    # 没有找到相似页面
                print('未成功到达目标页面')
                driver.quit()
                log.close()
                exit(1)


        #elif 'Scroll' in e:
        '''
        # 用大模型分析动作
        CurrentPageSource = driver.page_source  # 当前页面的xml文件
        CurrentPageHTML, coordinate, x_max, y_max = tools.page(CurrentPageSource,page_num,1)  # 当前页面的HTML presentation
        actions = ''
        for action in history_action:
            actions = actions + action + '\n'
        content = 'These are actions we have done:\n' + actions + 'You need to select an actions and the index of the target UI element to reach next page.\n' +\
            'Widgets information of current page:\n' + CurrentPageHTML + '\nTasks that can be completed in the next page:\n' + str(state_task[(path[i+1])]) +\
            '\n\nIn a previous attempt, executing action ' + e + ' can reach the next page from the current page.\n' +\
            '\noutput format:"click ui_index" or "input ui_index input-text" or "scroll up/down".Example:\nclick ui_index=1\ninput ui_index=1 "123"\nscroll up\n'
        result = ask_gpt_4(content)
        log.write(content + "\n" + result)
        print(content + "\n" + result)
        if 'click' in result:
            format = re.compile(r'click ui_index=(\d+)')
            id = int(format.findall(result)[0])
            widget_coordinate = coordinate[id].bounds
            a, b = tools.tap_coordinate(widget_coordinate)
            # 获取当前屏幕大小
            x = driver.get_window_size()['width']
            y = driver.get_window_size()['height']
            driver.tap([(int(a / x_max * x), int(b / y_max * y))], 100)
            history_action.append('click' + coordinate[id].html)
            time.sleep(10)
        elif 'input' in result:
            format = re.compile(r'input ui_index=(\d+) \"(.+?)\"')
            id = format.findall(result)
            id = int(id[0][0])
            text = id[0][1]
            xpath = '//android.widget.EditText[@resource-id=\"' + coordinate[id].resource_id + '\"]'
            search_text = driver.find_element(by=AppiumBy.XPATH, value=xpath)
            search_text.send_keys(text)
            history_action.append('input' + coordinate[id].html + text)
            time.sleep(10)
        elif 'scroll' in result:
            if 'up' in result:
                ActionChains(driver).scroll_from_origin(0, 0, 300000).perform()
                history_action.append('scroll up')
            elif 'down' in result:
                ActionChains(driver).scroll_from_origin(0, 0, -300000).perform()
                history_action.append('scroll down')
            time.sleep(2)
        
        # 反思执行的动作是否正确
        C = CurrentPageSource
        CurrentPageSource = driver.page_source  # 当前页面的xml文件
        CurrentPageHTML, coordinate, x_max, y_max = tools.page(CurrentPageSource, page_num,1)  # 当前页面的HTML presentation
        content = 'Please judge whether we have reached the target page based on the component information of the current page.Generally speaking, if the current page can complete most(not all) of the functions of the target page, it can be considered that the target page has been reached.\n' + \
                    'Tasks of the target page:\n' + str(state_task[(path[i + 1])]) + '\nthe current page status information:\n' + CurrentPageHTML + \
                    '\nOutput:YES/NO'
        result = ask_gpt(content)
        while ('YES'.casefold() in result and 'NO'.casefold() in result) or ('YES'.casefold() not in result and 'NO'.casefold() not in result):
            result = ask_gpt(content)

        if 'YES'.casefold() in result and 'NO'.casefold() not in result:
            i += 1
        elif 'NO'.casefold() in result and 'YES'.casefold() not in result:
            if C != CurrentPageSource:  # 页面未发生变化
                driver.keyevent(4)
                # history_action.append('back')
                history_action.pop()
        '''

# 到达目标页面后，大模型根据用户评论完成复现
# 判断是否完成评论复现
flag = 0  # 评论复现是否完成
actions = ''
for action in history_action:
    actions = actions + action + '\n'
CurrentPageSource = driver.page_source
CurrentPageHTML, coordinate, x_max, y_max = tools.page(CurrentPageSource, page_num,1)  # 当前页面的HTML presentation
content = 'This is the current status information. Please determine whether the entire process of comment reproduction has been completed.' +\
          'We only need to arrive at the scene described by the comment without paying attention to the result.' +\
          'For example,for comment:Flood your for you page with clips you arent interested in and will recycle them even when you click on the not interested button,the entire process of this comment reproduction includes find out the "not interested" button and click it.' +\
          'Please output:YES/NO\n' + 'comment:' + comment +\
          '\nThe actions we have completed inmaclude:\n' + actions + '\nthe current status information:' + CurrentPageHTML
result = ask_gpt(content)
log.write(content + "\n" + result)
print(content + "\n" + result)
#while ('YES' in result and 'NO' in result) or ('YES' not in result and 'NO' not in result):
#    result = ask_gpt(content)
if 'YES' in result or 'Yes' in result or 'yes' in result:
    flag = 1
elif 'NO' in result or 'No' in result or 'no' in result:
    flag = 0

while not flag:
    CurrentPageSource = driver.page_source
    CurrentPageHTML, coordinate, x_max, y_max = tools.page(CurrentPageSource, page_num,1)  # 当前页面的HTML presentation
    actions = ''
    for action in history_action:
        actions = actions + action
    content = 'You need to select an action and the index of the target UI element to reproduce a user comment.\n' +\
            'User comment:' + comment + '\nWidgets information of current state:\n' + CurrentPageHTML + "\nThe actions we have done:\n" + actions +\
            '\noutput format:"click ui_index" or "input ui_index input-text" or "scroll up/down".Example:\nclick ui_index=1\ninput ui_index=1 "123"\nscroll up\nNote that only one action is output at a time'
    result = ask_gpt_4(content)
    log.write(content + "\n" + result)
    print(content + "\n" + result)
    # = 0  # 是否得到下一个要执行的动作
    while True:
        # 判断动作是否已经执行过
        if 'click' in result:
            format = re.compile(r'click ui_index=(\d+)')
            try:
                id = int(format.findall(result)[0])
            except:  # 输出格式错误
                result = ask_gpt_4('Please output in right format.' + content)
                continue
            if id not in range(len(coordinate)):
                result = ask_gpt_4(('There is not a widget with id=' + id + content))
                continue
            if len(history_action) != 0 and ('click' + coordinate[id].html == history_action[len(history_action)-1]):
                result = ask_gpt_4('This action has been done.' + content)
                continue
        elif 'input' in result:
            format = re.compile(r'input ui_index=(\d+) \"(.+?)\"')
            try:
                id = format.findall(result)
                id = int(id[0])
                text = id[1]
            except:
                result = ask_gpt_4('Please output in right format.' + content)
                continue
            if id not in range(len(coordinate)):
                result = ask_gpt_4(('There is not a widget with id=' + id + content))
                continue
            if len(history_action) != 0 and ('input' + coordinate[id].html + text in history_action):
                result = ask_gpt_4('This action has been done.' + content)
                continue

        if 'click' in result:
            format = re.compile(r'click ui_index=(\d+)')
            try:
                id = int(format.findall(result)[0])
            except:
                result = ask_gpt_4('Please output in right format.' + content)
                continue
            widget_coordinate = coordinate[id].bounds
            a, b = tools.tap_coordinate(widget_coordinate)
            # 获取当前屏幕大小
            x = driver.get_window_size()['width']
            y = driver.get_window_size()['height']
            driver.tap([(int(a / x_max * x), int(b / y_max * y))], 100)
            history_action.append('click' + coordinate[id].html)
            time.sleep(10)
            break
        elif 'input' in result:
            format = re.compile(r'input ui_index=(\d+) \"(.+?)\"')
            try:
                id = format.findall(result)
                id = int(id[0])
                text = id[1]
            except:
                result = ask_gpt_4('Please output in right format.' + content)
                continue
            #if 'input' + coordinate[id].html + text in history_action:
            #ask_gpt('This action has been done.')
        #else:
            xpath = '//android.widget.EditText[@resource-id=\"' + coordinate[id].resource_id + '\"]'
            search_text = driver.find_element(by=AppiumBy.XPATH, value=xpath)
            search_text.send_keys(text)
            history_action.append('input' + coordinate[id].html + text)
            time.sleep(10)
            break
        elif 'scroll' in result:
            if 'up' in result:
                size = driver.get_window_size()
                height = driver.get_window_size().get('height')
                weight = driver.get_window_size().get('width')
                driver.swipe(start_x=weight * 0.5, start_y=height*0.9, end_x=weight * 0.5, end_y=height*0.1, duration=2000)
                history_action.append('scroll up')
                time.sleep(10)
            elif 'down' in result:
                size = driver.get_window_size()
                height = driver.get_window_size().get('height')
                weight = driver.get_window_size().get('width')
                driver.swipe(start_x=weight * 0.5, start_y=height * 0.1, end_x=weight * 0.5, end_y=height * 0.9,duration=2000)
                history_action.append('scroll down')
                time.sleep(10)
            break
        else:
            result = ask_gpt_4(content)

    # 判断是否完成评论复现
    actions = ''
    for action in history_action:
        actions = actions + action + '\n'
    CurrentPageSource = driver.page_source
    CurrentPageHTML, coordinate, x_max, y_max = tools.page(CurrentPageSource, page_num,1)  # 当前页面的HTML presentation
    content = 'This is the current status information. Please determine whether the entire process of comment reproduction has been completed.' + \
              'We only need to arrive at the scene described by the comment without paying attention to the result.Output:YES/NO\n' + 'comment:' + comment +\
              '\nThe actions we have completed include:\n' + actions + '\nthe current status information:' + CurrentPageHTML
    result = ask_gpt_4(content)
    log.write(content + "\n" + result)
    print(content + "\n" + result)
    #while ('YES' in result and 'NO' in result) or ('YES' not in result and 'NO' not in result):
    #    result = ask_gpt(content)
    if 'YES' in result or 'Yes' in result or 'yse' in result:
        flag = 1
    elif 'NO' in result or 'No' in result or 'no' in result:
        flag = 0



'''
# 用大模型到达目标页面
while CurrentPage != DestPage:
    content = "There are " + str(activity_num) + " pages in the app, named:" + ac + ".I want to go from the " + CurrentPage + " page to the " + DestPage + " page.What is the next page? Output format:activity name"
    NextPage = ask_gpt(content)
    log.write(content + "\n" + NextPage)
    print(content + "\n" + NextPage)

    # There are <#NumOfPageNames> pages in the app, named: <PageNames> . I want to go from the <CurrentPage> page to the <CrashPage> page.
    # The next page may be the <NextPage> page. Here are widgets I can click:<InteractableWidgets> . What should I click?
    source = driver.page_source
    page_html,coordinate,x_max,y_max = tools.page(source,page_index,1)
    page_index += 1
    # 根据page_html获取页面的子任务列表
    command1 = '\nPlease enumerate operations (sub-tasks) that does not exist in the activity sub-task list and can be performed on the screen.Each sub-task includes the following information: 1) sub-task name(A short summary of sub-tasks), 2) sub-task description(describe the sub-task in detail), 3) index of its relevant UI elements, 4) parameter names, and 5) questions required to obtain each parameter.\nOutput format:{name:" ",description:" ",parameters:{ }} \
                    \nExample:"1. { name: "Search", description: "Search for a contact", parameters: { "contact_name": "who are you looking for?" }, UI_index: 3 } \n2. { name: "Menu", description: "Open menu", parameters: {}, UI_index: 7 }"'
    result = ask_gpt(command1 + "\nscreen information:" + page_html)

    content = 'There are ' + str(activity_num) + ' page in the app, named:' + ac + '.I want to go from the ' + CurrentPage + ' page to the ' + DestPage + \
            ' page.The next page may be the ' + NextPage + ' page. Here are subtasks I can perform:\n' + result + \
                '. Which subtask should I perform?You should pick a sub-task from the list and fills in its required parameters.Output format:{name:" ",description:" ",parameters:{ }}.' + \
                'Example:{ name: "Search", description: "Search for a contact", parameters: { "contact_name": "who are you looking for?" }, UI_index: 3 }'
    result = ask_gpt(content)
    log.write(content + "\n" + result)
    print(content + "\n" + result)
    # derive
    content = 'You need to select an actions and the index of the target UI element to accomplish the sub-task.\nsub-task:' + result + \
              '\nlist of actions:click,input,scroll,long-click' + \
                '\ncurrent screen :\n' + page_html + '\noutput format:"click ui_index" or "input ui_index input-text" or "scroll up/down".Example:\nclick ui_index=1\ninput ui_index=1 "123"\nscroll up\n'
    result = ask_gpt(content)
    log.write(content + "\n" + result)
    print(content + "\n" + result)
    if 'click' in result:
        format = re.compile(r'click ui_index=(\d+)')
        id = int(format.findall(result)[0])
        widget_coordinate = coordinate[id].bounds
        a, b = tools.tap_coordinate(widget_coordinate)
        # 获取当前屏幕大小
        x = driver.get_window_size()['width']
        y = driver.get_window_size()['height']
        driver.tap([(int(a / x_max * x), int(b / y_max * y))], 100)
        time.sleep(10)
    elif 'input' in result:
        format = re.compile(r'input ui_index=(\d+) \"(.+?)\"')
        id = format.findall(result)
        id = int(id[0])
        text = id[1]
        xpath = '//android.widget.EditText[@resource-id=\"' + coordinate[id].resource_id + '\"]'
        search_text = driver.find_element(by=AppiumBy.XPATH, value=xpath)
        search_text.send_keys(text)
        time.sleep(10)
    elif 'scroll' in result:
        ActionChains(driver).scroll_from_origin(0, 0, 300000).perform()
        time.sleep(2)
'''
driver.quit()
log.close()











