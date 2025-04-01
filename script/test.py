import tools
from gpt.gpt import ask_gpt
import os


# file_path = "D:\\project\\MemoDroid\\app\\chrome_activity\\activity\\org.chromium.chrome.browser.app.bookmarks.BookmarkActivity\\state8.xml"
# command = '\nPlease enumerate operations (sub-tasks) can be performed on the screen.Each sub-task includes the following information: 1) sub-task name(A short summary of sub-tasks), 2) sub-task description(describe the sub-task in detail).\nOutput format:{name:" ",description:" "} \
#          \nExample:"1. { name: "Search", description: "Search for a contact"} \n2. { name: "Menu", description: "Open menu"}"'
#
# page_html = tools.traverse_xml(file_path)
# #page_html = tools.traverse_json(file_path)
# print(page_html)
# content = command + page_html
# result = ask_gpt(content)
# print(result)




# from appium import webdriver
# from appium.webdriver.common.touch_action import TouchAction
# from appium.options.android import UiAutomator2Options
# import time
# from appium.webdriver.common.appiumby import AppiumBy
# # 确定应用包名和launch activity
# # 确定应用包名和launch activity
# capabilities = dict(
#     platformName='Android',
#     automationName='uiautomator2',
#     deviceName='99141FFAZ00ATK',
#     #appPackage='com.google.android.apps.photos',
#     #appActivity='com.google.android.apps.photos.home.HomeActivity',
#     #appPackage='com.zhiliaoapp.musically',
#     #appActivity='com.ss.android.ugc.aweme.splash.SplashActivity',
#     #appPackage='com.spotify.music',
#     #appActivity='.MainActivity',
#     appPackage='com.pinterest',
#     appActivity='.activity.task.activity.MainActivity',
#     forceAppLaunch='true',
#     shouldTerminateApp='true',
#     noReset='true',
#     newCommandTimeout='6000'
# )
#
# # 初始化 WebDriver
# appium_server_url = 'http://127.0.0.1:4723'
# driver = webdriver.Remote(appium_server_url, options=UiAutomator2Options().load_capabilities(capabilities))
# # 滑动屏幕函数
# def swipe_up(driver, duration=500):
#     size = driver.get_window_size()
#     height = driver.get_window_size().get('height')
#     weight = driver.get_window_size().get('width')
#     #start_x = size['width'] / 2
#     #start_y = size['height'] * 0.8
#     #end_x = size['width'] / 2
#     #end_y = size['height'] * 0.2
#     driver.swipe(start_x=weight * 0.9,start_y=1661,end_x=weight * 0.1,end_y=1661, duration=2000)
#
#     #actions = TouchAction(driver)
#     #actions.press(x=start_x, y=start_y).wait(ms=duration).move_to(x=end_x, y=end_y).release().perform()
#
# def test_scroll_ele(self):
#     # 点击进入 Views 界面
#     self.driver.find_element(AppiumBy.ACCESSIBILITY_ID, 'Views').click()
#     # 滑动起始元素
#     image_btn = self.driver.find_element(AppiumBy.ACCESSIBILITY_ID, 'ImageButton')
#     # 滑动结束元素
#     button = self.driver.find_element(AppiumBy.ACCESSIBILITY_ID, 'Buttons')
#     # 执行滑动操作
#     self.driver.scroll(image_btn, button, duration=2000)
#     list_ele = self.driver.find_element(AppiumBy.ACCESSIBILITY_ID, 'Picker')
#     assert list_ele.text == 'Picker'
# # 等待应用启动
# time.sleep(10)
# print(tools.source_widgets(driver.page_source))
#
# # 滑动屏幕
# #swipe_up(driver)
#
# # 关闭驱动
# driver.quit()





import json

