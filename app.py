import os
import urllib
import logging

from google.appengine.ext import ndb
from google.appengine.api import users

import webapp2
import jinja2

PROJECT_ID = 'sepm-diary-shop'

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class user(ndb.Model):
    username = ndb.StringProperty()
    password = ndb.StringProperty()
    admin = ndb.BooleanProperty()

class Login(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('login.html')
        customMessage = self.request.get('customMessage')
        self.response.write(template.render(customMessage=customMessage))

class AdminLogin(webapp2.RequestHandler):
    def post(self):
        template = JINJA_ENVIRONMENT.get_template('admin-login.html')
        customMessage = self.request.get('customMessage')
        self.response.write(template.render(customMessage=customMessage))

class Validate(webapp2.RequestHandler):
    def post(self):
        name = self.request.get('name').lower()
        password = self.request.get('password')
        response = False
        query_params = {'username' : name}

        query = user.query()
        result = query.fetch()

        for entity in result:
            if entity.username == name and entity.password == password:
                template = JINJA_ENVIRONMENT.get_template('main.html')
                self.response.write(template.render(currentUser=name, currentUserEncode=urllib.urlencode(query_params)))
                response = True

        if response == False:
            template = JINJA_ENVIRONMENT.get_template('login.html')
            self.response.write(template.render(customMessage='Error: Invalid Username or Password'))

class ValidateAdmin(webapp2.RequestHandler):
    def post(self):
        name = self.request.get('name').lower()
        password = self.request.get('password')
        response = False
        query_params = {'username' : name}

        query = user.query()
        result = query.fetch()

        for entity in result:
            if entity.username == name and entity.password == password and entity.admin == True:                
                template = JINJA_ENVIRONMENT.get_template('admin-console.html')
                self.response.write(template.render(currentUser=name, currentUserEncode=urllib.urlencode(query_params)))
                response = True

        if response == False:
            template = JINJA_ENVIRONMENT.get_template('admin-login.html')
            self.response.write(template.render(customMessage='Error: Invalid Username or Password'))

class MainPage(webapp2.RequestHandler):
    def post(self):
        name = self.request.get('username')
        query_params= {'username' : name}
        template = JINJA_ENVIRONMENT.get_template('main.html')
        self.response.write(template.render(currentUser=name, currentUserEncode=urllib.urlencode(query_params)))

class AdminConsole(webapp2.RequestHandler):
    def post(self):
        name = self.request.get('username')
        query_params= {'username' : name}
        template = JINJA_ENVIRONMENT.get_template('admin-console.html')
        self.response.write(template.render(currentUser=name, currentUserEncode=urllib.urlencode(query_params)))

class LandingName(webapp2.RequestHandler):
    def post(self):
        admincheck = self.request.get('admincheck')
        currentUser = self.request.get('username')
        query_params = {'username' : currentUser}
        customMessage = self.request.get('customMessage')
        template = JINJA_ENVIRONMENT.get_template('name.html')
        self.response.write(template.render(customMessage=customMessage, currentUserEncode=urllib.urlencode(query_params), currentUser=currentUser, admincheck=admincheck))

class UpdateName(webapp2.RequestHandler):
    def post(self):
        admincheck = self.request.get('admincheck')
        currentUser = self.request.get('username')
        newName = self.request.get('newName').lower()
        currentUserEncode = {'username' : currentUser}
        error = False

        query = user.query()
        result = query.fetch()

        # Check if new name is unique 
        for entity in result:
            if entity.username == newName:
                error = True

        # If new name is blank or taken, send back to LandingName with original username and custom message
        if not newName or error == True:
            template = JINJA_ENVIRONMENT.get_template('name.html')
            self.response.write(template.render(currentUser=currentUser, customMessage='Error: Name Cannot Be Blank', currentUserEncode=urllib.urlencode(currentUserEncode), admincheck=admincheck))

        else:
            for entity in result:
                if entity.username == currentUser:
                    entity.username = newName
                    newName = entity.username
                    entity.put()
            currentUserEncode = {'username' : newName}
            # Check whether to send back to main or admin console.
            if admincheck == 0:
                template = JINJA_ENVIRONMENT.get_template('main.html')
                self.response.write(template.render(currentUser=newName, currentUserEncode=urllib.urlencode(currentUserEncode), admincheck=admincheck))
            else:
                template = JINJA_ENVIRONMENT.get_template('admin-console.html')
                self.response.write(template.render(currentUser=newName, currentUserEncode=urllib.urlencode(currentUserEncode), customMessage="Name changed successfully."))

class LandingPassword(webapp2.RequestHandler):
    def post(self):
        admincheck = self.request.get('admincheck')
        currentUser = self.request.get('username')
        user_encode = {'username' : currentUser}
        customMessage = self.request.get('customMessage')
        
        template = JINJA_ENVIRONMENT.get_template('password.html')
        self.response.write(template.render(customMessage=customMessage, currentUserEncode=urllib.urlencode(user_encode), currentUser=currentUser, admincheck=admincheck))

class UpdatePassword(webapp2.RequestHandler):
    def post(self):
        admincheck = self.request.get('admincheck')
        name = self.request.get('username')
        newPassword = self.request.get('newPassword')
        oldPassword = self.request.get('oldPassword')
        query = user.query()
        result = query.fetch()
        currentUserEncode = {'username' : name}
        check = False

        # If username's old password doesnt match stored password, then back to passwordlanding with error
        # Else, update username's password
        for entity in result:
            if entity.username == name and entity.password == oldPassword:
                entity.password = newPassword
                entity.put()
                check = True 
        
        if check:
            # Check whether to send back to main or admin console. 
            if admincheck == 0:
                template = JINJA_ENVIRONMENT.get_template('login.html')
                self.response.write(template.render(customMessage='Password Change Successful'))
            else:
                template = JINJA_ENVIRONMENT.get_template('admin-console.html')
                self.response.write(template.render(currentUser=name, currentUserEncode=urllib.urlencode(currentUserEncode), customMessage="Password changed successfully."))
        else:
            template = JINJA_ENVIRONMENT.get_template('password.html')
            self.response.write(template.render(currentUser=name, customMessage='Error: Old Password is Incorrect', currentUserEncode=urllib.urlencode(currentUserEncode), admincheck=admincheck))

class LandingNewUser(webapp2.RequestHandler):
    def post(self):
        currentUser = self.request.get('username')
        
        if currentUser == '':
            currentUser = 'Not logged in.'

        user_encode = {'username' : currentUser}

        adminCheck = self.request.get('admincheck')
        template = JINJA_ENVIRONMENT.get_template('new-user.html')
        self.response.write(template.render(createadmin=adminCheck, currentUser=currentUser, currentUserEncode=urllib.urlencode(user_encode)))

class NewUser(webapp2.RequestHandler):
    def post(self):
        name = self.request.get('name').lower()
        password = self.request.get('password')
        adminCheck = self.request.get('admincheck')
        currentUser = self.request.get('username')
        user_encode = {'username' : currentUser}
        error = False

        query = user.query()
        result = query.fetch()

        # Invalid username or password check
        if not name or not password:
            template = JINJA_ENVIRONMENT.get_template('new-user.html')
            self.response.write(template.render(customMessage='Error: Username or Password cannot be blank.', createadmin=adminCheck, currentUser=currentUser, currentUserEncode=urllib.urlencode(user_encode)))
            error = True

        # If username is already taken
        for entity in result:
            if entity.username == name:
                template = JINJA_ENVIRONMENT.get_template('new-user.html')
                self.response.write(template.render(customMessage='Error: Username Already Taken.', createadmin=adminCheck, currentUser=currentUser, currentUserEncode=urllib.urlencode(user_encode)))
                error = True
        
        # Add new user - customer
        if (error == False and adminCheck == '0'):
            newUser = user(username=name, password=password, admin=False)
            newUser.put()
            template = JINJA_ENVIRONMENT.get_template('login.html')
            self.response.write(template.render(customMessage='New user created successfully.'))

        # Add new user - admin
        elif (error == False and adminCheck == '1'):
            newUser = user(username=name, password=password, admin=True)
            newUser.put()
            template = JINJA_ENVIRONMENT.get_template('admin-console.html')
            self.response.write(template.render(customMessage='New admin created successfully.', currentUser=currentUser, currentUserEncode=urllib.urlencode(user_encode)))

class LandingDeactivateUser(webapp2.RequestHandler):
    def post(self):
        currentUser = self.request.get('username')
        user_encode = {'username' : currentUser}
        template = JINJA_ENVIRONMENT.get_template('deactivateuser.html')
        self.response.write(template.render(currentUser=currentUser, currentUserEncode=urllib.urlencode(user_encode)))

class DeactivateUser(webapp2.RequestHandler):
    def post(self):
        currentUser = self.request.get('username')
        user_encode = {'username' : currentUser}
        name = self.request.get('name')
        query = user.query()
        result = query.fetch()
        response = False

        # If trying to delete yourself, cancel.
        if currentUser == name:
            template = JINJA_ENVIRONMENT.get_template('deactivateuser.html')
            self.response.write(template.render(customMessage='Error: you can\'t delete yourself.', currentUser=currentUser, currentUserEncode=urllib.urlencode(user_encode)))
            response = True

        # If user exists, deactivate
        for entity in result:
            if entity.username == name and response == False:
                entity.key.delete()
                template = JINJA_ENVIRONMENT.get_template('admin-console.html')
                self.response.write(template.render(customMessage='User deleted.', currentUser=currentUser, currentUserEncode=urllib.urlencode(user_encode)))
                response = True

        if response == False:
            template = JINJA_ENVIRONMENT.get_template('admin-console.html')
            self.response.write(template.render('Error: user not found.', currentUser=currentUser, currentUserEncode=urllib.urlencode(user_encode)))

# [START app]
app = webapp2.WSGIApplication([
    ('/', Login),
    ('/adminlogin', AdminLogin),
    ('/validateadmin', ValidateAdmin),
    ('/validate', Validate),
    ('/main', MainPage),
    ('/adminconsole', AdminConsole),
    ('/name', LandingName),
    ('/landingnewuser', LandingNewUser),
    ('/newuser', NewUser),
    ('/landingpassword', LandingPassword),
    ('/updatepassword', UpdatePassword),
    ('/updatename', UpdateName),
    ('/landingname', LandingName),
    ('/landingdeactivateuser', LandingDeactivateUser),
    ('/deactivateuser', DeactivateUser),
], debug=True)
# [END app]