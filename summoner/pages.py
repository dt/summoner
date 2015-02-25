import base64
import json
import os
import re
import urllib

from google.appengine.api import mail, urlfetch, users
import jinja2
import webapp2

from bamboo import Bamboo

bamboo = Bamboo(os.environ.get('BAMBOO_DOMAIN'), os.environ.get('BAMBOO_KEY'))

class Index(webapp2.RequestHandler):
  def get(self):
    directory = bamboo.directory()
    template = JINJA_ENVIRONMENT.get_template('index.html')
    data = {'directory': sorted(directory.values(), key=lambda x: x.name)}
    self.response.write(template.render(data))

  def post(self):
    directory = bamboo.directory()

    guser = users.User().email()
    user = directory.get(guser)
    if user is None:
      self.response.write('User not found for ' + guser)
      raise Exception("user not found: " + guser)

    recipients = [directory[i] for i in self.request.get('recipients').split(',')]
    msg = self.request.get('msg')

    if not msg:
      self.response.set_status(400)
      self.response.write('Must provide a message')
      return

    body = user.name + ' via summon: ' + msg
    sent = False

    if self.request.get('sms', 'false').lower() != 'false':
      phones = dict((who.name, who.phone) for who in recipients)

      if None in phones.values():
        missing = [name for name, phone in phones.items() if phone is None]
        self.response.set_status(400)
        self.response.write('No phone numbers found for ' + ','.join(missing))
        return

      for phone in phones.values():
        params = urllib.urlencode({"From": os.environ['TWILIO_NUMBER'], "To": phone, "Body": body})
        headers = {'AUTHORIZATION': 'Basic %s=' % os.environ['TWILIO_AUTH']}
        url = os.environ['TWILIO_URL']

        resp = urlfetch.fetch(url, headers=headers, method=urlfetch.POST, payload=params)
        if resp.status_code > 400:
          raise Exception('SMS failed to send.  Maybe too long?  Error: ' + resp.content)
      sent = True

    if self.request.get('email', 'false').lower() != 'false':
      subject = msg[:50]
      if len(msg) > 50:
        subject += '...'
      from_addr = os.environ.get('FROM_ADDRESS')
      to = [recipient.email for recipient in recipients]
      mail.send_mail(from_addr, to, subject, body)
      sent = True

    if self.request.get('slack', 'false').lower() != 'false':
      try:
        for who in recipients:
          sender = user.username + ' (via summon)'
          params = json.dumps({'channel': '@' + who.username, 'username': sender, 'text': msg})
          urlfetch.fetch(os.environ.get('SLACK_URL'), method=urlfetch.POST, payload=params)
      except:
        pass
      sent = True

    if not sent:
      self.response.set_status(400)
      self.response.write('Must choose at least one contact method.')
      return



JINJA_ENVIRONMENT = jinja2.Environment(
  loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')),
  extensions=['jinja2.ext.autoescape'],
  autoescape=True
)

application = webapp2.WSGIApplication([('/', Index)], debug=True)
