import copy

import tools
from gpt.gpt import ask_gpt
import re
import os
import json
import time

def deduplicte_activity_subtask(subtask_list):
    content = '''This is a list of the subtasks of an activity in an application. Based on the name or description of the subtask, please remove similar or identical subtasks. \nOutput format:\n [{"name":"...","description":"..."},{},{},...]\nPlease do not output any other redundant information.\nThe subtask list:\n'''
    content += str(subtask_list)
    result = ask_gpt(content)
    result = json.loads(result)
    return result

activity_task = {}
activity_function = {}
page_htmls = {}
state_task = {}
state_widgets = {}   # 各状态的组件信息


command1 = '\nPlease enumerate operations (sub-tasks) that does not exist in the activity sub-task list and can be performed on the screen.Each sub-task includes the following information: 1) sub-task name(A short summary of sub-tasks), 2) sub-task description(describe the sub-task in detail), 3) index of its relevant UI elements, 4) parameter names, and 5) questions required to obtain each parameter.\nOutput format:{name:" ",description:" ",parameters:{ }} \
           \nExample:"1. { name: "Search", description: "Search for a contact", parameters: { "contact_name": "who are you looking for?" }, UI_index: 3 } \n2. { name: "Menu", description: "Open menu", parameters: {}, UI_index: 7 }"'
command = '\nPlease enumerate operations (sub-tasks) can be performed on the screen.Each sub-task includes the following information: 1) sub-task name(A short summary of sub-tasks), 2) sub-task description(describe the sub-task in detail).\nOutput format:{name:" ",description:" "} \
         \nExample:"1. { name: "Search", description: "Search for a contact"} \n2. { name: "Menu", description: "Open menu"}"'
