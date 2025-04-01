
class subtask:
    def __init__(self):
        self.name = ''
        self.description = ''
        self.parameter = {}
        self.UI_index

class page_node:
    def __init__(self):
        self.subtasks = []


class subtask_edge:
    def __init__(self):
        self.name = ''  # 子任务名称
        self.actions = []  # 完成该子任务所需的动作


# 节点集合
nodes = []
# 边集
edges = {}
UI_list = []


A = page_node()  # 创建一个节点
A.subtasks.append({
  "name": "ViewAlarmDetails",
  "description": "View details of a specific alarm",
  "parameters": {
    "alarm_time": "Which alarm time details do you want to view?"
  },
  "UI_index": 9
})

A.subtasks.append({
"name": "ViewClock",
"description": "View the clock",
"parameters": { },
"UI_index": 26
})

B = page_node()
B.subtasks.append({
"name": "ViewTimer",
"description": "View the timer",
"parameters": {},
"UI_index": 18
})

nodes.append(A)
nodes.append(B)

edges[(A,B)] = "ViewClock"








