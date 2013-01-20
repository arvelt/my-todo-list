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

        tasks_query = Task.all().filter("user_id", id).order("-create_time")
        tasks = tasks_query.fetch(50)
 
        #テンプレート内でstrが使えないので、ここでストリング化したキーをモデルに入れておく       
        for task in tasks :
            if task.str_key_id == None :
                task.str_key_id = str(task.key())
        
        template_values = {
            'tasks': tasks
        }
        
        template = jinja_environment.get_template('index.html')
        self.response.headers["Content-Type"] = "text/html; charset=utf-8"
        self.response.out.write(template.render(template_values))

class AddTask(webapp2.RequestHandler):
    
    #--------------------
    #タスクモデル一覧の取得
    #htmlの作成
    #--------------------    
    def post(self):

        #リクエストパラメータを取得
        task_content = self.request.get('send_content')
        req_duedate = self.request.get('send_duedate') #=>2013-01-19
        req_time = self.request.get('send_duetime')    #=>03:00

        logging.debug("key:"+self.request.get('key'))
        logging.debug("content:"+task_content)
        logging.debug("dudate"+req_duedate)
        logging.debug("duetime"+req_time)

        #日付と時間をdatetime型に統一        
        task_duedate = datetime.datetime.strptime(req_duedate, '%Y-%m-%d')
        task_time = datetime.datetime.strptime(req_time, '%H:%M')

        #１つのdatetimeとして生成
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

        renderTaskListHtml(self)


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

        renderTaskListHtml(self)


class DeleteTask(webapp2.RequestHandler):    
    def post(self):

        #keyを取得
        key = self.request.get('key')
        logging.debug("key:"+key)
        task = Task.get(db.Key(key))

        logging.debug("task user_id:"+task.user_id)
        logging.debug("current user:"+users.get_current_user().user_id())

        #自分のタスクのみ消せる
        if (task.user_id != users.get_current_user().user_id()):
            self.redirect('/')

        task.delete()

        renderTaskListHtml(self)

def renderTaskListHtml(self):
    if users.get_current_user():
        id = users.get_current_user().user_id()
    
    tasks_query = Task.all().filter("user_id", id).order("-create_time")
    tasks = tasks_query.fetch(50)

    #テンプレート内でstrが使えないので、ここでストリング化したキーをモデルに入れておく       
    for task in tasks :
        if task.str_key_id == None :
            task.str_key_id = str(task.key())
    
    template_values = {
        'tasks': tasks
    }
    
    template = jinja_environment.get_template('list.html')
    self.response.headers["Content-Type"] = "text/html; charset=utf-8"
    self.response.out.write(template.render(template_values))


app = webapp2.WSGIApplication([
                               ('/', MainPage),
                               ('/add', AddTask),
                               ('/update', UpdateTask),
                               ('/delete', DeleteTask)
                               ],debug=True)

