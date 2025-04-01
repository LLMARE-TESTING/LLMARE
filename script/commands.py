from gpt.gpt import ask_gpt4
import re


command = '''Based on the user comment and the functions of each activity in application, determine which activity the comment describes.Only output activity name.
Here are a few tips for you：
1)If there are multiple consecutive actions in the scenario described by the user, the activity related to the first action is given priority. For example, for the UI context "Deleted a board and then tried to create another board with the same name, but the app shows a message saying, 'you have another board with the same name'", you need to select an activity that can complete deleting a board, because we want to complete multiple continuous actions described in the scene one by one.
2)Please complete the action in the scenario specified by the user. For example, for the scenario "After editing a photo, when the user hits \"done,\" the app does not allow saving changes directly and instead provides a \"save copy\" option. However, selecting \"save copy\" results in an error message \"unable to save changes,\" and the app gets stuck in a loading state.", the user review mentioned "editing a photo", so it must be saving after editing a photo, and the scenario of editing a video cannot be selected.
3)When selecting an activity, you don't need to pay attention to the description of the result in the scenario, but focus on the application page where the scenario is most likely to appear. For example, if the scenario mentioned in a user comment is "the video feed randomly disappears", you only need to select the activity related to playing videos.\n\n
Note that the name of the activity is the content before the first colon of each paragraph, for example:\norg.chromium.chrome.browser.settings.SettingsActivity:Manage app navigation, settings, privacy, security, themes, notifications, language options, and provide help or feedback. Configure browser and account settings for personalization and enhanced security.\ntask list:{'name': 'Access Settings', 'description': 'Interact with settings options, including Privacy and security, Notifications, Theme, Advanced, and more.'}...\nThe activity name is "org. chromium.chrome.browser.settings.SettingsActivity"\n'''

command1 = "Please extract the mobile application component information or page information mentioned in the comment.The key information should be component of the application or the name of a page.Only output one phrase."


command2 = '''Based on the user comment and the functions of each state in application, determine which state the comment describes. Only output state name. 
Here are a few tips for you：
1）If there are multiple consecutive actions in the scenario described by the user, the state related to the first action is given priority. For example, for the UI context "Deleted a board and then tried to create another board with the same name, but the app shows a message saying, 'you have another board with the same name'", you need to select an activity that can complete deleting a board, because we want to complete multiple continuous actions described in the scene one by one.
2）Please complete the action in the scenario specified by the user. For example, for the scenario "After editing a photo, when the user hits \"done,\" the app does not allow saving changes directly and instead provides a \"save copy\" option. However, selecting \"save copy\" results in an error message \"unable to save changes,\" and the app gets stuck in a loading state.", the user review mentioned "editing a photo", so it must be saving after editing a photo, and the scenario of editing a video cannot be selected.\n\n'''


example1 = "\nExample:\ncomment:THE worst part is when I share a tiktok with someone, I have to scroll back and forth between tiktoks to make the share menu go away and the share menu freezes in place making it frustrating and impossible to share videos with people. key information:share menu"


command_of_key_sentence = '''And then you need to extract key sentences related to the scenarios described in user reviews. ''' + \
            '''For example:\ncomment: I've relied on this for years to help with language learning but two things have always bugged me about the camera mode: by default the original text is covered up by the translation (why can't we set our own default?) and it's quite difficult to select text that's bigger than a word but smaller than the whole page - and the latter is even harder now that Translate outsources the camera to Lens, where half the screen is covered with buttons and pop-up dialogs.''' + \
            '''\nThe key sentence：two things have always bugged me about the camera mode\nThe key statement indicates that the problem scenario described in this user comment occurs in "camera mode", so I can prioritize going to the page where the camera mode is located to reproduce the scenario described in the user comment.''' + \
            '''\nBased on the above example, please extract the key sentences of the following comment and output the key sentence without other content."\n'''

