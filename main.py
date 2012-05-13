#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import webapp2
import jinja2
import hmac
import re
import random
import string
import hashlib

from google.appengine.ext import db
        
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

SECRET = "lesecretdaj00liana"
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
PASS_RE = re.compile(r"^.{3,20}$")

#===== DADOS =====
class Post(db.Model):
    title = db.StringProperty(required = True)
    post = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class User(db.Model):
    username = db.StringProperty(required = True)
    hashed_pass = db.StringProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

#===== RESTO =====
def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(5))

# implement the function make_pw_hash(name, pw) that returns a hashed password 
# of the format: 
# HASH(name + pw + salt),salt
# use sha256

def make_pw_hash(name, pw, salt=""):
    if not salt:
        salt = make_salt()
    return "%s|%s" % (hashlib.sha256(name + pw + salt).hexdigest(), salt)

def hash_str(s):
    return hmac.new(SECRET, s).hexdigest()

def make_secure_val(s):
    return "%s|%s" % (s, hash_str(s))

def check_secure_val(h):
    s1 = h.split("|")[0]
    if h == make_secure_val(s1):
        return s1

def valid_pw(name, pw, h):
    if make_pw_hash(name, pw, h.split("|")[1]) == h:
        return True

def valid_username(username):
    return USER_RE.match(username)

def valid_email(email):
    return EMAIL_RE.match(email)

def valid_password(password):
    return PASS_RE.match(password)

def defCookie(self, name, val):
    self.response.headers.add_header("Set-Cookie", "%s=%s; Path=/" % (name, str(val)))
    self.redirect("/welcome")

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class NewPostHandler(Handler):
    def render_front(self, title = "", post = "", error = ""):
        self.render("newpost.html", error = error, title = title, post = post)

    def get(self):
        self.render_front()

    def post(self):
        title = self.request.get("subject")
        post = self.request.get("content")

        if title and post:
            p = Post(title = title, post = post)
            p.put()

            self.redirect("/blog/")
        else:
            error = "Title and/or post is necessary"
            self.render_front(title, post, error)

class PostPermalink(Handler):
    def get(self, post_id):
        post = Post.get_by_id(int(post_id))

        if post:
            self.render("post.html", post=post)
        else:
            self.render("post.html", error="Blog post not found!")

class BlogHandler(Handler):
    def get(self):
        posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC")
        self.render("blog.html", posts = posts)

class LogoutHandler(Handler):
    def get(self):
        defCookie(self, "user", "")


class LoginHandler(Handler):
    def write_login_form(self, username="", password="", login_error=""):
        self.render("login.html", username = username, password = password, login_error = login_error)

    def get(self):
        self.write_login_form()

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        if username and password:
            u = db.GqlQuery("SELECT * FROM User WHERE username = :1", username)
            user = u.get()
            if user:
                salt = user.hashed_pass.split("|")[1]
                h = make_pw_hash(username, password, salt)
                valid_user = (user.hashed_pass == h)
                if valid_user:
                    cookie_user = make_secure_val(username)
                    defCookie(self, "user", cookie_user)
        login_error = "Invalid login"
        self.write_login_form(username, password, login_error)

class SignupHandler(Handler):
    def write_signup_form(self, username="", username_error="", password="", password_error="", 
                            verify="", verify_error="", email="", email_error=""):
        self.render("signup.html", username=username, username_error= username_error, 
                                    password= password, password_error= password_error, 
                                    verify= verify, verify_error= verify_error,
                                    email= email, email_error= email_error)
    
    def get(self):
        self.write_signup_form()
        
    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        verify = self.request.get("verify")
        email = self.request.get("email")
        username_valid = valid_username(username)
        password_valid = password and password == verify and valid_password(password)
        email_valid = not email or valid_email(email)
        if username_valid and password_valid and email_valid:
            h = make_pw_hash(username, password)
            u = User(username = username, hashed_pass = h)
            u.put()
            cookie_user = make_secure_val(username)
            defCookie(self, "user", cookie_user)
        else:
            user_error_msg = ""
            pass_error_msg = ""
            verify_error_msg = ""
            email_error_msg = ""
            if not username_valid:
                user_error_msg = "Invalid username"
            if not password_valid:
                if not password:
                    pass_error_msg = "Password can't be blank"
                elif password != verify:
                    verify_error_msg = "Passwords don't match"
                elif not valid_password(password):
                    pass_error_msg = "Invalid password"
            if email:
                if not email_valid:
                    email_error_msg = "Invalid email"
            self.write_signup_form(username, user_error_msg, "", pass_error_msg, "", verify_error_msg, email, email_error_msg)

class WelcomeHandler(Handler):
    def get(self):
        user_str = self.request.cookies.get("user")
        if user_str:
            user_val = check_secure_val(user_str)
            if user_val:
                self.render("welcome.html", user=user_val)
            else:
                self.redirect("/signup")
        else:
            self.redirect("/signup")

class MainHandler(Handler):
    def get(self):
        visits = 0
        visit_cookie_str = self.request.cookies.get("visits")
        if visit_cookie_str:
            cookie_val = check_secure_val(visit_cookie_str)
            if cookie_val:
                visits = int(cookie_val)

        visits += 1

        new_cookie_val = make_secure_val(str(visits))
        self.response.headers.add_header("Set-Cookie", "visits=%s" % new_cookie_val)

        if visits > 1000:
            self.write("cool")
        else:
            self.write("You have been here %s" % visits)

        self.render("front.html")
        
    
#, ("/welcome", WelcomeHandler)
app = webapp2.WSGIApplication([('/', MainHandler), ("/blog", BlogHandler), ("/blog/newpost", NewPostHandler), 
                                (r'/blog/(\d+)', PostPermalink), ("/signup", SignupHandler), ("/welcome", WelcomeHandler),
                                ("/login", LoginHandler), ("/logout", LogoutHandler)],
                              debug=True)