command2 = 'Please check whether there is a sub-task on this page that does not exist in the activity sub-task list.Output:YES/NO.'
command3 = 'You should summary the function of the activity within 30 words based on its task list.\nactivity task list:\n'
app_name = 'instagram_activity'
# # 总结各activity的子任务列表
#  # 将所有的uix文件改为xml文件
# folder_path = f"..\\app\\{app_name}\\activity"
# for root,dirs,files in os.walk(folder_path):
#     for file in files:
#         file_name = os.path.join(root,file)
#         if '.uix' in file_name:
#             os.rename(file_name,file_name[:-4] + '.xml')
#
# for root,dirs,files in os.walk(folder_path):
#     dir_name = (os.path.join(root, ""))[36:-1]
#     activity_task[dir_name] = []
#     #activity_function[dir_name] = []
#     for file in files:
#         viewtree_path = os.path.join(root,file)
#         if '.xml' in viewtree_path:
#             file_name = os.path.join("", file)[:-4]
#             page_html = tools.traverse_xml(viewtree_path)
#             # 获取页面的组件信息
#             widgets = tools.xml_widgets(viewtree_path,1)
#             state_widgets[file_name] = widgets
#             print(page_html)
#             page_htmls[file_name] = page_html
#             # 根据state的相似度来判断是否要保存该state
#             flag = 0  # 0表示没有相似state
#             for key, value in state_widgets.items():
#                 if key != file_name:
#                     similarity = tools.state_similarity(widgets, value)
#                     if similarity >= 0.85:
#                         flag = 1
#                         break
#             if flag == 0:  # 没有相似state,直接将state_task添加到acivity_task
#                 content = command + page_html
#                 try:
#                     state_task[file_name] = []
#                     result = ask_gpt(content)
#                     print(result)
#                     time.sleep(2)
#                 except:
#                     continue
#                 format_task = re.compile(r'name: "(.+?)", description: "(.+?)"')
#                 tasks = format_task.findall(result)
#                 for task in tasks:
#                     state_task[file_name].append({"name": task[0], "description": task[1]})
#             #if len(activity_task[dir_name]) != 0:
#                 activity_task[dir_name] = activity_task[dir_name] + copy.deepcopy(state_task[file_name])
#                 # 如果activity_task的长度超过阈值，则通过大模型进行总结去重
#                 if len(activity_task[dir_name]) > 8000:
#                     activity_task[dir_name] = deduplicte_activity_subtask(activity_task[dir_name])
#             else:
#                 continue   # 有相似的state，跳过对activity_task的修改
#             #else:
#                 #activity_task[dir_name] = activity_task[dir_name] + copy.deepcopy(state_task[file_name])
#                 #content = command2 + "\nPage information:" + page_html + "\nactivity task list:" + str(activity_task[dir_name])
#                 #try:
#                 #    result = ask_gpt(content)
#                 #    time.sleep(2)
#                 #except:
#                 #    continue
#                 #if 'NO' in result and 'YES' not in result:
#                 #    continue
#                 #else:
#                     # 获取新的子任务列表
#                     #content = "\nactivity task list:" + str(activity_task[dir_name]) + command1 + page_html
#                     #try:
#                     #    result = ask_gpt(content)
#                     #    time.sleep(2)
#                     #except:
#                     #    continue
#                     #format_task = re.compile(r'name: "(.+?)", description: "(.+?)"')
#                     #tasks = format_task.findall(result)
#                     #for task in tasks:
#                     #    activity_task[dir_name].append({"name": task[0], "description": task[1]})
#             #else:
#             #    activity_task[dir_name] = copy.deepcopy(state_task[file_name])
#
#             #format_function = re.compile(r'\{ name: "(.+?)", description: "(.+?)", parameters: \{(.*?)\}, UI_index: (\d+) \}')
#             #functions = format_function.findall(result)
#             #for func in functions:
#                 #activity_function[dir_name].append(
#                     #{"name": func[0], "description": func[1], "parameters": func[2], "UI_index": func[3]})
#         if '.json' in viewtree_path:
#             #file_name = os.path.join("", file)[:-5]
#             page_html = tools.traverse_json(viewtree_path)
#             # 获取页面的组件信息
#             widgets = tools.json_widgets(viewtree_path,1)
#             print(page_html)
#             with open(viewtree_path, "r") as file:
#                 data = json.load(file)
#                 file_name = data["state_str"]
#                 state_widgets[file_name] = widgets
#                 page_htmls[file_name] = page_html
#                 content = command + page_html
#                 # 根据state的相似度来判断是否要保存该state
#                 flag = 0  # 0表示没有相似state
#                 for key, value in state_widgets.items():
#                     if key != file_name:
#                         similarity = tools.state_similarity(widgets, value)
#                         if similarity >= 0.85:
#                             flag = 1
#                             break
#                 if flag == 0:  # 没有相似state,直接将state_task添加到acivity_task
#                     content = command + page_html
#                     try:
#                         state_task[file_name] = []
#                         result = ask_gpt(content)
#                         #print(result)
#                         time.sleep(2)
#                     except:
#                         continue
#                     format_task = re.compile(r'name: "(.+?)", description: "(.+?)"')
#                     tasks = format_task.findall(result)
#                     for task in tasks:
#                         state_task[file_name].append({"name": task[0], "description": task[1]})
#                     # if len(activity_task[dir_name]) != 0:
#                     activity_task[dir_name] = activity_task[dir_name] + copy.deepcopy(state_task[file_name])# 如果activity_task的长度超过阈值，则通过大模型进行总结去重
#                     if len(activity_task[dir_name]) > 8000:
#                         activity_task[dir_name] = deduplicte_activity_subtask(activity_task[dir_name])
#                 else:
#                     continue  # 有相似的state，跳过对activity_task的修改
#                 '''
#                 content = command2 + "\nPage information:" + page_html + "\nactivity task list:" + str(activity_task[dir_name])
#                 try:
#                     result = ask_gpt(content)
#                     time.sleep(2)
#                 except:
#                     continue
#                 if 'NO' in result and 'YES' not in result:
#                     continue
#                 else:
#                     # 获取新的子任务列表
#                     content = "\nactivity task list:" + str(activity_task[dir_name]) + command1 + page_html
#                     try:
#                         result = ask_gpt(content)
#                         time.sleep(2)
#                     except:
#                         continue
#                     format_task = re.compile(r'name: "(.+?)", description: "(.+?)"')
#                     tasks = format_task.findall(result)
#                     for task in tasks:
#                         activity_task[dir_name].append({"name": task[0], "description": task[1]})
#             else:
#                 activity_task[dir_name] = copy.deepcopy(state_task[file_name])
#             '''
#             format_function = re.compile(r'\{ name: "(.+?)", description: "(.+?)", parameters: \{(.*?)\}, UI_index: (\d+) \}')
#             functions = format_function.findall(result)
#             for func in functions:
#                 activity_function[dir_name].append({"name": func[0], "description": func[1], "parameters": func[2], "UI_index": func[3]})
#
#
#
#
# with open(f"..\\app\\{app_name}\\activity_task.json", 'w') as file1:
#     json.dump(activity_task, file1, indent=4, separators=(',', ': '))
# with open(f"..\\app\\{app_name}\\state_widgets.json", 'w') as file2:
#     json.dump(state_widgets, file2, indent=4, separators=(',', ': '))
# with open(f"..\\app\\{app_name}\\page_html.json",'w') as file3:
#     json.dump(page_htmls, file3, indent=4, separators=(',', ': '))
# with open(f"..\\app\\{app_name}\\state_task.json",'w') as file4:
#     json.dump(state_task, file4, indent=4, separators=(',', ': '))