# example2 = '''For example,for comment:Love the app, only issue is I think due to the new update; everytime I press the 'conversation' icon, a voice keeps repeating 'press and hold the Google assistant button'. And it doesn't go away no matter what I do. This has made the app unusable for me for now. I hope it gets fixed soon.\n''' + \
# '''We only need to press the 'conversation' icon to reproduce the scenario the comment described.So if the action like clicking conversation button in the actions have been done,the reproduction is finished.'''
example2 = '''Please determine whether the entire process of reproducing a comment-described scenario has been completed. We need to reach the scenario described by the user and complete the actions they mentioned, but we do not focus on whether the issues described by the user occur. You need to focus on the actions we have completed and the CurrentPageHTML. 
Here are two examples of successful reproduction:

##example1
UI context:Whenever I open the app and see a nice pin I save it in my board and it's doesn't get saved. It shows 'Save failed'.
actions required to reach the UI context:
1.click a pin;
2.click the "save" button;
3.select a target board;
#Note: In this example, it is important to note that clicking the "save" button does not lead to the scenario described in the user's comment, because the action of "save a pin" is not completed yet and needs to be saved to the board before the reproduction is complete. In actual execution, in addition to the historical actions performed, you can also use the component information of the current page to determine whether the entire operation is completed. For example, after completing "save a pin", the "saved" component may appear, indicating that the pin has been saved.

##example2
UI context:But however I have deleted a board and if i want to create another board with the same name it's showing as 'you have another board with the same name'. 
actions required to reach the UI context:
1.click "saved" button to change to saved page;
2.click "Boards" button to chage the boards page;
3.click a board named "g";
4.click the "more options" button;
5.click the "Edit board and header image" button;
6.scroll down;
7.click the "Delete" button to delete the board;
8.click the "Delete" button to confirm the deletion;
9.click the "Create" button;
10.click the "Board" to create a board;
11.input the same name "g" as the board name;
12.click "Next" button;
13.click "Done" button to finish the create process.
#Chain-of-Thought:
Let's think about this step by step. The UI context involves two main tasks: deleting a board and creating a new one with the same name.
For the deletion task: First, based on the widget information of the current page, look for the component for deleting the board. The deletion process likely requires confirmation steps.
For the creation task: On the page following the deletion operation, we need to locate the create component. If needing to select the type of content to create, choose "board". During the process of creating a board, it is required to  enter the board's name, we should input the name of the previously deleted board as specified in the UI context. After entering the necessary information, it may also be necessary to confirm the creation action.
Therefore, the specific actions needed are: click the delete board button, and confirm the deletion (Actions 1–2). Next, to create another board with the same name, click the create button (Action 3), and after entering the same board name, click next, done, or similar buttons to complete the creation process (Actions 5–7).
#Note:
In this example, to reach the target UI context, two operations, namely deleting and creating a board, must be completed. If only one of the operations is completed, the target UI context is not reached.

##example3
UI context:when I press do not turn on back up it just spins forever and doesn't let me into my photos at all.
actions required to reach the UI context:
1.click "account and setting" button;
2.click "backup complete" button to transfer to backup setting page;
3.click "Buck up photos & vedios on this device automatically" to turn off buckup;
4.back;
5.click a photo.
#Chain-of-Thought:
Let's think about this step by step. The UI context involves two main tasks: turn off back up and go into a photo.
For the turning off task: First, based on the widget information of the current page, look for the component for setting, which may contain the component to turn off the backup. There is no component on the "Account and Settings" page that directly allows you to turn off the backup feature. However, the "Backup Complete" indicator shows that the backup feature is currently enabled. By clicking on this component, you can access a page where you can turn the backup on or off.
After disabling the backup, you need to return to the previous page and then click to open the photos.
#Note: Even if the user mentions that certain actions cannot be completed, we still need to execute them, because we are not concerned with whether the actions the user mentioned can actually be performed, but rather with knowledge reproduction. Therefore, when reproducing the example in this case, after disabling the backup feature, you also need to click to open the photo.

It should be noted that an operation mentioned by the user generally requires multiple steps to complete, as in the example given above. At the same time, for features described in user comments, whether they are complaints about complexity or opinions about bugs, the features involved in the full reproduction scenario need to be fully reproduced. For example, in the UI context "The Albums feature is difficult and tedious to use, and the user can't figure out how to make a folder.", the reproduction is successful only if the action of "making a folder" is completed. 
For actions mentioned by users, all must be executed. For example, if a comment describes "can not comment on a vedio", the action is considered complete only after completing commenting on a vedio, rather than assuming that the above action can be executed when the relevant components are seen.
##\n'''


