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

def escape_html(s):
    return s.replace("&", "&amp;").replace(">", "&gt;").replace("<", "&lt;").replace("\"", "&quot;")

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

rot_form = """
        <h3>Enter some text to ROT13:</h3>
        <form method="post">
            <textarea name="text" style="width:400px;height:100px">%(rotted)s</textarea>
            <br>
            <input type="submit">
        </form>
"""

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

app = webapp2.WSGIApplication([('/', MainHandler), ("/thanks", ThanksHandler), ("/rot13", RotHandler)],
                              debug=True)