# 总结应用各页面的功能
# 总结各个activity的功能


with open(f"..\\app\\{app_name}\\activity_task.json", 'r') as file1:
    activity_task = json.load(file1)
    for key, value in activity_task.items():
        if key != '' and len(value)!=0:
            task_list = ''
            for task in value:
                task_list = task_list + str(task) + '\n'
            content = command3 + task_list
            try:
                result = ask_gpt(content)
                time.sleep(2)
            except:
                continue
            activity_function[key] = result
    with open(f"..\\app\\{app_name}\\activity_function.json", 'w') as file2:
        json.dump(activity_function, file2, indent=4, separators=(',', ': '))


'''
folder_path = '..//GUI'
UIFunc = open("..//UIFunction.txt",'r')
# 根据用户反馈确定主要应用页面
user_comment = '准备下载动漫看，结果离线下载有好多都不能看，都是黑屏.'
command = 'Based on the user review, select the mobile app page most likely associated with the provided description of mobile app pages.Output format:<GUI index>。'
UIFuncs = UIFunc.read()
content = command + 'user comment:' + user_comment + 'GUI screens:' +UIFuncs
result = ask_gpt(content)
print(result)
UIFunc.close()

# 判断是否为新的页面


# 页面状态信息
viewtree_path = "D:\\project\\cert\\GUI\\进入动画后.xml"
page_html = transfer.traverse_xml(viewtree_path)
print(page_html)

command = '\nPlease enumerate operations (sub-tasks) that can be performed on the screen.Each sub-task includes the following information: 1) sub-task name, 2) sub-task description, 3) index of its relevant UI elements, 4) parameter names, and 5) questions required to obtain each parameter.\nOutput format:{name:" ",description:" ",parameters:{ }} \
           \nExample:"1. { name: "Search", description: "Search for a contact", parameters: { "contact_name": "who are you looking for?" }, UI_index: 3 } \n2. { name: "Menu", description: "Open menu", parameters: {}, UI_index: 7 }"'
content = page_html + command
result = ask_gpt(content)
print(result)

# 存储页面的子任务列表
pattern = re.compile(r'.+name: ".+", description: ".+", parameters: { ".+": ".+" }, UI_index: \d+ }\n')
for subtask in pattern.findall(result):
    print(subtask)
    matches = re.match(r'.+name: ".+", description: ".+", parameters: { ".+": ".+" }, UI_index: \d }',subtask)
    print(matches)


# 人工修改机制

# 用户反馈转换
command = '我现在要对某些移动应用的用户评论进行测试，需要你根据用户评论提取出测试步骤，能够依次执行以完成测试。\n例如：评论：准备下载动漫看，结果离线下载有好多都不能看，都是黑屏；测试步骤：1.到达应用的动漫界面；2.点击进入某部动漫；3.离线缓存；4.查看离线缓存的内容。\n请你给出下面评论的测试步骤：刷视频时会卡着不懂，不管重新进入应用还是断网重连都一直卡在那个画面不动。'
content = command
result = ask_gpt(content)
print(result)


# 任务执行
command = '我现在要测试移动应用的用户评论，这是某条用户评论的测试步骤：1.到达应用的动漫界面；2.点击进入某部动漫；3.离线缓存；4.查看离线缓存的内容。\n现在要执行第3步：离线缓存。' + \
           '\n当前页面可以完成的子任务列表为：' + result + \
           '\n当前页面的状态信息为：' + page_html + '\n请你从子任务列表中选择一个子任务执行以完成测试步骤的第一步。'
content = command
result = ask_gpt(content)
print(result)
'''