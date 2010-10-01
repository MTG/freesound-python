# Largely based on canoris-python by Vincent Akkermans 

import httplib2, urllib2, urllib
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import simplejson as json
from urllib2 import HTTPError
import re
from contextlib import contextmanager
import os

# Register the streaming http handlers with urllib2
register_openers()

BASE_URI                = 'http://tabasco.upf.edu/api' #TODO:this should be freesound.org

URI_SOUNDS              = '/sounds'
URI_SOUNDS_SEARCH       = '/sounds/search'
URI_SOUND               = '/sounds/<sound_id>'
URI_USERS               = '/people'
URI_USER                = '/people/<username>'
URI_USER_SOUNDS         = '/people/<username>/sounds'
URI_USER_PACKS          = '/people/<username>/packs'
URI_PACKS               = '/packs'
URI_PACK                = '/packs/<pack_id>'
URI_PACK_SOUNDS         = '/packs/<pack_id>/sounds'


def _uri(uri, *args):
    for a in args:
        uri = re.sub('<[\w_]+>', urllib.quote(str(a)), uri, 1)
    return BASE_URI+uri


class Freesound():

    __api_key = False

    @classmethod
    def set_api_key(cls, key):
        cls.__api_key = key

    @classmethod
    def get_api_key(cls):
        if not cls.__api_key:
            raise Exception("Please set the API key! --> Freesound.set_api_key(<your_key>)")
        return cls.__api_key

class RequestWithMethod(urllib2.Request):
    '''
    Workaround for using DELETE with urllib2.

    N.B. Taken from http://www.abhinandh.com/posts/making-a-http-delete-request-with-urllib2/
    '''
    def __init__(self, url, method, data=None, headers={},\
                 origin_req_host=None, unverifiable=False):
        self._method = method
        urllib2.Request.__init__(self, url, data, headers,\
                                 origin_req_host, unverifiable)

    def get_method(self):
        if self._method:
            return self._method
        else:
            return urllib2.Request.get_method(self)


class FreesoundObject(object):

    def __init__(self, attrs):
        # If we only set the ref field we will set _loaded to false.
        # This way we can 'lazily' load the resource later on.
        self._loaded = False \
                       if len(attrs.keys())==1 and 'ref' in attrs \
                       else True
        self.attributes = attrs
    
    def __getitem__(self, name):
        # if the property isn't present, it might be because we haven't
        # loaded all the data yet.
        if not name in self.attributes:
            self.__load()
        # try to get the property
        return self.attributes[name]

    def __setitem__(self, name, val):
        raise NotImplementedError

    def __delitem__(self, name, val):
        raise NotImplementedError

    def keys(self):
        return self.attributes.keys()

    def __load(self):
        self.attributes = json.loads(_FSReq.simple_get(self['ref']))

    def get(self, name, default):
        return self.attributes.get(name, default)

    def update(self):
        self.__load()
        return self.attributes


class _FSReq(object):

    @classmethod
    def simple_get(cls, uri, params=False):
        return cls._simple_req(uri, 'GET', params)

    @classmethod
    def simple_del(cls, uri, params=False):
        return cls._simple_req(uri, 'DELETE', params)

    @classmethod
    def simple_post(cls, uri, params=False):
        return cls._simple_req(uri, 'POST', False, params)

    @classmethod
    def _simple_req(cls, uri, method, params, data=False):
        p = params if params else {}
        p['api_key'] = Freesound.get_api_key()
        u = '%s?%s' % (uri, urllib.urlencode(p))
        d = urllib.urlencode(data) if data else None
        req = RequestWithMethod(u, method, d)
        try:
            try:
                f = urllib2.urlopen(req)
            except HTTPError, e:
                if e.code >= 200 and e.code < 300:
                    resp = e.read()
                    return resp
                else:
                    raise e
            resp = f.read()
            f.close()
            return resp
        except HTTPError, e:
            print '--- request failed ---'
            print 'code:\t%s' % e.code
            print 'resp:\n%s' % e.read()
            raise e
   
    @classmethod
    def retrieve(cls, url, path):
        urllib.urlretrieve('%s?api_key=%s' % (url, Freesound.get_api_key()), path)

class Sound(FreesoundObject):

    @staticmethod
    def get_sound(sound_id):
        return Sound.get_sound_from_ref(_uri(URI_SOUND, sound_id))

    @staticmethod
    def get_sound_from_ref(ref):
        return Sound(json.loads(_FSReq.simple_get(ref)))

    @staticmethod
    def search(**params):#q query str, p page num, f filter, s sort
        return json.loads(_FSReq.simple_get(_uri(URI_SOUNDS_SEARCH),params))

    def retrieve(self, directory, name=False):
       path = os.path.join(directory, name if name else self['original_filename']) 
       return _FSReq.retrieve(self['serve'], path)
    
    def retrieve_preview(self, directory, name=False):
       path = os.path.join(directory, name if name else str(self['base_filename_slug']+".mp3")) 
       return _FSReq.retrieve(self['preview'], path)
	
    def __repr__(self):
        return '<Sound: id="%s", name="%s">' % \
                (self['id'], self.get('original_filename','n.a.'))


class User(FreesoundObject):

    @staticmethod
    def get_user(username):
        return User(json.loads(_FSReq.simple_get(_uri(URI_USER,username))))

    def sounds(self):
        return json.loads(_FSReq.simple_get(self['sounds']))
    
    def packs(self):
        return json.loads(_FSReq.simple_get(self['packs']))

    def __repr__(self):
        return '<User: "%s">' % \
                ( self.get('username','n.a.'))

class Pack(FreesoundObject):

    @staticmethod
    def get_pack(pack_id):
        return Pack(json.loads(_FSReq.simple_get(_uri(URI_PACK,pack_id))))

    def sounds(self):
        return json.loads(_FSReq.simple_get(self['sounds']))

    def __repr__(self):
        return '<Pack:  name="%s">' % \
                ( self.get('name','n.a.'))
