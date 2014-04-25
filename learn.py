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

form = """
<form method = "post" action = "/testform">
   <input name = 'name'>
   <input type = 'submit'>
</form>
"""

form1 = """
<form>
<label>
One
<input type = 'radio' name = 'q' value = 'one'>
</label>

<label>
Two
<input type = 'radio' name = 'q' value = 'two'>
</label>

<label>
Three
<input type = 'radio' name = 'q' value = 'three'>
</label>

<br>
<input type = 'submit'>
</form>
"""
#type learnt: text, checkbox, password, radio
#radio: same name gets only one choice
#radio: add value parameter to differentiate them
#radio: add lable element to add text

#dropdown
form2 = """
<form>
<select name = 'q'>
   <option value = '1'>the long option one</option>
   <option value = '2'>the long option two</option>
   <option value = '3'>the long option three</option>
</select>
<input type = 'submit'>
</form>
"""
#dropdown: value makes the /?.. shorter if option is long


form3 = """
<form method = 'post'>
What is your birthday?
<br>
Month
<input type = 'text' name = 'month'>
Day
<input type = 'text' name = 'day'>
Year
<input type = 'text' name = 'year'>
<br>
<br>
<input type = 'submit'>
</form>
"""

class MainHandler(webapp2.RequestHandler):
  #this is used to draw the form
  def get(self):
    self.response.headers['Content-Type'] = 'text/html'
    self.response.out.write(form3)

  # post method to match the post method in form3
  def post(self):
    self.response.out.write("Thanks!")

# class TestHandler(webapp2.RequestHandler):
#   def get(self): # post method hides the "?name=hello"
#     # self.response.headers['Content-Type'] = 'text/plain'
#     # self.response.out.write(self.request)
#     # q = self.request.get("name")
#     # self.response.out.write(q)
#     q = self.request.get('q')
#     self.response.out.write(q)

      
app = webapp2.WSGIApplication([
  ('/', MainHandler)
  # ('/testform', TestHandler)
  ], debug=True)
