token = ""
close_send_if = false

// Config
password = "S0F6lFbi8s82kwv93W7SolYjcfLqocsM"

function beforeunload(token) {
    // ページを閉じた時にサーバーに通知する
    body = JSON.stringify({"status": "closed"});
    fetch("http://localhost:5000/status", {
        method: 'POST',
        body: JSON.stringify({"status": "closed"}),
        headers: {
            "Content-type": "application/json",
            "Authorization": "Bearer " + this.token
        },
        keepalive: true
    });
    console.debug("Send_Close");
    close_send_if = true;
};

function ajaxerror(xhr, testStatus, errorThrown) {
    // トークンの有効期限が切れたら再読込する
    if (xhr.status == 401) {
        console.log("Reloading token...")
        token = gettoken(password)
    };
};

function sleep(ms) {
    // sleep関数を作る
    return new Promise(resolve => setTimeout(resolve, ms));
};

async function gettoken(password) {
    // トークンを取得する
    tokenrecv = $.ajax(
        {
            type: "POST",
            url: "http://localhost:5000/login",
            data: JSON.stringify({"user": "user1", "password": password}),
            contentType: "application/json; charset=UTF-8"
        }
    );
    while (true) {
        await sleep(50);
        if (tokenrecv.responseJSON == undefined) {
            continue;
        } else {
            token = tokenrecv.responseJSON["token"];
            window.addEventListener('beforeunload', {token: token, handleEvent: beforeunload});
            return token
        };
    };
};

token = gettoken(password);


async function loop_my_page() {
    while (document.getElementsByClassName("score")[0].textContent == null) {
        console.debug("SCORE_NULL");
        await sleep(200);
    }
    while (document.getElementsByClassName("myRanking")[0].textContent == "") {
        console.debug("RANKING_NULL")
        await sleep(200);
    }
    while (token == "") {
        await sleep(200);
    }
    console.debug("Show MyPage");
        // 現在の進捗取得
        var daily_progress = document.getElementsByClassName("score")[0].textContent;
        var daily_goal = document.getElementsByClassName("crGoal")[0].textContent;
        var weekly_progress = document.getElementsByClassName("score")[1].textContent;
        var weekly_goal = document.getElementsByClassName("crGoal")[1].textContent;
        var ranking = document.getElementsByClassName("myRanking")[0].textContent;
        var now_json = JSON.stringify({'status': 'my_page', 'daily_progress': daily_progress, 'daily_goal': daily_goal, 'weekly_progress': weekly_progress, 'weekly_goal': weekly_goal, 'ranking': ranking})
        console.debug(now_json);
        // 現在の進捗をログに出力
        console.debug("daily_Progress: "+daily_progress+"/"+daily_goal);
        console.debug("weekly_Progress: "+weekly_progress+"/"+weekly_goal);
        console.debug("Ranking: "+ranking);
        $.ajax({
            type: "POST",
            url: "http://localhost:5000/status",
            data: now_json,
            headers: {"Authorization": "Bearer " + token},
            contentType: "application/json; charset=UTF-8",
            error: ajaxerror});
        if(close_send_if == true){
            //break;
        }
    //}
};

async function loop_studyreport() {
    while (document.getElementsByClassName("score")[0].textContent == null) {
        console.debug("SCORE_NULL");
        await sleep(200);
    }
    while (document.getElementsByClassName("current-ranking score-text grade-right")[0].textContent == "") {
        console.debug("RANKING_NULL")
        await sleep(200);
    }
    while (token == "") {
        await sleep(200);
    }
    console.debug("Show StudyReport");
        // 現在の進捗取得
        var daily_progress = document.getElementsByClassName("score")[0].textContent;
        var daily_goal = document.getElementsByClassName("crGoal")[0].textContent;
        var weekly_progress = document.getElementsByClassName("score")[1].textContent;
        var weekly_goal = document.getElementsByClassName("crGoal")[1].textContent;
        var ranking = document.getElementsByClassName("current-ranking score-text grade-right")[0].textContent;
        var now_json = JSON.stringify({'status': 'studyreport', 'daily_progress': daily_progress, 'daily_goal': daily_goal, 'weekly_progress': weekly_progress, 'weekly_goal': weekly_goal, 'ranking': ranking});
        // 現在の進捗をログに出力
        console.debug("daily_Progress: "+daily_progress+"/"+daily_goal);
        console.debug("weekly_Progress: "+weekly_progress+"/"+weekly_goal);
        console.debug("Ranking: "+ranking);
        $.ajax({
            type: "POST",
            url: "http://localhost:5000/status",
            data: now_json,
            headers: {"Authorization": "Bearer " + token},
            contentType: "application/json; charset=UTF-8",
            error: ajaxerror});
};

async function loop_flashwords() {
    console.debug("Doing FlashWords");
    var before_progress = 0;
    while (true) {
        await sleep(10);
        // 現在の進捗取得
        var now_progress = document.getElementsByClassName("flashword-header-pagination question-pagination")[0].textContent.split(' ')[0];
        // 前回取得時と同じかどうか
        if(now_progress == before_progress) {
            // 同じならループの最初から
            continue;
        }
        // 同じでない時
        // 現在の進捗をログに出力
        console.debug("Now_Progress: "+now_progress+"/15");
        $.ajax({
            type: "POST",
            url: "http://localhost:5000/status",
            data: JSON.stringify({'status': 'flashwords', 'progress': now_progress}),
            headers: {"Authorization": "Bearer " + token},
            contentType: "application/json; charset=UTF-8",
            error: ajaxerror});
        before_progress = now_progress;
    }
};

async function loop_wordpanic() {
    console.debug("Doing WordPanic");
    var before_json = JSON.stringify({'none':'none'});
    while (true) {
        await sleep(100);
        var now_json = JSON.stringify({'status': 'wordpanic'})
        $.ajax({
            type: "POST",
            url: "http://localhost:5000/status",
            data: now_json,
            headers: {"Authorization": "Bearer " + token},
            contentType: "application/json; charset=UTF-8",
            error: ajaxerror});
        if(close_send_if == true){
            break;
        }
    }
};

/*
async function a() {
    //a
};
*/

console.debug("start")

if(location.pathname == '/my_page.html') {
    // トップページにアクセスされている
    // 今日の達成数と今週の達成数、ランキングを取得しサーバーに送信
    loop_my_page();
} else if(location.pathname == '/flashwords.html') {
    // フラッシュワード実施中
    // 現在の進捗(○/15)を取得し、サーバーに送信
    loop_flashwords();
} else if(location.pathname == '/studyreport.html') {
    // 学習終了
    // 今日の達成数と今週の達成数、ランキングを取得しサーバーに送信
    loop_studyreport();
} else if(location.pathname == '/wordpanic.html') {
    // ワードパニック実施中
    // ワードパニック実施中とサーバーに送信
    loop_wordpanic();
} else if(location.pathname == '/wordpanic-studyreport.html') {
    // 学習終了
    // 今日の達成数と今週の達成数、ランキングを取得しサーバーに送信
    loop_studyreport();
} else if(location.pathname == '') {
    ///a
}/* else if(location.pathname == '') {
    ///a
}*/
