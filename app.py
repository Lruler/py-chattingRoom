from flask import Flask, session, request, redirect, url_for, render_template, flash
from flask_socketio import SocketIO, emit, join_room
from flask_uploads import configure_uploads,UploadSet
import os, query, datetime, hashlib, time

app = Flask(__name__)   #定义模块名字为APP
app.config.update({     #配置APP模块
    'DEBUG':True,
    'TEMPLATES_AUTO_RELOAD' :True,
    'SECRET_KEY': os.urandom(10)
})
socketio = SocketIO(app)

user_dict = {}
users = []

#配置上传文件存放路径
base = os.path.dirname(os.path.abspath(__file__))
base = os.path.join(base,'static')
app.config['UPLOADS_DEFAULT_DEST']=base
photo=UploadSet()
configure_uploads(app,photo)

@app.route('/upload_img', methods=['POST'])
def upload():
        now = str(time.time())
        fileName = now + '.png'
        path = "static/files/img1/" + fileName
    	#接收图片
        photo.save(request.files['file'], 'img1', fileName)#保存图片
		#发送图片
        img = open(path, 'rb')#读取图片文件
        return img.name

def getLoginDetails():    #获取用户登录状态
    if 'email' not in session:
        loggedIn = False
        userName = 'please sign in'
    else:
        loggedIn = True
        sql = "SELECT user_name FROM chatroom.users WHERE email = %s"
        params = [session['email']]
        userName = query.query(sql,params)
        session['user'] = userName[0][0]
    return (loggedIn, userName[0][0])
#判断账户密码是否匹配
def is_valid(email, password):
    sql = 'SELECT email, password FROM chatroom.users'
    data =query.query_no(sql)
    for row in data:
        if row[0] == email and row[1] == hashlib.md5(password.encode()).hexdigest():
            return True
    return False

#登录
@app.route("/", methods = ['POST', 'GET'])
@app.route("/login", methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if is_valid(email, str(password)):
            session['email'] = email
            flash('登录成功')
            return redirect(url_for('index'))
        else:
            error = 'Invalid UserId / Password'
            flash('登录失败')
            return render_template('login.html', error=error)
    else:
        flash('登录失败')
        return render_template('login.html')

@app.route("/logout")
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))

# 注册
@app.route("/register", methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        #Parse form data
        password = request.form['password']
        email = request.form['email']
        name = request.form['name']
        if is_valid(email, password):
            flash('账号已存在，请登录')
            return render_template("login.html")
        else:
            sql = 'INSERT INTO chatroom.users (email,password,user_name) VALUES (%s,%s,%s)'
            params = [email,hashlib.md5(password.encode()).hexdigest(),name]
            msg = query.update(sql,params)
            if msg == 'Changed successfully':
                flash('注册成功')
                return render_template("login.html")
            else:
                flash('注册失败')
                return render_template('register.html')
    else:
        return render_template('register.html')

@app.route("/index", methods = ['POST', 'GET'])
def index():
    if 'email' not in session:
        return redirect(url_for('login'))
    else:
        loggedIn, userName = getLoginDetails()
        sql = "SELECT avatar_url FROM chatroom.users WHERE email = %s"#获取头像
        params = [session['email']]
        avatar_url = query.query(sql, params)
        sql = "SELECT user_name,users.avatar_url,users.email FROM chatroom.users" #获取用户名
        users = query.query_no(sql)
        return render_template("index.html",userName = userName,avatar_url=avatar_url[0][0],users = users)

@app.route("/chatroom", methods = ['POST', 'GET'])
def chatroom():
    if 'email' not in session:
        return redirect(url_for('login'))
    else:
        loggedIn, userName = getLoginDetails()
        sql = "SELECT messages.content,messages.create_time,users.user_name,users.avatar_url,messages.user_id FROM chatroom.messages,chatroom.users where messages.user_id = users.user_id"
        message = query.query_no(sql)
        sql = "SELECT user_name,users.avatar_url FROM chatroom.users"
        users = query.query_no(sql)
        sql = "SELECT avatar_url FROM chatroom.users WHERE email = %s"
        params = [session['email']]
        avatar_url = query.query(sql, params)
        newMessage = []
        for row in message:
            if (row[0].find('static/files/img1/') != -1):
                img = row[0][row[0].find('static/files/img1/'):]
                text = row[0][:row[0].find('static/files/img1/')]
                row = list(row)
                row[0] = [img, text]
                newMessage.append(row)
            else:
                img = 'none'
                text = row[0]
                row = list(row)
                row[0] = [img, text]
                newMessage.append(row)
            print(row[0][0], row[0][1])
        return render_template("chatroom.html",userName = userName,message = newMessage,users = users,avatar_url = avatar_url)

#连接聊天室
@socketio.on('connect', namespace='/chatroom')
def connect():
    print('加入聊天成功')
    users.append(request.sid)

#接收聊天信息
@socketio.on('text', namespace='/chatroom')
def text(information):
    text = information.get('text')
    img = information.get('img')
    user_name = session.get('user') #获取用户名称
    sql = "SELECT user_id FROM chatroom.users WHERE email = %s"
    params = [session['email']]
    user_id = query.query(sql, params)  #获取用户ID
    create_time = datetime.datetime.now()
    create_time = datetime.datetime.strftime(create_time, '%Y-%m-%d %H:%M:%S')
    sql = 'INSERT INTO chatroom.messages (content,user_id, create_time) VALUES (%s,%s,%s)'
    params = [text + img, user_id, create_time]
    query.update(sql, params)  #将聊天信息插入数据库，更新数据库
    sql = "SELECT avatar_url FROM chatroom.users WHERE email = %s"
    params = [session['email']]
    avatar_url = query.query(sql, params)  #获取用户头像
    #返回聊天信息给前端
    for user in users: 
        print(user)
        emit('message',  {
        'user_name': user_name,
        'text': text,
        'create_time': create_time,
        'avatar_url':avatar_url,
        'img': img
    }, broadcast=False, room=user)

#连接主页
@socketio.on('Iconnect', namespace='/index')
def Iconnect():
    print('连接成功')

#接收更换的头像的路径
@socketio.on('avatar_url' ,namespace='/index')
def avatar_url(information):
    email = session['email']
    avatar_url = information.get('avatar_url')
    sql = "UPDATE chatroom.users SET avatar_url = %s WHERE email = %s "
    params = [avatar_url,email]
    query.update(sql, params)

if __name__ == '__main__':
    #app.run(debug=True, use_reloader=False)
    socketio.run(app, host='0.0.0.0', port=8000)
