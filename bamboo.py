from __future__ import with_statement

import urllib2
import base64
import json
from hashlib import md5
from collections import namedtuple
from google.appengine.api import memcache

class BambooException(Exception):
  pass

Person = namedtuple('Person', ['id', 'name', 'active', 'username', 'email', 'team', 'title', 'photo', 'executive', 'phone'])

class Bamboo(object):
  """super thin wrapper around urllib2 to make get and post requests to bamboo"""

  def __init__(self, subdomain, api_key):
    self._subdomain = subdomain
    self._api_key = api_key
    self._base_url = 'https://api.bamboohr.com/api/gateway.php/{0}/v1/'.format(self._subdomain)
    self.headers = {
      "Authorization": "Basic %s" % base64.b64encode(self._api_key + ':'),
      'Accept': 'application/json',
    }

  def call(self, path, data=None):
    url = self._base_url + path
    req = urllib2.Request(url, data, headers=self.headers)
    response = urllib2.urlopen(req)
    if response.getcode() > 400:
      raise BambooException(response)
    return response

  def _photo(self, email):
    photo = md5(email).hexdigest() if email else None
    return 'https://{s}.bamboohr.com/employees/photos/?h={i}'.format(s=self._subdomain, i=photo)

  def _person(self, directory_entry):
    def is_exec(title):
      for i in ['Chief', 'CEO', 'VP']:
        if i in (title or ''):
          return True
      return False

    return Person(
      id=directory_entry['id'],
      name=directory_entry['displayName'],
      active=directory_entry['status'] == 'Active',
      username=directory_entry['workEmail'].split('@')[0],
      email=directory_entry['workEmail'],
      team=directory_entry['department'],
      title=directory_entry['jobTitle'],
      photo=self._photo(directory_entry['workEmail']),
      executive=is_exec(directory_entry['jobTitle']),
      phone=directory_entry.get('mobilePhone') or directory_entry.get('homePhone') or directory_entry.get('workPhone'),
    )

  def fetch_directory_json(self):
    req_xml = '<report><title>Directory</title><fields>'
    for i in ['id', 'displayName', 'workEmail', 'department', 'status', 'jobTitle', 'homePhone', 'mobilePhone', 'workPhone']:
      req_xml += '<field id="{0}" />'.format(i)
    req_xml += '</fields></report>'
    return self.call('reports/custom?format=JSON', req_xml).read()

  def directory(self):
    """Use a custom report to get all employees"""

    cache_key = 'direcotry-2'
    raw = memcache.get(cache_key)
    if raw is None:
      raw = self.fetch_directory_json()
      if not memcache.add(cache_key, raw, 60 * 5):
        print 'Memcache set failed.'

    parsed = json.loads(raw)['employees']
    return dict((i['workEmail'], self._person(i)) for i in parsed if i['workEmail'])
