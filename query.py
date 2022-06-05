import pymysql


def query(sql,params):  #数据库查询函数
    # 打开数据库连接
    db = pymysql.connect(host='localhost', user='root', password='954595', database='chatroom', charset='utf8')
    cursor = db.cursor()              # 使用 cursor() 方法创建一个游标对象 cursor
    try:
        cursor.execute(sql,params)           # 使用 execute() 方法执行 SQL 查询
        result = cursor.fetchall()    #获取查询结果
        db.commit()                #执行sql语句
        return result              #返回查询结果
        #print('query success')
    except:
        # print('query loss')
        db.rollback()              #发生错误时回滚
    cursor.close()
    db.close()                     #关闭数据库连接

def query_no(sql):  #数据库查询函数,不带参数
    # 打开数据库连接
    db = pymysql.connect(host='localhost', user='root', password='954595', database='chatroom', charset='utf8')
    cursor = db.cursor()              # 使用 cursor() 方法创建一个游标对象 cursor
    try:
        cursor.execute(sql)           # 使用 execute() 方法执行 SQL 查询
        result = cursor.fetchall()    #获取查询结果
        db.commit()                #执行sql语句
        return result              #返回查询结果
        #print('query success')
    except:
        # print('query loss')
        db.rollback()              #发生错误时回滚
    cursor.close()
    db.close()                     #关闭数据库连接

def update(sql,params):
    """
    功能; 使用sql语句更新数据库中员工信息。
    参数: sql(string)
    """
    db = pymysql.connect(host='localhost', user='root', password='954595', database='chatroom', charset='utf8')
    cur = db.cursor()           # 使用 execute() 方法执行 SQL 查询
    try:
        cur.execute(sql,params)
        db.commit()             #执行sql语句
        return "Changed successfully"
    except:
        db.rollback()           #发生错误时回滚
        return "Failed"
    cur.close()
    db.close()                  #关闭数据库连接
