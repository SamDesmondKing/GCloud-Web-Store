import os
import urllib
import logging

from google.appengine.ext import ndb
from google.appengine.api import users

import webapp2
import jinja2

PROJECT_ID = 'imposing-ring-270422'

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class user(ndb.Model):
    name = ndb.StringProperty()
    password = ndb.IntegerProperty()

class Login(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('login.html')
        customMessage = self.request.get('customMessage')
        self.response.write(template.render(customMessage=customMessage))

class Validate(webapp2.RequestHandler):
    def get(self):
        name = self.request.get('name')
        password = self.request.get('password')

        query = user.query()
        result = query.fetch()

        for entity in result:
            if entity.name == name and entity.password == int(password):
                query_params = {'username' : name}
                self.redirect('/main?' + urllib.urlencode(query_params))

        template = JINJA_ENVIRONMENT.get_template('login.html')
        self.response.write(template.render(customMessage='Error: Invalid Username or Password'))

class MainPage(webapp2.RequestHandler):
    def get(self):

        name = self.request.get('username')

        query_params= {'username' : name}
        template = JINJA_ENVIRONMENT.get_template('main.html')
        self.response.write(template.render(currentUser=name, currentUserEncode=urllib.urlencode(query_params)))

class LandingName(webapp2.RequestHandler):
    def get(self):

        currentUser = self.request.get('username')
        query_params = {'username' : currentUser}
        customMessage = self.request.get('customMessage')
        
        template = JINJA_ENVIRONMENT.get_template('name.html')
        self.response.write(template.render(customMessage=customMessage, currentUserEncode=urllib.urlencode(query_params), currentUser=currentUser))

    def post(self):

        currentUser = self.request.get('username')
        query_params = {'username' : currentUser}
        customMessage = self.request.get('customMessage')
        
        template = JINJA_ENVIRONMENT.get_template('name.html')
        self.response.write(template.render(customMessage=customMessage, currentUserEncode=urllib.urlencode(query_params), currentUser=currentUser))

class UpdateName(webapp2.RequestHandler):
    def post(self):
        
        name = self.request.get('username')
        newName = self.request.get('newName')

        # Saving original username
        query_params = {'username' : name}

        # If empty, send back to LandingName with original username and custom message

        if not newName:
            custom_message = {'customMessage' : 'Error: Name Cannot Be Blank'}
            self.redirect('/landingname?' + urllib.urlencode(query_params) + '&' + urllib.urlencode(custom_message))
        else:
            query = user.query()
            result = query.fetch()

            for entity in result:
                if entity.name == name:
                    entity.name = newName
                    entity.put()

            username_param = {'username' : newName}
            self.redirect('/main?' + urllib.urlencode(username_param))


class LandingPassword(webapp2.RequestHandler):
    
    def get(self):
        currentUser = self.request.get('username')
        user_encode = {'username' : currentUser}
        customMessage = self.request.get('customMessage')
        
        template = JINJA_ENVIRONMENT.get_template('password.html')
        self.response.write(template.render(customMessage=customMessage, currentUserEncode=urllib.urlencode(user_encode), currentUser=currentUser))
    
    def post(self):

        currentUser = self.request.get('username')
        user_encode = {'username' : currentUser}
        customMessage = self.request.get('customMessage')
        
        template = JINJA_ENVIRONMENT.get_template('password.html')
        self.response.write(template.render(customMessage=customMessage, currentUserEncode=urllib.urlencode(user_encode), currentUser=currentUser))

class UpdatePassword(webapp2.RequestHandler):
    def post(self):

        name = self.request.get('username')
        newPassword = self.request.get('newPassword')
        oldPassword = self.request.get('oldPassword')

        # Saving original username
        user_encode = {'username' : name}

        # If username's old password doesnt match stored password, then back to passwordlanding with error
        # Else, update username's password

        query = user.query()
        result = query.fetch()
        check = False

        logging.error('name is ' + str(name))
        logging.error('newPassword is ' + str(newPassword))
        logging.error('oldPassword is ' + str(oldPassword))

        for entity in result:
            if entity.name == name and entity.password == int(oldPassword):
                entity.password = int(newPassword)
                entity.put()
                check = True 
        
        if check:
            custom_message = {'customMessage' : 'Password Change Successful'}
            self.redirect('/?' + urllib.urlencode(custom_message))
        else:
            custom_message = {'customMessage' : 'Error: Old Password is Incorrect'}
            self.redirect('/landingpassword?' + urllib.urlencode(user_encode) + '&' + urllib.urlencode(custom_message))
        
# [START app]
app = webapp2.WSGIApplication([
    ('/', Login),
    ('/validate', Validate),
    ('/main', MainPage),
    ('/name', LandingName),
    ('/landingpassword', LandingPassword),
    ('/updatepassword', UpdatePassword),
    ('/updatename', UpdateName),
    ('/landingname', LandingName),
], debug=True)
# [END app]