# = '''I am trying to reproduce the problem scenarios described in user reviews of mobile apps to help developers maintain and improve the apps. The following is an APP review:''' + comment + \
#               '''Please judge: 1. Is the scenario the review described reproducible? Does the review describe a specific application scenario, that is, according to its description, it can be determined which page of the application it occurs on, and the scenario is a fixed interface of the application and does not appear randomly?''' + \
#               '''2. User reviews that are helpful in improving application functions and enhancing user experience, and are not content-related issues, such as "inaccurate content", "too many ads", "ads cannot be turned off", etc.'''+\
#               '''3. The scene cannot be cross-application.The scenario described in the comment does not occur when the app is in a small window, in the background or in poping up/floating status, but occurs after the app is started normally.''' + command4 +\
#               '''You need to answer:\n1)If all three points are met,output 'YES, otherwise output 'NO'.You should show reasons.\n2)The key sentence of the comment.'''
    # 大模型判断该用户评论是否可以用于测试
    #result = ask_gpt_4(command3)
    #log.write(command3 + '\n' + result)

command6 = '''And then you need to extract key words related to the scenarios described in user reviews.''' + \
            '''For example:\nscenario: by default the original text is covered up by the translation (why can't we set our own default?) and it's quite difficult to select text that's bigger than a word but smaller than the whole page.''' + \
            '''\nThe key words：the camera mode\nThe key words indicates that the problem scenario described in this user comment occurs in "camera mode", so I can prioritize going to the page where the camera mode is located to reproduce the scenario described in the user comment.''' + \
            '''\nBased on the above example, please extract the key words of the following comment and output the key words without other content."\n'''

example_select_action = '''You need to select an action and the index of the target UI element to reproduce a comment-described scenario.We need to reach the scenario described by the user and complete the actions they mentioned, but we do not focus on whether the issues described by the user occur.

##example 1
UI context:Crop a video and save it, resulting in the saved video becoming pixelated.
The reproduced UI context sequence is as follows:
1)click a vedio;
2)click "Edit" button;
3)click "Change to crop tab" button;
4)click the "Choose crop aspect ratio" button;
5)click the "Square" button;
6)click the "Save copy" button.
##
In the above example, the UI context only mentions the "crop a vedio" operation, but the actions to complete the operation need to be inferred. In fact, the actions to complete the operation include 3 to 5. If you save the copy directly after changing to the crop tab, the crop a vedio operation is not actually performed. In addition, be careful not to select actions that are irrelevant to the scenario described in the user's comment, as this will be considered redundant. If your scene includes multiple sequential actions, complete all the actions in sequence.\n

##example 2
UI context:The boomerang/video option doesn't work.
The reproduced UI context sequence is as follows:
1)click "creation" button;
2)click "story" button;
3)"long-click" the "shutter" button to take a vedio.
##
In the above example, it should be noted that the operation of shooting a video requires long pressing the capture button.

Before selecting an action, please think about the detailed steps required to reproduce the UI context. You can refer to the examples we provide. Then decide whether the following UI Context is reproduced. Please select the action to be performed based on the information below:\n'''

# 获取用户评论中的所有场景
def get_scenarios(app,comment):
    scenarios = []
    example_comment = '''Needs to be repaired. I have followed several pages, but when I go to see my followed pages, they aren't there. Then when I search the page, it has the button for me to follow. I don't understand the issue.'''
    #comment = '''Please just request a quick question.I was trying to edit a video and I found out that there is no option to change text to speech only audio. A l've made sure the app is up to date so I don't know why it's not working. Oh and it would also be nice if everyone had the same editing features. Allowing them on one phone but not other gets really annoying. I am only talking about TikTok editing which other apps can't find to edit clips. My account @aftab.mahar786'''
    example_comment_2 = '''The updates made everything change. Before the updates, the app was good and everything worked perfectly fine. Once the update happened though, the functions wouldn't work that well, at all. For example, I put a video as favorite and later on decide to unfavorite it it won't, same with the likes and following. When I try to share, duet, or switch, the app crashes. I also can't change any of the settings or anything involved with my account.'''

    command_of_scenario = f'''You are an app maintenance personnel, and you want to identify the app features or scenarios that need improvement and maintenance by reproducing the scenarios described in user comments. A continuous scenario refers to a coherent action taken by the user at one time or the user's description of a specific feature.
        For example, in "{example_comment}", the user describes a series of continuous actions related to the "follow" feature: after following a page, they then navigate to the followed page to check it, but do not find the content they had previously followed.
        Such continuous actions count as a single use case. \nFor different use case in a single comment, it is necessary to extract them separately. For example, in "{example_comment_2}", the user described three scenarios: 1.put a video as favorite and later on decide to unfavorite it it won't, same with the likes and following; 2.try to share, duet, or switch, the app crashes; 3.can't change any of the settings or anything involved with my account. ''' + \
        f'''\nThis is a user comment on the "{app}" app. Please extract all reproducible and continuous user scenarios from this user comment:{comment}\n''' + \
        '''For actions that can be performed consecutively, try not to separate them. We only consider scenarios involving specific app features and do not take into account evaluations of the overall app performance.\nOutput format:The use cases included in the user comment are as follows:\n1. ...\n2. ...\n'''
    while True:
        try:
            result = ask_gpt4(command_of_scenario)
            break
        except:
            pass

    pattern = r'\d+\.\s*(.+?)(?=\n\d+\.|$)'
    matches = re.findall(pattern, result, re.DOTALL)

    return matches




