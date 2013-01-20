# -*- coding: utf-8 -*-

import datetime
import webapp2
import jinja2
import os
import logging
import jinja2_custom_filters

from google.appengine.ext import db
from google.appengine.api import users

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

jinja_environment.filters.update({
    "datetimeformat": jinja2_custom_filters.datetimeformat
})

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

class IndexPage(webapp2.RequestHandler):

    def get(self):

        #ログインしていなければログインリンク
        #ログインしていればメインページへのリンク
        user = users.get_current_user()
        if user:
            greeting = ("""<a href="/main">go now!</a> """)
        else:
            greeting = ("<a href=\"%s\">Sign in or register</a>." %
                        users.create_login_url("/main"))
            
        template_values = {
            'greeting' : greeting
        }
        
        template = jinja_environment.get_template('index.html')
        self.response.headers["Content-Type"] = "text/html; charset=utf-8"
        self.response.out.write(template.render(template_values))            
            
class MainPage(webapp2.RequestHandler):

    #--------------------
    #メインページの取得
    #タスク一覧を表示
    #--------------------
    def get(self):
                
        user_id = getUserIdOrGoLoginPage(self)

        #ログインユーザーを取得
        user = users.get_current_user()
        greeting = ("Welcome to todolist! , %s! (<a href=\"%s\">sign out</a>)" %
                    (user.nickname(), users.create_logout_url("/")))

        tasks_query = Task.all().filter("user_id", user_id).order("-create_time")
        tasks = tasks_query.fetch(50)
 
        #テンプレート内でstrが使えないので、ここでストリング化したキーをモデルに入れておく       
        for task in tasks :
            if task.str_key_id == None :
                task.str_key_id = str(task.key())

            
        template_values = {
            'tasks': tasks ,
            'greeting' : greeting
        }
                
        
        template = jinja_environment.get_template('main.html')
        self.response.headers["Content-Type"] = "text/html; charset=utf-8"
        self.response.out.write(template.render(template_values))

class AddTask(webapp2.RequestHandler):
    
    #--------------------
    #タスクモデルを追加する
    #取得しなおした一覧部分を返却
    #--------------------    
    def post(self):

        user_id = getUserIdOrGoLoginPage(self)

        #リクエストパラメータを取得
        task_content = self.request.get('send_content')
        req_duedate = self.request.get('send_duedatetime') #=>2013-01-19 3:00

        logging.debug("key:"+self.request.get('key'))
        logging.debug("content:"+task_content)
        logging.debug("dudate"+req_duedate)

        #日付時刻チェック   
        checkDateTime(self,req_duedate)
        duedate = datetime.datetime.strptime(req_duedate, '%Y-%m-%d %H:%M')

        #タスクモデルを追加
        task = Task()        
        task.user_id = user_id
        task.content = task_content
        task.due_datetime = duedate
        task.put()

        renderTaskListHtml(self)


class UpdateTask(webapp2.RequestHandler):

    #--------------------
    #タスクモデルを更新
    #取得しなおした一覧部分を返却
    #--------------------    
    def post(self):

        user_id = getUserIdOrGoLoginPage(self)

        #パラメータを取得
        content = self.request.get('content')
        req_datetime = self.request.get('datetime')
        status = self.request.get('status')
        key = self.request.get('key')

        logging.debug("updatetask")
        logging.debug("key:"+key)
        logging.debug("content:"+content)
        logging.debug("status:"+status)
        logging.debug("datetime:"+req_datetime)

        #日付時刻チェック   
        checkDateTime(self,req_datetime)
        checked_date_time = datetime.datetime.strptime(req_datetime, '%Y-%m-%d %H:%M')

        #タスクモデルを取得して更新
        task = Task.get(db.Key(key))
        task.status = int(status)
        task.content = content
        task.due_datetime = checked_date_time

        #自分のタスクなら更新
        if (task.user_id == user_id):
            task.put()

        renderTaskListHtml(self)


class DeleteTask(webapp2.RequestHandler):    

    #--------------------
    #タスクモデルを削除
    #取得しなおした一覧部分を返却
    #--------------------        
    def post(self):

        user_id = getUserIdOrGoLoginPage(self)

        #keyを取得
        key = self.request.get('key')
        logging.debug("key:"+key)
        task = Task.get(db.Key(key))

        logging.debug("task user_id:"+task.user_id)
        logging.debug("current user:"+users.get_current_user().user_id())

        #自分のタスクなら削除
        if (task.user_id == user_id):
            task.delete()

        renderTaskListHtml(self)

def renderTaskListHtml(self):

    #-------------------------
    #タスクのリストを取得
    #一覧部分のHtmlとして整形して返却
    #-------------------------
    
    user_id = users.get_current_user().user_id()
    
    tasks_query = Task.all().filter("user_id", user_id).order("-create_time")
    tasks = tasks_query.fetch(50)

    #テンプレート内でstrが使えないので、ここでストリング化したキーをモデルに入れておく       
    for task in tasks :
        if task.str_key_id == None :
            task.str_key_id = str(task.key())
    
    template_values = {
        'tasks': tasks ,
        'datetime' : datetime.datetime
    }
    
    template = jinja_environment.get_template('list.html')
    self.response.headers["Content-Type"] = "text/html; charset=utf-8"
    self.response.out.write(template.render(template_values))

def getUserIdOrGoLoginPage(self):

    #ログインしていればユーザーIDを返す
    #ログインしていなければログインページへ

    if users.get_current_user():
        return users.get_current_user().user_id()
    else:
        self.redirect(users.create_login_url(self.request.uri))

def checkDateTime(self,check_date_time):
    try :
        datetime.datetime.strptime(check_date_time, '%Y-%m-%d %H:%M')
    except ValueError:
        self.redirect("/")



app = webapp2.WSGIApplication([
                               ('/', IndexPage),
                               ('/main', MainPage),
                               ('/add', AddTask),
                               ('/update', UpdateTask),
                               ('/delete', DeleteTask)
                               ],debug=True)

