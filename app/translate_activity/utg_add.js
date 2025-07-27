var utg = {
    "nodes" : [
        {
            "image": "state1.png",
            "activity": ".TranslateActivity",
            "state_str": "state1"
        },
        {
            
            "image": "state2.png",
            "activity": ".TranslateActivity",
            "state_str": "state2"
        },
        {
            
            "image": "state3.png",
            "activity": ".TranslateActivity",
            "state_str": "state3"
        },
        {
            
            "image": "state4.png",
            "activity": ".TranslateActivity",
            "state_str": "state4"
        },
        {
            
            "image": "state5.png",
            "activity": ".TranslateActivity",
            "state_str": "state5"
        },
        {
            
            "image": "state6.png",
            "activity": ".TranslateActivity",
            "state_str": "state6"
        },
        {
            "image": "state7.png",
            "activity": "com.google.android.apps.translate.pref.SettingsActivity",
            "state_str": "state7"
        }
    ],
    "edges" : [
        {
            "from": "1e0a8968f43dbb61fd758c305c65c40a",
            "to": "state1",
            "event_str": "scroll-up(com.google.android.apps.translate:id/pad_area_container:[0,259][1080,1477])",
        },
        {
            "from": "1e0a8968f43dbb61fd758c305c65c40a",
            "to": "state2",
            "event_str": "click(com.google.android.apps.translate:id/pad_area_container:[0,259][1080,1477])",
        },
        {
            "from": "state2",
            "to": "state3",
            "event_str": "input(EditText-com.google.android.apps.translate:id/text_input_field:[66,347][1014,474])(enter)",
        },
        {
            "from": "state3",
            "to": "state4",
            "event_str": "click(ViewGroup-Edit Query Completion entertainment:[0,876][1080,1045])",
        },
        {
            "from": "1e0a8968f43dbb61fd758c305c65c40a",
            "to": "state5",
            "event_str": "click(ImageView-Signed in as ran Jin jinran848@gmail.com:[925,104][1080,237])",
        },
        {
            "from": "state2",
            "to": "state6",
            "event_str": "click(Button-Handwriting:[805,105][937,237])",
        },
        {
            "from": "7bdc16aba671b5811d835b68b453fdff",
            "to": "state6",
            "event_str": "click(Button-Handwriting:[805,105][937,237])",
        },
        {
            "from": "state5",
            "to": "state7",
            "event_str": "click(TextView-Settings:[254,1249][970,1310])",
        }
    ]
}