#coding: utf-8
import datetime
import webapp2

import logging

logging.getLogger().setLevel(logging.DEBUG)

from google.appengine.ext import db
from google.appengine.api import users

class Task(db.Model):
#    user = db.ReferenceProperty(users)
    user_id = db.StringProperty()
    content = db.StringProperty()
    status = db.StringProperty()
    create_time = db.DateTimeProperty(auto_now_add=True)
    due_datetime = db.DateTimeProperty()

class MainPage(webapp2.RequestHandler):

    #--------------------
    #タスクモデル一覧の取得
    #htmlの作成
    #--------------------
    def get(self):
                
        #ログインしていなければログインページへ
        id = ''
        if users.get_current_user():
            id = users.get_current_user().user_id()
        else:
            self.redirect(users.create_login_url(self.request.uri))

        tasks = Task.all().filter("user_id", id).order("-create_time")
        
        #html生成
        self.response.headers["Content-Type"] = "text/html; charset=utf-8"
        self.response.out.write("""
        <html>
            <body>
                <form action="/add" method="post">
        """)

        self.response.out.write("""
                    <table>
                        <tr>
                        <td><input type="text" name="send_content"></td>
                        <td><input type="date" name="send_duedate"></td>
                        <td><input type="time" name="send_duetime"></td>
                        <td><input type="submit" value="追加"></td>
                        </tr>
                    </table>
        """)


        self.response.out.write("""
                    <table>
                    <tr><td>タイトル</td><td>期限</td></tr>
        """)

        #タスク一覧
        for task in tasks :
            self.response.out.write('<tr><td>%s</td><td>%s %s</td></tr>' % (
            task.content,task.status,task.due_datetime)
            )
                        
        self.response.out.write("""
                    </table>
                </form>
            <body>
        </html>
        """)

class AddTask(webapp2.RequestHandler):
    
    #--------------------
    #タスクモデル一覧の取得
    #htmlの作成
    #--------------------
    def post(self):

        #リクエストパラメータを取得
        
        #内容を取得
        task_content = self.request.get('send_content')
        
        #日付を取得
        req_duedate = self.request.get('send_duedate') #=>2013-01-19
        task_duedate = datetime.datetime.strptime(req_duedate, '%Y-%m-%d')

        #時間を取得
        req_time = self.request.get('send_duetime')    #=>03:00
        task_time = datetime.datetime.strptime(req_time, '%H:%M')

        #datetimeを生成
        duedate = datetime.datetime(
        task_duedate.year ,
        task_duedate.month ,
        task_duedate.day ,
        task_time.hour ,
        task_time.minute ,
        0
        )
 
        logging.debug(task_duedate)
        logging.debug(task_time)
        logging.debug(duedate)



        #ユーザーIDをキーにして、タスクモデルを追加

        task = Task()
        
        if users.get_current_user():
            task.user_id = users.get_current_user().user_id()

        task.content = task_content
        task.due_datetime = duedate
        task.put()
        
        self.redirect('/')

class TaskList(webapp2.RequestHandler):
    def post(self):
        
        id = ""
        if users.get_current_user():
            id = users.get_current_user().user_id()
        else:
            self.redirect(users.create_login_url(self.request.uri))

        tasks = Task.all().filter("user_id", id).order("-create_time")

        tasks.to_json

        self.response.out.write("""
        <html>
        <title></title>
        <body>
        AddtaskPage
        </body>
        </html>
        """)


class SetDoneTask(webapp2.RequestHandler):    
    def post(self):
        self.response.out.write("""
        <html>
        <title></title>
        <body>
        SetDoneTaskPage
        </body>
        </html>
        """)


class DeleteTask(webapp2.RequestHandler):    
    def post(self):
        self.response.out.write("""
        <html>
        <title></title>
        <body>
        DeleteTaskPage
        </body>
        </html>
        """)


app = webapp2.WSGIApplication([
                               ('/', MainPage),
                               ('/list', TaskList),
                               ('/add', AddTask),
                               ('/done', SetDoneTask),
                               ('/delete', DeleteTask)
                               ],debug=True)

