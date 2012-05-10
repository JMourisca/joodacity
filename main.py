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

from google.appengine.ext import db
        
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

SECRET = "lesecretdaj00liana"

def hash_str(s):
    return hmac.new(SECRET, s).hexdigest()

def make_secure_val(s):
    return "%s|%s" % (s, hash_str(s))

def check_secure_val(h):
    s1 = h.split("|")[0]
    if h == make_secure_val(s1):
        return s1

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Post(db.Model):
    title = db.StringProperty(required = True)
    post = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

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
        posts = odb.GqlQuery("SELECT * FROM Post ORDER BY created DESC")
        self.render("blog.html", posts = posts)

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
                                (r'/blog/(\d+)', PostPermalink)],
                              debug=True)
