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
import re # regex
import jinja2
import os # template_dir
import hashlib # hash, salt, md5 etc
import hmac # hmac even better encryption
import random # ramdom salt
import string
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), '')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASS_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")

def rot13letter(l):
  if l >= 'a' and l <= 'z':
    return chr((((ord(l) - ord('a')) + 13) % 26) + ord('a'))
  elif l >= 'A' and l <= 'Z':
    return chr((((ord(l) - ord('A')) + 13) % 26) + ord('A'))
  else:
    return l

def rot13(text):
  return "".join(map(rot13letter, text))

# no longer necessary, included in jinja template
# def escape_html(s):
#   for (a, b) in (("&", "&amp;"),(">", "&gt;"),
#                  ("<", "&lt;"), ("\"", "&quot;")):
#         s = s.replace(a, b)
#   return s

SECRET = "waterlooo"

# using hashlib md5 or even better: hmac with a secret string mixed with string s
def hash_str(s):
  # return hashlib.md5(s).hexdigest()
  return hmac.new(SECRET, s).hexdigest()

def make_secure_val(s):
  return "%s|%s" % (s, hash_str(s))

def check_secure_val(h):
  s = h.split("|")[0]
  if make_secure_val(s) == h:
    return s
    
# returns a hashed password using sha256 of the format: 
# HASH(name + pw + salt),salt

def make_salt():
  return "".join(random.choice(string.letters) for x in xrange(5))

def make_pw_hash(name, pw):
  salt = make_salt()
  hashh = hashlib.sha256(name + pw + salt).hexdigest()
  return "%s,%s" % (hashh, salt)

def valid_pw(name, pw, h):
  check_hash = h.split(",")[0]
  check_salt = h.split(",")[1]
  return check_hash == hashlib.sha256(name + pw + check_salt).hexdigest()

# using jinja template to simplify code
class Handler(webapp2.RequestHandler):
  def write(self, *a, **kw):
    self.response.out.write(*a, **kw)
  def render_str(self, template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)
  def render(self, template, **kw):
    self.write(self.render_str(template, **kw))

class MainHandler(Handler):
  def get(self):
    self.render("/html/welcome.html")

    # visits = 0
    # visit_cookie_str = self.request.cookies.get('visits')
    # if visit_cookie_str:
    #   cookie_val = check_secure_val(visit_cookie_str)
    #   if cookie_val:
    #     visits = int(cookie_val)

    # visits += 1

    # new_cookie_val = make_secure_val(str(visits))

    # self.response.headers.add_header("Set-Cookie", "visits=%s" % new_cookie_val)

    # if visits > 10:
    #   self.write("You are my best friend! You've been here %s times!" % visits)
    # else:
    #   self.write("You've been here %s times!" % visits)

class CS253Handler(Handler):
  def get(self):
    self.render("/cs253/main.html")

class Rot13Handler(Handler):
  def get(self):
    self.render("/cs253/rot13form.html")
  def post(self):
    usertext = self.request.get("text")
    r = rot13(usertext)
    self.render("/cs253/rot13form.html", text = r)

class YouTubeHandler(Handler):
  def get(self):
    self.render("/cs253/learntocode.html")

class SignUpHandler(Handler):
  def write_form(self, username, password, verify, email, nameerr, passerr, matcherr, emailerr):
    self.response.out.write(signup % {"username" : username,
      "password" : password, "verify" : verify, "email": email, "nameerr" : nameerr, "passerr" : passerr, "matcherr" : matcherr, "emailerr" : emailerr})
  def get(self):
    self.render("/cs253/signup.html")

  def post(self):
    username = self.request.get("username")
    password = self.request.get("password")
    verify = self.request.get("verify")
    email = self.request.get("email")
    nameerr = ""
    passerr = ""
    matcherr = ""
    emailerr = ""
    
    if not USER_RE.match(username):
      nameerr = "That's not a valid username."
    if not PASS_RE.match(password):
      passerr = "That wasn't a valid password."
    if password != verify:
      matcherr = "Your passwords didn't match."
    if email and not EMAIL_RE.match(email):
      emailerr = "That's not a valid email."

    raw_name = self.request.cookies.get("name")
    if raw_name:
      that_name = raw_name.split("|")[0]
      if that_name == username:
        nameerr = "The user already exists"

    if (nameerr or passerr or matcherr or emailerr):
      self.render("/cs253/signup.html", username = username, nameerr = nameerr, password = "", passerr = passerr, verify = "", matcherr = matcherr, email = email, emailerr = emailerr)
    else:
      name = username
      salted_name = make_secure_val(str(name))
      self.response.headers.add_header("Set-Cookie", "name=%s" % salted_name)
      self.redirect("/cs253/welcome")