from gpt.gpt import ask_gpt, ask_gpt_state, ask_gpt_info, ask_gpt_activity,ask_gpt4
import re
import tools
from appium import webdriver
from appium.options.android import UiAutomator2Options
import time
from appium.webdriver.common.appiumby import AppiumBy
import os
import pandas as pd
from copy import deepcopy
from commands import command,command1,command2,example1,example2,command6,get_scenarios,scenario_is_reproducible,example_select_action
import shutil
import random
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
    deviceName='99141FFAZ00ATK',
    #appPackage='com.google.android.apps.photos',
    #appActivity='com.google.android.apps.photos.home.HomeActivity',
    #appPackage='com.zhiliaoapp.musically',
    #appActivity='com.ss.android.ugc.aweme.splash.SplashActivity',
    # appPackage='com.spotify.music',
    # appActivity='.MainActivity',
    appPackage='com.pinterest',
    appActivity='.activity.task.activity.MainActivity',
    # appPackage='com.lemon.lvoverseas',
    # appActivity='com.vega.main.MainActivity',
    # appPackage='com.google.android.apps.translate',
    # appActivity='com.google.android.apps.translate.TranslateActivity',
    # appPackage='com.instagram.android',
    # appActivity='com.instagram.mainactivity.InstagramMainActivity',
    # appPackage = 'com.android.chrome',
    # appActivity = 'com.google.android.apps.chrome.Main',
    forceAppLaunch='true',
    shouldTerminateApp='true',
    noReset='true',
    newCommandTimeout='6000'
)

os.environ.setdefault("OPENAI_API_KEY", "sk-oh7AbfOOYzPLt23v2075Ec7f1eEc4e64A1Dd44865cFb8eDc")
os.environ.setdefault("OPENAI_BASE_URL", "https://oneapi.xty.app/v1")
# 各个应用的初始页面
startpage  = {"chrome_activity": "4e5cd78cfbca801ea96edfce1920b231", "photos_activity": "fdedbaae0d7db088bdc1a119bf22aa84", "pinterest_activity": "ba5f165ac71b67896bd0c28f07857be5", "tiktok_activity": "86ad15cba4ecd2166c92cbbf7eddfa20", "translate_activity": "1e0a8968f43dbb61fd758c305c65c40a", "spotify_activity": "a17e568448adcdbafe37f9f618f3f5ca", "instagram_activity": "111111" , "capcut_activity": "222222"}
#chroma_client = chromadb.Client()
#collection = chroma_client.create_collection(name="my_collection")
appium_server_url = 'http://127.0.0.1:4723'
app_name = 'pinterest_activity'
log = open(f"..\\app\\{app_name}\\LLM-output\\log.txt", 'a', encoding='utf-8')
log_sc = open(f"..\\app\\{app_name}\\LLM-output\\log_sc.txt", 'a', encoding='utf-8')
page_num = 1
history_action = []  # 记录执行过的历史动作
comment_num = 0
test_comment_num = 300   # 测试的用户评论的数量
screenshot_dir = f'..\\app\\{app_name}\\LLM-output\\screenshot'
comment = ''
max_actions = 13   # 最多执行动作数
# 根据comment确定初始activity
# 从文件中随机获取用户评论
df = pd.read_excel("D:\\project\\MemoDroid\\app\\data.xlsx", sheet_name=5)
key_sentence = ''
re_action = {}
ob = []

