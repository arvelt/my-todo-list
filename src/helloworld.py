# -*- coding: utf-8 -*-

import datetime
import webapp2
import jinja2
import os
import logging

from google.appengine.ext import db
from google.appengine.api import users

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

logging.getLogger().setLevel(logging.DEBUG)

class Task(db.Model):
    STATUS_NO_FINISH = 1
    STATUS_FINISH = 2
    
    str_key_id = db.StringProperty()
    user_id = db.StringProperty()
    content = db.StringProperty()
    status = db.IntegerProperty(default=STATUS_NO_FINISH)
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

        #tasks = Task.all().filter("user_id", id).order("-create_time")
        tasks_query = Task.all().filter("user_id", id).order("-create_time")
        tasks = tasks_query.fetch(20)
        
        for task in tasks :
            if task.str_key_id == None :
                task.str_key_id = str(task.key())
        
        template_values = {
            'tasks': tasks
        }
        
        template = jinja_environment.get_template('index.html')
        self.response.headers["Content-Type"] = "text/html; charset=utf-8"
        self.response.out.write(template.render(template_values))
        
        #html生成
#===============================================================================
#        self.response.out.write("""
#        <html>
#            <head>
#            <script src="//ajax.googleapis.com/ajax/libs/jquery/1.8.3/jquery.min.js"></script>
#            <script type="text/javascript">
#            function doAddTask(key){
#                var form = document.getElementById('form');
#                var hide = document.createElement('input'); 
#                hide.type = 'hidden'; 
#                hide.name = 'key'; 
#                hide.id = 'key'; 
#                hide.value = key; 
#                form.appendChild(hide); 
#                form.action = '/add';
#                form.submit();
#            }
#            function doDeleteTask(key){
#                var form = document.getElementById('form');
#                var hide = document.createElement('input'); 
#                hide.type = 'hidden'; 
#                hide.id = 'key'; 
#                hide.name = 'key'; 
#                hide.value = key; 
#                form.appendChild(hide); 
#                form.action = '/delete';
#                form.submit();
#            }
#            function doUpdateTask(key){
#                var form = document.getElementById('form');
#                var hide = document.createElement('input'); 
#                hide.type = 'hidden'; 
#                hide.name = 'key'; 
#                hide.id = 'key'; 
#                hide.value = key; 
#                
#                var sendstatus = document.getElementById('status_'+key); 
#                
#                var sta = document.createElement('input'); 
#                sta.type = 'hidden'; 
#                sta.name = 'status'; 
#                sta.value = sendstatus.value; 
# 
#                form.appendChild(hide); 
#                form.appendChild(sta); 
#                form.action = '/update';
#                form.submit();
#            }
#            window.onload=function(){
#                var statuses = document.getElementsByName("status");
#                var inits = document.getElementsByName("initstatus");
#                for( var i = 0 ; i < statuses.length ; i++ ){
#                    var status = statuses[i];
#                    var init = inits[i];
#                    var status = statuses[i];
#                    var initSelected = init.value;
#                    status.options[initSelected-1].selected = true;
#                }
#            }
#            </script>
#            </head>
#            <body>
#                <form id="form" action="" method="post">
#        """)
# 
#        self.response.out.write("""
#                    <table name="input_task">
#                        <tr>
#                        <td><input type="text" name="send_content"></td>
#                        <td><input type="date" name="send_duedate"></td>
#                        <td><input type="time" name="send_duetime"></td>
#                        <td><input type="submit" value="追加" onclick="doAddTask()"></td>
#                        </tr>
#                    </table>
#        """)
# 
# 
#        self.response.out.write("""
#                    <table name="tasks">
#                    <tr><td>タイトル</td><td>状況</td><td>期限</td></tr>
#        """)
# 
#        #タスク一覧
#        for task in tasks :
#            self.response.out.write(u"""
#            <tr>
#                <td>%s</td>
#                <td>
#                    <select id="status_%s" name="status">
#                    <option value="1">未完了</option>
#                    <option value="2">完了</option>
#                    </select>
#                    <input type="hidden" name="initstatus" value="%s"/>
#                </td>
#                <td>%s</td>
#                <td><input type="submit" value="更新" onclick="doUpdateTask('%s')"></td>
#                <td><input type="submit" value="削除" onclick="doDeleteTask('%s')"></td>
#            </tr>""" % (
#            task.content,
#            str(task.key()),
#            task.status,
#            task.due_datetime,
#            str(task.key()),
#            str(task.key()))
#            )
#                        
#        self.response.out.write("""
#                    </table>
#                </form>
#            <body>
#        </html>
#        """)
#===============================================================================

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

        #タスクモデルを追加
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


class UpdateTask(webapp2.RequestHandler):    
    def post(self):

        #パラメータを取得
        status = self.request.get('status')
        key = self.request.get('key')
        
        logging.debug("updatetask")
        logging.debug("status:"+status)
        logging.debug("key:"+key)

        #タスクモデルを取得して更新
        task = Task.get(db.Key(key))
        task.status = int(status)
        task.put()

        self.redirect('/')


class DeleteTask(webapp2.RequestHandler):    
    def post(self):

        #keyを取得
        key = self.request.get('key')
        task = Task.get(db.Key(key))

        logging.debug("task user_id:"+task.user_id)
        logging.debug("current user:"+users.get_current_user().user_id())

        #自分のタスクのみ消せる
        if (task.user_id != users.get_current_user().user_id()):
            self.redirect('/')

        task.delete()

        self.redirect('/')
        
app = webapp2.WSGIApplication([
                               ('/', MainPage),
                               ('/list', TaskList),
                               ('/add', AddTask),
                               ('/update', UpdateTask),
                               ('/delete', DeleteTask)
                               ],debug=True)

