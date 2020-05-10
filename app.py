import os
import urllib
import logging

from google.appengine.ext import ndb
from google.appengine.api import users
from datetime import datetime

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

class diary(ndb.Model):
    coverText = ndb.StringProperty()
    coverTheme = ndb.StringProperty()
    deliveryOption = ndb.StringProperty()
    paperColour = ndb.StringProperty()
    paperType = ndb.StringProperty()
    paymentChoice = ndb.StringProperty()
    price = ndb.FloatProperty()
    purchaseDate = ndb.DateTimeProperty()
    user = ndb.StringProperty()

class paperColour(ndb.Model):
    paperColour = ndb.StringProperty()

class coverTheme(ndb.Model):
    coverTheme = ndb.StringProperty()

class paperType(ndb.Model):
    paperType = ndb.StringProperty()

class deliveryOption(ndb.Model):
    deliveryOption = ndb.StringProperty()

class paymentChoice(ndb.Model):
    paymentChoice = ndb.StringProperty()

class Home(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('home.html')
        self.response.write(template.render())

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
            if admincheck == '0':
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
            if admincheck == '0':
                template = JINJA_ENVIRONMENT.get_template('login.html')
                self.response.write(template.render(customMessage='Password Change Successful'))
            else:
                template = JINJA_ENVIRONMENT.get_template('admin-login.html')
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

        if (adminCheck == '0'):
            adminoruser = "Sign Up"
        else:
            adminoruser = "Create Admin"

        template = JINJA_ENVIRONMENT.get_template('new-user.html')
        self.response.write(template.render(createadmin=adminCheck, currentUser=currentUser, currentUserEncode=urllib.urlencode(user_encode), adminoruser=adminoruser))

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

        if (adminCheck == '0'):
            adminoruser = "Sign Up"
        else:
            adminoruser = "Create Admin"

        # Invalid username or password check
        if not name or not password:
            template = JINJA_ENVIRONMENT.get_template('new-user.html')
            self.response.write(template.render(customMessage='Error: Username or Password cannot be blank.', createadmin=adminCheck, currentUser=currentUser, currentUserEncode=urllib.urlencode(user_encode), adminoruser=adminoruser))
            error = True

        # If username is already taken
        for entity in result:
            if entity.username == name:
                template = JINJA_ENVIRONMENT.get_template('new-user.html')
                self.response.write(template.render(customMessage='Error: Username Already Taken.', createadmin=adminCheck, currentUser=currentUser, currentUserEncode=urllib.urlencode(user_encode), adminoruser=adminoruser))
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
                self.response.write(template.render(customMessage='User deactivated.', currentUser=currentUser, currentUserEncode=urllib.urlencode(user_encode)))
                response = True

        if response == False:
            template = JINJA_ENVIRONMENT.get_template('admin-console.html')
            self.response.write(template.render('Error: user not found.', currentUser=currentUser, currentUserEncode=urllib.urlencode(user_encode)))

class CreateDiary(webapp2.RequestHandler):
    def post(self):
        currentUser = self.request.get('username')
        currentUserEncode = {'username' : currentUser}

        paperColours = []
        colourQuery = paperColour.query()
        coloursResult = colourQuery.fetch()

        for colour in coloursResult:
            paperColours.append(colour.paperColour)

        coverThemes = []
        themeQuery = coverTheme.query()
        themesResult = themeQuery.fetch()

        for theme in themesResult:
            coverThemes.append(theme.coverTheme)

        paperTypes = []
        paperTypeQuery = paperType.query()
        paperTypeResult = paperTypeQuery.fetch()

        for paper in paperTypeResult:
            paperTypes.append(paper.paperType)

        template = JINJA_ENVIRONMENT.get_template('create-diary.html')
        self.response.write(template.render(customMessage='', currentUser=currentUser, currentUserEncode=urllib.urlencode(currentUserEncode), paperColours=paperColours, coverThemes=coverThemes, paperTypes=paperTypes))

class PurchaseDiary(webapp2.RequestHandler):
    def post(self):
        # Get diary customisation parameters from url
        # Send these parameters to purchase-diary.html page
        currentUser = self.request.get('username')
        currentUserEncode = {'username' : currentUser}

        paperColour = self.request.get('paperColour')
        paperColourEncode = {'paperColour' : paperColour}

        coverTheme = self.request.get('coverTheme')
        coverThemeEncode = {'coverTheme' : coverTheme}
        
        paperType = self.request.get('paperType')
        paperTypeEncode = {'paperType' : paperType}
        
        coverText = self.request.get('coverText')
        coverTextEncode = {'coverText' : coverText}

        price = 29.99

        description = 'You have chosen a Diary with ' + paperColour + ' ' + paperType + ' paper, a ' + coverTheme + ' cover, and the custom text ' + coverText + '.'

        deliveryOptions = []
        deliveryQuery = deliveryOption.query()
        deliveryResult = deliveryQuery.fetch()

        for option in deliveryResult:
            deliveryOptions.append(option.deliveryOption)

        paymentChoices = []
        paymentQuery = paymentChoice.query()
        paymentResult = paymentQuery.fetch()

        for payment in paymentResult:
            paymentChoices.append(payment.paymentChoice)

        template = JINJA_ENVIRONMENT.get_template('purchase-diary.html')
        self.response.write(template.render(currentUser=currentUser, currentUserEncode=urllib.urlencode(currentUserEncode), paperColour=urllib.urlencode(paperColourEncode), coverTheme=urllib.urlencode(coverThemeEncode), paperType=urllib.urlencode(paperTypeEncode), coverText=urllib.urlencode(coverTextEncode), description=description, deliveryOptions=deliveryOptions, paymentChoices=paymentChoices, price=price))

class MakePurchase(webapp2.RequestHandler):
    def post(self):
        # get diary purchase and delivery parameters from url, along with customisation params
        # add diary entity to database
        # Send back to main with success message. 
        currentUser = self.request.get('username')
        currentUserEncode = {'username' : currentUser}

        paperColour = self.request.get('paperColour')
        coverTheme = self.request.get('coverTheme')
        paperType = self.request.get('paperType')
        coverText = self.request.get('coverText')
        paymentChoice = self.request.get('paymentChoice')
        deliveryOption = self.request.get('deliveryOption')

        price = 29.99
        purchaseDate = datetime.now()

        newDiary = diary(coverText=coverText, coverTheme=coverTheme, deliveryOption=deliveryOption, paperColour=paperColour, paperType=paperType, paymentChoice=paymentChoice, price=price, purchaseDate=purchaseDate, user=currentUser)
        newDiary.put()

        template = JINJA_ENVIRONMENT.get_template('main.html')
        self.response.write(template.render(currentUser=currentUser, currentUserEncode=urllib.urlencode(currentUserEncode), customMessage='Purchase Successful'))


# [START app]
app = webapp2.WSGIApplication([
    ('/', Home),
    ('/login', Login),
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
    ('/creatediary', CreateDiary),
    ('/purchasediary', PurchaseDiary),
    ('/makepurchase', MakePurchase),
], debug=True)