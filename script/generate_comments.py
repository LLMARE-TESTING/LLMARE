import pandas as pd
import random
from gpt.gpt import ask_gpt_4
import re
import openpyxl
from commands import command4
import time

comment_num = 0  # 随机选择的用户评论的数量



app_name = 'translate_activity'
df = pd.read_excel(f"..\\app\\{app_name}\\300comment.xlsx")
log = open(f"..\\app\\{app_name}\\output\\log-comment.txt", 'a', encoding='utf-8')
test_comment_num = 0
data_list = []
# 随机选择一条评论
while True:
    try:
        random_index = random.randint(1, len(df) - 1)
        comment = df.iloc[random_index]['comment']
        comment_num += 1
        command3 = '''I am trying to reproduce the problem scenarios described in user reviews of mobile apps to help developers maintain and improve the apps. The following is an APP review:''' + comment + \
                   '''Please judge: 1. Is the scenario the review described reproducible? Does the review describe a specific application scenario, that is, according to its description, it can be determined which page of the application it occurs on, and the scenario is a fixed interface of the application and does not appear randomly?''' + \
                   '''2. User reviews that are helpful in improving application functions and enhancing user experience, and are not content-related issues, such as "inaccurate content", "too many ads", "ads cannot be turned off", etc.''' + \
                   '''3. The scene cannot be cross-application.The scenario described in the comment does not occur when the app is in a small window, in the background or in poping up/floating status, but occurs after the app is started normally.''' + command4 + \
                   '''You need to answer:\n1)If all three points are met,output 'YES, otherwise output 'NO'.You should show reasons.\n2)The key sentence of the comment.'''
        # 大模型判断该用户评论是否可以用于测试
        result = ask_gpt_4(command3)
        time.sleep(5)
        match = re.search(r'Key sentence:', result)
        if match is None:
            match = re.search(r'Key sentences:', result)
        if match is None:
            key_sentence = ''
        else:
            key_sentence = result[(match.span())[1]:]
        # 读取 Excel 文件
        row_to_insert = comment_num  # 插入到第 1 行，原第 1 行及之后的行会向下移动
        if 'YES' in result:
            test_comment_num += 1
            data_to_insert = [{"comment": comment, "test": 'YES', "key_sentence": key_sentence}]  # 插入的数据
            data_to_insert = pd.DataFrame(data_to_insert)
            data_list.append(data_to_insert)
        else:
            data_to_insert = [{"comment": comment, "test": 'NO', "key_sentence": key_sentence}]  # 插入的数据
            data_to_insert = pd.DataFrame(data_to_insert)
            data_list.append(data_to_insert)
        print(f'{test_comment_num}/{comment_num}')
        log.write(command3 + '\n' + result)
        if comment_num == 200:  # 随机选择的用户评论的数量
            break
    except:
        break
merged_df = pd.concat(data_list).drop_duplicates()
merged_df.to_excel(f"..\\app\\{app_name}\\300comments.xlsx", index=False)
log.close()