while True:
    if test_comment_num == 301:
        break
    # 选择用户评论
    # random_index = random.randint(0, len(df) - 1)
    #comment = df.iloc[comment_num]['comment']
    comment = '''Delete a board'''
    print(comment)
    #scenarios = ['''When translating from Chinese to English or using the thesaurus, the app doesn't always provide pinyin for Chinese symbols.''']
    #if df.iloc[comment_num]['备注'] == '评论不可复现':
    #    break
    #comment = df.iloc[comment_num]['comment']
    # 获取用户评论中所有不连续的场景
    scenarios = get_scenarios(app_name[:-9], comment)
    log_sc.write(comment + '\n' + str(scenarios) + '\n')
    if len(scenarios) == 0:
        continue
    record = Record(comment)
    # # 判断场景是否可以复现，并将所有可以复现的场景保存到record中
    # for sc in scenarios:
    #     if scenario_is_reproducible(sc):
    #         record.scenario.append(sc)
    record.scenario = scenarios
    if len(record.scenario) == 0:  # 用户评论中没有可以复现的场景
       comment_num += 1
       continue
    screenshot_path = screenshot_dir + '\\comment' + str(test_comment_num)
    if not os.path.exists(screenshot_path):  # 创建保存屏幕截图的目录
        os.mkdir(screenshot_path)
    result_path = f'..\\app\\{app_name}\\LLM-output\\record\\comment' + str(test_comment_num)
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
    # 依次复现用户评论中可以复现的场景
    for i in range(len(record.scenario)):
        is_finished = 0
        ob = []
        record.node = []
        record.op = []
        # 创建相关目录
        if not os.path.exists(screenshot_path + '\\scene' + str(i)):
            os.mkdir(screenshot_path + '\\scene' + str(i))
        else:
            # If the directory exists, remove all files within it
            path = screenshot_path + '\\scene' + str(i)
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
        sc_screenshot_path = screenshot_path + '\\scene' + str(i)
        scene_path = result_path + '\\scene' + str(i)
        is_finished = 0
        record.key_sentence = record.scenario[i]
        while is_finished < 2:
            history_action = []

            driver = webdriver.Remote(appium_server_url,options=UiAutomator2Options().load_capabilities(capabilities))  # 开启driver
            time.sleep(5)  # 等待开启广告

            CurrentPage = startpage[app_name]
            image_path = tools.get_screenshot(sc_screenshot_path + '\\' + CurrentPage + '.png')
            activity_name = tools.get_activity()
            if activity_name is None:
                activity_name = ''
            node = {"image": image_path, "activity": activity_name , "state_str": CurrentPage}
            record.node.append(node)
            #page_html_file = json.load(open(f"..\\app\\{app_name}\\page_html.json", 'r', encoding='utf-8'))
            time.sleep(5)

            # 判断是否完成评论复现
            flag = 0  # 评论复现是否完成
            begin = CurrentPage
            record.op = []
            record.node = []
            while not flag:
                # 询问大模型接下来要执行的动作
                CurrentPageSource = driver.page_source
                CurrentPageHTML, coordinate, x_max, y_max = tools.page(CurrentPageSource, page_num,1)     # 当前页面的HTML presentation
                actions = ''
                for action in history_action:
                    actions = actions + action + '\n'
                content = example_select_action + 'User comment:' + comment + '\nThe key words of the comment:' + record.key_sentence + '\nWidgets information of current state:\n' + CurrentPageHTML + "\nThe actions we have done:\n" + actions + \
                          '\noutput format:"click ui_index" or "input ui_index input-text" or "scroll up/down or "long-click ui_index".Example:\nclick 1\ninput 1 "123"\nscroll up\nlong-click 2\nScroll up means sliding up, scroll down means sliding down. Note that only one action is output at a time.If you think the current page is wrong or want to return to the previous page, please output "back".'
                time.sleep(5)
                result = ask_gpt4(content)
                log.write(content + "\n" + result + '\n')
                print(content + "\n" + result)
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
                        if len(history_action) != 0 and ('long-click' == history_action[len(history_action) - 1]):
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
                            # re_action['click ' + str(id)] += 1
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
                        if len(history_action) != 0 and history_action[len(history_action)-1] == 'back':
                            result = ask_gpt4('The "back" action has been done.' + content)
                            log.write('The "back" action has been done.' + content + "\n" + result + '\n')
                            continue
                    try:    # 执行对应动作
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
                            history_action.append('long-click')
                            action = {'from': begin, 'to': str(hash(CurrentPageSource)), 'event': 'long-click'}
                            record.op.append(action)
                            begin = action['to']
                            image_path = tools.get_screenshot(sc_screenshot_path + '\\' + str(hash(CurrentPageSource)) + '.png')
                            activity_name = tools.get_activity()
                            if activity_name is None:
                                activity_name = ''
                            node = {"image": image_path, "activity": activity_name,"state_str": str(hash(CurrentPageSource))}
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
                            time.sleep(10)
                            history_action.append('click' + coordinate[id].html)
                            CurrentPageSource = driver.page_source
                            action = {'from': begin, 'to': str(hash(CurrentPageSource)), 'event': 'click' + coordinate[id].html}
                            record.op.append(action)
                            begin = action['to']
                            image_path = tools.get_screenshot(sc_screenshot_path + '\\' + str(hash(CurrentPageSource)) + '.png')
                            activity_name = tools.get_activity()
                            if activity_name is None:
                                activity_name = ''
                            node = {"image": image_path, "activity": activity_name,
                                    "state_str": str(hash(CurrentPageSource))}
                            record.node.append(node)
                            # re_action['click ' + str(id)] = 0
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
                            time.sleep(10)
                            CurrentPageSource = driver.page_source
                            action = {'from': begin, 'to': str(hash(CurrentPageSource)),
                                      'event': 'input' + coordinate[id].html + text}
                            record.op.append(action)
                            begin = action['to']
                            image_path = tools.get_screenshot(sc_screenshot_path + '\\' + str(hash(CurrentPageSource)) + '.png')
                            activity_name = tools.get_activity()
                            if activity_name is None:
                                activity_name = ''
                            node = {"image": image_path, "activity": activity_name,"state_str": str(hash(CurrentPageSource))}
                            record.node.append(node)
                            re_action['input ' + str(id)] = 0
                            break
                        elif 'scroll' in result:
                            if 'up' in result:
                                size = driver.get_window_size()
                                height = driver.get_window_size().get('height')
                                weight = driver.get_window_size().get('width')
                                driver.swipe(start_x=weight * 0.5, start_y=height * 0.8, end_x=weight * 0.5, end_y=height * 0.2, duration=1000)
                                history_action.append('scroll up')
                                time.sleep(10)
                                CurrentPageSource = driver.page_source
                                action = {'from': begin, 'to': str(hash(CurrentPageSource)), 'event': 'scroll up'}
                                record.op.append(action)
                                begin = action['to']
                                image_path = tools.get_screenshot(sc_screenshot_path + '\\' +  str(hash(CurrentPageSource)) + '.png')
                                activity_name = tools.get_activity()
                                if activity_name is None:
                                    activity_name = ''
                                node = {"image": image_path, "activity": activity_name,"state_str": str(hash(CurrentPageSource))}
                                record.node.append(node)
                            elif 'down' in result:
                                size = driver.get_window_size()
                                height = driver.get_window_size().get('height')
                                weight = driver.get_window_size().get('width')
                                driver.swipe(start_x=weight * 0.5, start_y=height * 0.2, end_x=weight * 0.5, end_y=height * 0.8,duration=1000)
                                history_action.append('scroll down')
                                time.sleep(10)
                                CurrentPageSource = driver.page_source
                                action = {'from': begin, 'to': str(hash(CurrentPageSource)), 'event': 'scroll down'}
                                record.op.append(action)
                                begin = action['to']
                                image_path = tools.get_screenshot(sc_screenshot_path + '\\' +  str(hash(CurrentPageSource)) + '.png')
                                activity_name = tools.get_activity()
                                if activity_name is None:
                                    activity_name = ''
                                node = {"image": image_path, "activity": activity_name,"state_str": str(hash(CurrentPageSource))}
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
                    content = example2 + '''Please determine whether the following user comment UI context has been reproduced. Output:YES/NO\n''' + \
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

            ob.append(deepcopy({"round": is_finished, "comment": record.comment, "scenarios": record.scenario, "key sentence": record.key_sentence, "target activity": record.targetac,"the function of activity": record.acfunction, "target state": record.targetst,
                    "the sub-task list of state": deepcopy(record.statelist), "nodes": deepcopy(record.node), "operations": deepcopy(record.op), "Final answer": flag}))
            #comment_num += 1
            #df.drop(index=random_index)  # 在原始数据文件中删除此条评论
            driver.keyevent(4)
            driver.keyevent(4)
            driver.keyevent(4)
            driver.quit()
        with open(scene_path + '.json', 'w') as f:
            json.dump(ob, f, indent=4, separators=(',', ': '))
    test_comment_num += 1
    comment_num += 1

log_sc.close()
log.close()



