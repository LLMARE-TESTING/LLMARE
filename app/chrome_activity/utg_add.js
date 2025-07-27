var utg = {
    "nodes" : [
        {
            "image": "state1.png",
            "activity": "com.google.android.apps.chrome.Main",
            "state_str": "state1"
        },
        {
            "image": "state2.png",
            "activity": "org.chromium.chrome.browser.settings.SettingsActivity",
            "state_str": "state2"
        },
        {
            "image": "state3.png",
            "activity": "org.chromium.chrome.browser.settings.SettingsActivity",
            "state_str": "state3"
        },
        {
            "image": "state4.png",
            "activity": "org.chromium.chrome.browser.settings.SettingsActivity",
            "state_str": "state4"
        },
        {
            "image": "state5.png",
            "activity": "org.chromium.chrome.browser.settings.SettingsActivity",
            "state_str": "state5"
        },
        {
            "image": "state6.png",
            "activity": "org.chromium.chrome.browser.settings.SettingsActivity",
            "state_str": "state6"
        },
        {
            "image": "state7.png",
            "activity": "org.chromium.chrome.browser.app.bookmarks.BookmarkActivity",
            "state_str": "state7"
        },
        {
            "image": "state8.png",
            "activity": "org.chromium.chrome.browser.app.bookmarks.BookmarkActivity",
            "state_str": "state8"
        },
        {
            "image": "state9.png",
            "activity": "org.chromium.chrome.browser.settings.SettingsActivity",
            "state_str": "state9"
        }
    ],
    "edges" : [
        {
            "from": "c3089b85bf0d6e714b4c98eaf108cb84",
            "to": "state1",
            "event_str": "click(com.android.chrome:id/menu_button:[948,83][1080,237])"
        },
        {
            "from": "ed054865d30b2d32562c74d38331f102",
            "to": "state2",
            "event_str": "scroll-down(com.android.chrome:id/recycler_view:[0,237][1080,2148])"
        },
        {
            "from": "state2",
            "to": "state3",
            "event_str": "scroll-down(com.android.chrome:id/recycler_view:[0,237][1080,2148])"
        },
        {
            "from": "state3",
            "to": "state4",
            "event_str": "click(android.widget.RelativeLayout:[44,1751][260,1810])"
        },
        {
            "from": "ed054865d30b2d32562c74d38331f102",
            "to": "state5",
            "event_str": "click(android:id/title:[44,1770][436,1829])"
        },
        {
            "from": "state5",
            "to": "state6",
            "event_str": "scroll-down(androidx.recyclerview.widget.RecyclerView:[0,237][1080,2148])"
        },
        {
            "from": "c22707ef795c84f9d5b86771cdeb3175",
            "to": "state7",
            "event_str": "click(com.android.chrome:id/all_bookmarks_menu_id:[354,953][1064,1085])"
        },
        {
            "from": "state7",
            "to": "state8",
            "event_str": "click(com.android.chrome:id/container:[28,400][1052,654])"
        },
        {
            "from": "state2",
            "to": "state9",
            "event_str": "click(android.widget.TextView-Theme:[28,400][1052,654])"
        }
        
    ]
}