class WelcomeHandler(Handler):
  def get(self):
    raw_name = self.request.cookies.get("name")
    if raw_name:
      cookie_val = check_secure_val(raw_name)
      if cookie_val:
        username = str(cookie_val)
        self.write("<h1>Welcome, %s!</h1>" % username)
      else:
        self.redirect("/cs253/signup")
    else:
      self.redirect("/cs253/signup")
    

class Message(db.Model):
  title = db.StringProperty(required = True)
  message = db.TextProperty(required=  True)
  created = db.DateTimeProperty(auto_now_add = True)

class MessageHandler(Handler):
  def render_message(self, title="", message="", error=""):
    messages = db.GqlQuery("SELECT * FROM Message ORDER BY created DESC")
    self.render("/cs253/message.html", title=title, message=message, error=error, messages = messages)

  def get(self):
    self.render_message()

  def post(self):
    title = self.request.get("title")
    message = self.request.get("message")

    if title and message:
      a = Message(title = title, message = message)
      a.put()
      self.redirect("/cs253/message")
    else:
      error = "You need both a title and message!"
      self.render_message(title, message, error)

class ResumeHandler(Handler):
  def get(self):
    self.render("/html/resume.html")

class TechnicalHandler(Handler):
  def get(self):
    self.render("/html/technical.html")
    
class PEulerHandler(Handler):
  def get(self):
    self.render("/html/peuler.html")

class CreditCCHandler(Handler):
  def get(self):
    self.render("/html/creditcard.html")

class BlogPost(db.Model):
  subject = db.StringProperty(required = True)
  content = db.TextProperty(required = True)
  created = db.DateTimeProperty(auto_now_add = True)
  last_modified = db.DateTimeProperty(auto_now = True)

class BlogHandler(Handler):
  def render_blog(self, subject="", content="", error=""):
    blogposts = db.GqlQuery("SELECT * from BlogPost ORDER BY created DESC LIMIT 30")
    self.render("/html/blog.html", subject=subject, content=content, error=error, blogposts=blogposts)
  def get(self):
    self.render_blog()

class NewPostHandler(Handler):
  def get(self):
    self.render("/html/newpost.html")
  def post(self):
    subject = self.request.get("subject")
    content = self.request.get("content")
    if subject and content:
      a = BlogPost(subject = subject, content = content)
      a.put()
      self.redirect("/blog/%s" % str(a.key().id()))
    else:
      error = "You need both subject and content!"
      self.render("/html/newpost.html", subject=subject, content=content, error=error)

class PostPageHandler(Handler):
  def get(self, post_id):
    key = db.Key.from_path("BlogPost", int(post_id))
    post = db.get(key)
    if not post: #404
      self.redirect("/blog")
      return
    self.render("/html/permanent.html", entry=post)


app = webapp2.WSGIApplication([
  ('/', MainHandler),
  ('/cs253', CS253Handler),
  ('/cs253/rot13', Rot13Handler),
  ('/cs253/learntocode', YouTubeHandler),
  ('/cs253/signup', SignUpHandler),
  ('/cs253/welcome',WelcomeHandler),
  ('/cs253/message', MessageHandler),
  ('/technical', TechnicalHandler),
  ('/resume', ResumeHandler),
  ('/blog', BlogHandler),
  ('/blog/newpost', NewPostHandler),
  ('/blog/([0-9]+)', PostPageHandler),
  ('/peuler', PEulerHandler),
  ('/credit-card', CreditCCHandler)
  ], debug=True)