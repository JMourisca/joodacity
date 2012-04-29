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
import webapp2
import re

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
PASS_RE = re.compile(r"^.{3,20}$")

months = ['January',
          'February',
          'March',
          'April',
          'May',
          'June',
          'July',
          'August',
          'September',
          'October',
          'November',
          'December']

month_abbs = dict((m[:3].lower(), m) for m in months)

def rot13(text):
    res = ""
    for i in text:
        n = ord(i)
        if n >= 65 and n <= 90: #A - Z
            new = n + 13
            if new > 90:
                new = 65 + (new - 90 - 1)
        elif n >= 97 and n <= 122: #A - Z
            new = n + 13
            if new > 122:
                new = 97 + (new - 122 - 1)
        else:
            new = n
        res = res + chr(new)
    print text, res
          
def valid_month(month):
    if month:
        short_month = month[:3].lower()
        return month_abbs.get(short_month)

def valid_day(day):
    try: 
        d = int(day)
        return d if d >= 1 and d <= 31 else None
    except:
        return None

def valid_year(year):
    if year and year.isdigit():
        y = int(year)
        return y if y > 1900 and y <=2020 else None
    else:
        return None
    
def valid_username(username):
    return USER_RE.match(username)

def valid_email(email):
    return EMAIL_RE.match(email)

def valid_password(password):
    return PASS_RE.match(password)

def escape_html(s):
    return s.replace("&", "&amp;").replace(">", "&gt;").replace("<", "&lt;").replace("\"", "&quot;")
    
def rot13(text):
    res = ""
    for i in text:
        n = ord(i)
        if n >= 65 and n <= 90: #A - Z
            new = n + 13
            if new > 90:
                new = 65 + (new - 90 - 1)
        elif n >= 97 and n <= 122: #A - Z
            new = n + 13
            if new > 122:
                new = 97 + (new - 122 - 1)
        else:
            new = n
        res = res + chr(new)
    return res

form = """ &=&amp;amp;
        <form method="post">
            What's your birthday?
            <br>
            <label>
                Day
                <input type="text" name="day" value="%(day)s">
            </label>
            <label>
                Month
                <input type="text" name="month" value="%(month)s">
            </label>
            <label>
                Year
                <input type="text" name="year" value="%(year)s">
            </label>
            <div style="color:red">%(error)s</div>
            <br>
            <br>
            <input type="submit">
        </form>
"""

rot_form = """
        <h3>Enter some text to ROT13:</h3>
        <form method="post">
            <textarea name="text" style="width:400px;height:100px">%(rotted)s</textarea>
            <br>
            <input type="submit">
        </form>
"""

signup_form = """
<style>.error{color:red}</style>
<h2>Signup</h2>
    <form method="post">
      <table>
        <tr>
          <td class="label">Username</td>
          <td>
            <input type="text" name="username" value="%(username)s">
          </td>
          <td class="error">%(username_error)s</td>
        </tr>
        <tr>
          <td class="label">Password</td>
          <td>
            <input type="password" name="password" value="%(password)s">
          </td>
          <td class="error">%(password_error)s</td>
        </tr>
        <tr>
          <td class="label">Verify Password</td>
          <td>
            <input type="password" name="verify" value="%(verify)s">
          </td>
          <td class="error">%(verify_error)s</td>
        </tr>
        <tr>
          <td class="label">Email (optional)</td>
          <td>
            <input type="text" name="email" value="%(email)s">
          </td>
          <td class="error">%(email_error)s</td>
        </tr>
      </table>

      <input type="submit">
    </form>
"""

welcome = "<h1>Welcome, %(username)s!</h1>"

class SignupHandler(webapp2.RequestHandler):
    def write_signup_form(self, username="", username_error="", password="", password_error="", 
                            verify="", verify_error="", email="", email_error=""):
        self.response.out.write(signup_form % {"username": username, "username_error": username_error, 
                                                "password": password, "password_error": password_error, 
                                                "verify": verify, "verify_error": verify_error,
                                                "email": email, "email_error": email_error})
    
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
            self.redirect("/welcome?username=" + username)
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

class WelcomeHandler(webapp2.RequestHandler):
    def get(self):
        username = self.request.get("username")
        self.response.out.write(welcome % {"username": username})
    
class RotHandler(webapp2.RequestHandler):
    def write_form_rot(self, rotted=""):
        self.response.out.write(rot_form % {"rotted": rotted})
    
    def get(self):
        self.write_form_rot()
        
    def post(self):
        rot_text = rot13(self.request.get("text"))
        self.write_form_rot(escape_html(rot_text))
        

class ThanksHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("Totally valid date.")

class MainHandler(webapp2.RequestHandler):
    def write_form(self, error="", day="", month="", year=""):
        self.response.out.write(form % {"error": error, 
                                        "day": escape_html(day),
                                        "month": escape_html(month),
                                        "year": escape_html(year)})
        
    def get(self):
        self.write_form()
    
    def post(self):
        user_month = self.request.get("month")
        user_day = self.request.get("day")
        user_year = self.request.get("year")
        
        month = valid_month(user_month)
        day = valid_day(user_day)
        year = valid_year(user_year)
        
        if not (month and day and year):
            self.write_form("Not valid.", user_day, user_month, user_year)
        else:
            self.redirect("/thanks")
#, ("/welcome", WelcomeHandler)
app = webapp2.WSGIApplication([('/', MainHandler), ("/thanks", ThanksHandler), ("/rot13", RotHandler), 
                                ("/signup", SignupHandler), ("/welcome", WelcomeHandler)],
                              debug=True)
