command = "Based on the user comment and the functions of each activity in application, determine which activity the comment describes.Only output activity name.(e.g. .uioverrides.QuickstepLauncher). "
command1 = "Please extract the mobile application component information or page information mentioned in the comment.The key information should be component of the application or the name of a page.Only output one phrase."
command2 = 'Based on the user comment and the functions of each state in application, determine which state the comment describes.Only output state name.(e.g.state1,45b7f0f22a9dbb70bd79a2785ca109fc)'
example1 = "\nExample:\ncomment:THE worst part is when I share a tiktok with someone, I have to scroll back and forth between tiktoks to make the share menu go away and the share menu freezes in place making it frustrating and impossible to share videos with people. key information:share menu"


command4 = '''And then you need to extract key sentences related to the scenarios described in user reviews. ''' + \
            '''For example:\ncomment: I've relied on this for years to help with language learning but two things have always bugged me about the camera mode: by default the original text is covered up by the translation (why can't we set our own default?) and it's quite difficult to select text that's bigger than a word but smaller than the whole page - and the latter is even harder now that Translate outsources the camera to Lens, where half the screen is covered with buttons and pop-up dialogs.''' + \
            '''\nThe key sentence：two things have always bugged me about the camera mode\nThe key statement indicates that the problem scenario described in this user comment occurs in "camera mode", so I can prioritize going to the page where the camera mode is located to reproduce the scenario described in the user comment.''' + \
            '''\nBased on the above example, please extract the key sentences of the following comment and output the key sentence without other content."\n'''

example2 = '''For example,for comment:Love the app, only issue is I think due to the new update; everytime I press the 'conversation' icon, a voice keeps repeating 'press and hold the Google assistant button'. And it doesn't go away no matter what I do. This has made the app unusable for me for now. I hope it gets fixed soon.\n''' + \
'''We only need to press the 'conversation' icon to reproduce the scenario the comment described.So if the action like clicking conversation button in the actions have been done,the reproduction is finished.'''

# = '''I am trying to reproduce the problem scenarios described in user reviews of mobile apps to help developers maintain and improve the apps. The following is an APP review:''' + comment + \
#               '''Please judge: 1. Is the scenario the review described reproducible? Does the review describe a specific application scenario, that is, according to its description, it can be determined which page of the application it occurs on, and the scenario is a fixed interface of the application and does not appear randomly?''' + \
#               '''2. User reviews that are helpful in improving application functions and enhancing user experience, and are not content-related issues, such as "inaccurate content", "too many ads", "ads cannot be turned off", etc.'''+\
#               '''3. The scene cannot be cross-application.The scenario described in the comment does not occur when the app is in a small window, in the background or in poping up/floating status, but occurs after the app is started normally.''' + command4 +\
#               '''You need to answer:\n1)If all three points are met,output 'YES, otherwise output 'NO'.You should show reasons.\n2)The key sentence of the comment.'''
    # 大模型判断该用户评论是否可以用于测试
    #result = ask_gpt_4(command3)
    #log.write(command3 + '\n' + result)

command6 = '''And then you need to extract key words related to the scenarios described in user reviews.''' + \
            '''For example:\ncomment: I've relied on this for years to help with language learning but two things have always bugged me about the camera mode: by default the original text is covered up by the translation (why can't we set our own default?) and it's quite difficult to select text that's bigger than a word but smaller than the whole page - and the latter is even harder now that Translate outsources the camera to Lens, where half the screen is covered with buttons and pop-up dialogs.''' + \
            '''\nThe key words：the camera mode\nThe key words indicates that the problem scenario described in this user comment occurs in "camera mode", so I can prioritize going to the page where the camera mode is located to reproduce the scenario described in the user comment.''' + \
            '''\nBased on the above example, please extract the key words of the following comment and output the key words without other content."\n'''