# 判断用户评论中的某一场景是否可以复现
def scenario_is_reproducible(scenario):
    log_re = open(f"..\\app\\translate_activity\\output\\log_reproducible.txt", 'a', encoding='utf-8')
    command = '''I am trying to reproduce the problem scenarios described in user reviews of mobile apps to help developers maintain and improve the apps. The following is a scenario exracted from a user comment:''' + scenario + \
            '''Please judge: 1. Is the scenario reproducible? Does the scenario describe a specific application page or a specific application widget/feature and the scenario is a fixed interface of the application and does not appear randomly? In addition, the features mentioned in the scenario should not be those suggested by the user for addition, as this indicates that the app does not currently include these features.''' + \
            '''2. The feature described by the scenario is helpful in improving application functions and enhancing user experience, and are not content-related issues, such as "inaccurate content", "too many ads", "ads cannot be turned off", etc.''' + \
            '''3. The scenario cannot be cross-application.The scenario does not occur when the app is in a small window, in the background or in poping up/floating status, but occurs after the app is started normally.\n''' + \
            '''We do not care whether the issues mentioned in the comment actually occur, nor do we care whether the described scenario is related to the app version or the mobile device configuration.\n''' +\
            '''You need to answer:\n1)If all three points are met,output 'YES, otherwise output 'NO'.You should show reasons.\nOutput format:\nYES/NO\nReason:...'''
    result = ask_gpt4(command)
    log_re.write(command + '\n' + str(result))
    log_re.close()
    if 'YES' in result:
        return True
    else:
        return False




# 将记录的内容提供给LLM，判断整个复现过程是否完成
            #command5 = f'''I am reproducing the scenario described in the user's comment. I will give you information about the entire reproduction process. Please use the information to determine whether the scenario described in the user's comment has been reproduced.\n''' +\
            #    f'''User review content:{record.comment}\nYou need to pay special attention to these sentences:{record.key_sentence}\n\n''' + \
            #    f'''The actions completed during the entire reproduction process:\n{actions}\n\nWe only need to arrive at the scene described by the comment without completely reproducing the entire process of the comment.You need to focus on the actions we have completed.{example2}If the review describes multiple scenarios, reaching one scenario is considered complete.If you think the reproduction is complete, please output YES, otherwise output NO.'''
            #while True:
            #    time.sleep(5)
            #    result = ask_gpt4(command5)
            #     log.write(command5 + "\n" + result)
            #     if 'YES' in result:
            #         record.answer = 'YES'
            #         #is_finished = 0
            #         break
            #     elif 'NO' in result:
            #         record.answer = 'NO'
            #         #is_finished -= 1
            #         break

        # ## Chain-of-thought
        # Let
        # 's think step by step
        # 1.
        # Recognize
        # UI
        # context: The
        # user
        # comments
        # state
        # "After editing photos, either with the markup tool or by cropping them, I can't save the changes. The "
        # done
        # " button exists, but nothing happens when you press it".It
        # describes
        # a
        # UI
        # context
        # where
        # saving
        # the
        # change
        # after
        # using
        # the
        # markup
        # tool or crop
        # feature.
        # 2.
        # Expected
        # actions: Please
        # predict
        # the
        # exploration
        # steps
        # to
        # reproduce
        # this
        # UI
        # context
        # based
        # on
        # above
        # information.
        # 3.
        # Actual
        # actions: The
        # reproduced
        # UI
        # context
        # sequence is as follows:
        # 1)click
        # a
        # photo;
        # 2)click
        # the
        # "Edit"
        # button;
        # 3)click
        # the
        # "Change to crop tab"
        # button;
        # 4)click
        # the
        # "Choose crop aspect ratio"
        # button;
        # 5)click
        # the
        # "Square"
        # button;
        # 6)click
        # the
        # "Save"
        # button;
        # 7)click
        # the
        # "Save"
        # button or "Save as a copy"
        # to
        # confirm
        # the
        # change.
        # ##