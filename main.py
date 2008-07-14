import cgi
import wsgiref.handlers
import os
import sys
import logging
import re
import string

from google.appengine.api import datastore
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import search
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

class Post(search.SearchableModel):
  author = db.UserProperty()
  content = db.TextProperty()
  date = db.DateTimeProperty(auto_now_add=True)

class Page(webapp.RequestHandler):
    def updateTemplateValues(self):
        self.templateValues = {
            'user': self.user,
            'logout': users.create_logout_url(self.request.uri),
            'title': 'WebApp for %s' % self.user, 
            }

    def get(self):
        # this is the standard appengine way of getting a
        # logged-in user object
        self.user = users.get_current_user()

        if not self.user:
            self.redirect(users.create_login_url(self.request.uri))
            
        self.updateTemplateValues()

        # Get a template file from disk
        path = os.path.join(os.path.dirname(__file__), self.getTemplateName())

        # process the template and write it out to the response
        self.response.out.write(template.render(path, self.templateValues))

    def getPost(self):
        postId = self.request.get('post')
        if postId:
            return Post.get_by_id(int(postId))

class Index(Page):
    def getTemplateName(self):
        return 'index.html'

    def updateTemplateValues(self):
        Page.updateTemplateValues(self)
        # to get a parmeter from the request, do this
        filter = self.request.get('filter')

        # get any data for this page
        if filter != '':
            query = Post().all()
            query.search(filter)
        else:
            query = db.Query(Post)
            query.order('-date')

        posts = query.fetch(10)
        self.templateValues['filter'] = filter
        self.templateValues['posts'] = posts

class HandleCreate(Page):
    def post(self):
        postData = Post()
        if users.get_current_user():
            postData.author = users.get_current_user()
        postData.content = self.request.get('content')
        postData.save()
        self.redirect('/')

class HandleDelete(Page):
   def post(self):
       thePost = self.getPost()
       if thePost:
           thePost.delete()
       self.redirect('/')

class HandleUpdate(Page):
    def post(self):
        thePost = self.getPost()
        thePost.content = self.request.get('content')
        thePost.save()
        self.redirect('/')

    def updateTemplateValues(self):
        Page.updateTemplateValues(self)
        self.templateValues['post'] = self.getPost()

    def getTemplateName(self):
       return 'update.html'

def main():
  application = webapp.WSGIApplication(
                                       [('/', Index),
                                        ('/create', HandleCreate),
                                        ('/update', HandleUpdate),
                                        ('/delete', HandleDelete),
                                        ],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()
