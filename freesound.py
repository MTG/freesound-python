"""
A python client for the Freesound API.

Find the API documentation at https://www.freesound.org/docs/api/.

Apply for an API key at https://www.freesound.org/api/apply/.

The client automatically maps function arguments to http parameters of the API.
JSON results are converted to python objects. The main object types (Sound,
User, Pack) are augmented with the corresponding API calls.

Note that POST resources are not supported. Downloading full quality sounds
requires Oauth2 authentication
(see https://freesound.org/docs/api/authentication.html). Oauth2 authentication
is supported, but you are expected to implement the workflow.
"""
import re
from pathlib import Path
from urllib.parse import quote

from requests import Session, Request, JSONDecodeError, HTTPError

CONTENT_CHUNK_SIZE = 10 * 1024


class URIS:
    HOST = 'freesound.org'
    BASE = 'https://' + HOST + '/apiv2'
    SEARCH = '/search/'
    SOUND = '/sounds/<sound_id>/'
    SOUND_ANALYSIS = '/sounds/<sound_id>/analysis/'
    SIMILAR_SOUNDS = '/sounds/<sound_id>/similar/'
    COMMENTS = '/sounds/<sound_id>/comments/'
    DOWNLOAD = '/sounds/<sound_id>/download/'
    UPLOAD = '/sounds/upload/'
    DESCRIBE = '/sounds/<sound_id>/describe/'
    PENDING = '/sounds/pending_uploads/'
    BOOKMARK = '/sounds/<sound_id>/bookmark/'
    RATE = '/sounds/<sound_id>/rate/'
    COMMENT = '/sounds/<sound_id>/comment/'
    AUTHORIZE = '/oauth2/authorize/'
    LOGOUT = '/api-auth/logout/'
    LOGOUT_AUTHORIZE = '/oauth2/logout_and_authorize/'
    ME = '/me/'
    ME_BOOKMARK_CATEGORIES = '/me/bookmark_categories/'
    ME_BOOKMARK_CATEGORY_SOUNDS = '/me/bookmark_categories/<category_id>/sounds/'
    USER = '/users/<username>/'
    USER_SOUNDS = '/users/<username>/sounds/'
    USER_PACKS = '/users/<username>/packs/'
    PACK = '/packs/<pack_id>/'
    PACK_SOUNDS = '/packs/<pack_id>/sounds/'
    PACK_DOWNLOAD = '/packs/<pack_id>/download/'

    @classmethod
    def uri(cls, uri, *args):
        for a in args:
            uri = re.sub(r'<[\w_]+>', quote(str(a)), uri, 1)
        return cls.BASE + uri


class FreesoundTokenAuth:
    """Attaches HTTP Token Authentication header to the given Request object."""

    def __init__(self, token, auth_type="token"):
        if auth_type == "oauth":
            self.header = "Bearer " + token
        else:
            self.header = "Token " + token

    def __call__(self, r):
        r.headers['Authorization'] = self.header
        return r


class FreesoundClient:
    """
    Start here, create a FreesoundClient and set an authentication token using
    set_token
    >>> c = FreesoundClient()
    >>> c.set_token("<your_api_key>")
    """

    def __init__(self):
        self.auth = None    # should be set later
        self.session = Session()

    def get_sound(self, sound_id, **params):
        """
        Get a sound object by id
        Relevant params: fields
        https://freesound.org/docs/api/resources_apiv2.html#sound-resources

        >>> sound = c.get_sound(6)
        """
        uri = URIS.uri(URIS.SOUND, sound_id)
        return FSRequest.request(uri, params, self, Sound)

    def search(self, **params):
        """
        Search sounds using a text query and/or filter. Returns an iterable
        Pager object. The fields parameter allows you to specify the
        information you want in the results list
        https://freesound.org/docs/api/resources_apiv2.html#text-search

        >>> sounds = c.search(
        >>>     query="dubstep", filter="tag:loop", fields="id,name,url"
        >>> )
        >>> for snd in sounds: print snd.name
        """
        if 'fields' not in params:
            # If no fields parameter is specified, add fields parameter
            # with default Freesound fields for a query plus the previews
            # URIs. This will simplify the process of retrieving previews
            # as it will ensure that the preview URIs are already loaded in
            # the Sound objects resulting from a search query.
            params['fields'] = 'id,name,tags,username,license,previews'

        if 'similar_to' in params:
            # If similar_to parameter is specified and it is specified as
            # a vector, then change it to a list and limit float precssion
            # to avoid too long URL
            if isinstance(params['similar_to'], (list, tuple)):
                vector = params['similar_to']
                vector_str = ','.join(['{0:.5f}'.format(v) for v in vector])
                params['similar_to'] = '[' + vector_str + ']'
            
        uri = URIS.uri(URIS.SEARCH)
        return FSRequest.request(uri, params, self, Pager)

    def get_user(self, username):
        """
        Get a user object by username
        https://freesound.org/docs/api/resources_apiv2.html#user-instance

        >>> u = c.get_user("xserra")
        """
        uri = URIS.uri(URIS.USER, username)
        return FSRequest.request(uri, {}, self, User)

    def get_pack(self, pack_id):
        """
        Get a user object by username
        https://freesound.org/docs/api/resources_apiv2.html#pack-instance

        >>> p = c.get_pack(3416)
        """
        uri = URIS.uri(URIS.PACK, pack_id)
        return FSRequest.request(uri, {}, self, Pack)

    def get_my_bookmark_categories(self, **params):
        """
        Get bookmark categories for the authenticated user.
        Relevant params: page, page_size
        https://freesound.org/docs/api/resources_apiv2.html#my-bookmark-categories
        Requires OAuth2 authentication.

        >>> c.get_my_bookmark_categories()
        """
        uri = URIS.uri(URIS.ME_BOOKMARK_CATEGORIES)
        return FSRequest.request(uri, params, self, GenericPager)

    def get_my_bookmark_category_sounds(self, category_id, **params):
        """
        Get sounds in a bookmark category for the authenticated user.
        Relevant params: page, page_size, fields
        https://freesound.org/docs/api/resources_apiv2.html#my-bookmark-category-sounds
        Requires OAuth2 authentication.

        >>> c.get_my_bookmark_category_sounds(0)
        """
        uri = URIS.uri(URIS.ME_BOOKMARK_CATEGORY_SOUNDS, category_id)
        return FSRequest.request(uri, params, self, Pager)

    def set_token(self, token, auth_type="token"):
        """
        Set your API key or Oauth2 token
        https://freesound.org/docs/api/authentication.html

        >>> c.set_token("<your_api_key>")
        """
        self.auth = FreesoundTokenAuth(token, auth_type)


class FreesoundObject:
    """
    Base object, automatically populated from parsed json dictionary
    """

    def __init__(self, json_dict, client):
        self.client = client
        self.json_dict = json_dict

        def replace_dashes(d):
            for k, v in list(d.items()):
                if "-" in k:
                    d[k.replace("-", "_")] = d[k]
                    del d[k]
                if isinstance(v, dict):
                    replace_dashes(v)

        replace_dashes(json_dict)
        self.__dict__.update(json_dict)
        for k, v in json_dict.items():
            if isinstance(v, dict):
                self.__dict__[k] = FreesoundObject(v, client)

    def as_dict(self):
        return self.json_dict


class FreesoundException(Exception):
    """
    Freesound API exception
    """

    def __init__(self, http_code, detail):
        self.code = http_code
        self.detail = detail

    def __str__(self):
        return '<FreesoundException: code=%s, detail="%s">' % \
               (self.code, self.detail)


class FSRequest:
    """
    Makes requests to the freesound API. Should not be used directly.
    """

    @staticmethod
    def request(
        uri,
        params,
        client,
        wrapper=FreesoundObject,
        method='GET',
    ):
        req = Request(method, uri, params=params, auth=client.auth)
        prepared = client.session.prepare_request(req)
        resp = client.session.send(prepared)
        try:
            resp.raise_for_status()
        except HTTPError as e:
            raise FreesoundException(resp.status_code, resp.reason) from e
        try:
            result = resp.json()
        except JSONDecodeError as e:
            raise FreesoundException(0, "Couldn't parse response") from e
        if wrapper:
            return wrapper(result, client)
        return result

    @staticmethod
    def retrieve(url, client, path, reporthook=None):
        """
        :param reporthook: a callback which is called when a block of data
        has been downloaded. The callback should have a signature such as
        def updateProgress(self, count, blockSize, totalSize)
        For further reference, check the urllib docs.
        """
        resp = client.session.get(url, auth=client.auth)
        try:
            resp.raise_for_status()
        except HTTPError as e:
            raise FreesoundException(resp.status_code, resp.reason) from e
        content_length = resp.headers.get("Content-Length", -1)
        if reporthook is not None:
            reporthook(0, CONTENT_CHUNK_SIZE, content_length)
        with open(path, "wb") as fh:
            for i, chunk in enumerate(resp.iter_content(CONTENT_CHUNK_SIZE), start=1):
                if reporthook is not None:
                    reporthook(i, CONTENT_CHUNK_SIZE, content_length)
                fh.write(chunk)


class Pager(FreesoundObject):
    """
    Paginates search results. Can be used in for loops to iterate its results
    array.
    """

    def __getitem__(self, key):
        return Sound(self.results[key], self.client)

    def next_page(self):
        """
        Get a Pager with the next results page.
        """
        return FSRequest.request(self.next, {}, self.client, Pager)

    def previous_page(self):
        """
        Get a Pager with the previous results page.
        """
        return FSRequest.request(self.previous, {}, self.client, Pager)


class GenericPager(Pager):
    """
    Paginates results for objects different from Sound.
    """

    def __getitem__(self, key):
        return FreesoundObject(self.results[key], self.client)


class Sound(FreesoundObject):
    """
    Freesound Sound resources

    >>> sound = c.get_sound(6)
    """

    def retrieve(self, directory, name=None, reporthook=None):
        """
        Download the original sound file (requires Oauth2 authentication).
        https://freesound.org/docs/api/resources_apiv2.html#download-sound-oauth2-required

         >>> sound.retrieve("/tmp")

        :param reporthook: a callback which is called when a block of data
        has been downloaded. The callback should have a signature such as
        def updateProgress(self, count, blockSize, totalSize)
        For further reference, check the urllib docs.
        """
        filename = (name if name else self.name).replace('/', '_')
        path = Path(directory, filename)
        uri = URIS.uri(URIS.DOWNLOAD, self.id)
        return FSRequest.retrieve(uri, self.client, path, reporthook)

    def retrieve_preview(self, directory, name=None, quality='lq', file_format='mp3'):
        """
        Download the sound preview.
        If no quality or file format is specified, preview_lq_mp3 is returned. 

        Parameters:
            directory (str): The directory where the sound preview will be downloaded. 
            name (str, optional): The name of the downloaded sound preview file. If no file 
                                extension is specified or if it mismatches the chosen one in
                                file_format, then the file_format is added as a file extension. 
            quality (str, optional): The quality of the audio preview. Available values: 
                                    'lq' (low quality) or 'hq' (high quality).
            file_format (str, optional): The desired file format of the audio preview. 
                                        Available values: 'mp3','ogg' (only!).

        >>> sound.retrieve_preview("/tmp")
        """
        preview_type = 'preview_' + quality + '_' + file_format
        preview_attr = getattr(self.previews, preview_type)
        try:
            if name:
                if name.split('.')[-1] != file_format:
                    file_name = name + '.' + file_format
                else:
                    file_name = name
            else:
                file_name = preview_attr.split("/")[-1]
            path = Path(directory, file_name)
        except AttributeError as exc:
            raise FreesoundException(
                '-',
                'Preview uris are not present in your sound object. Please add'
                ' them using the fields parameter in your request. See '
                ' https://www.freesound.org/docs/api/resources_apiv2.html#response-sound-list.'    # noqa
            ) from exc
        return FSRequest.retrieve(preview_attr, self.client, path)

    def get_analysis(self, fields=None):
        """
        Get content-based descriptors.
        https://freesound.org/docs/api/resources_apiv2.html#sound-analysis

        Example:
        >>> analysis_object = sound.get_analysis()
        >>> mffc_mean = analysis_object.mfcc # <-- access analysis results by using object properties
        >>> mffc_mean = analysis_object.as_dict()['mfcc'] # <-- Is possible to convert it to a Dictionary
        """
        uri = URIS.uri(URIS.SOUND_ANALYSIS, self.id)
        return FSRequest.request(uri, {}, self.client, FreesoundObject)

    def get_analysis_frames(self):
        """
        Get analysis frames.
        Returns a list of all computed descriptors for all frames as a FreesoundObject.
        https://freesound.org/docs/api/analysis_docs.html#analysis-docs

        Example:
        >>> analysis_frames_object = sound.get_analysis_frames()
        >>> pitch_by_frames = analysis_frames_object.lowlevel.pich # <-- access analysis results by using object properties
        >>> pitch_by_frames = analysis_frames_object.as_dict()['lowlevel']['pich'] # <-- Is possible to convert it to a Dictionary
        """
        uri = self.analysis_frames
        return FSRequest.request(uri, params=None, client=self.client, wrapper=FreesoundObject)

    def get_similar(self, **params):
        """
        Get similar sounds based on similarity spaces.
        Relevant params: page, page_size, fields, similarity_space
        https://freesound.org/docs/api/resources_apiv2.html#similar-sounds

        >>> s = sound.get_similar()
        """
        uri = URIS.uri(URIS.SIMILAR_SOUNDS, self.id)
        return FSRequest.request(uri, params, self.client, Pager)

    def get_comments(self, **params):
        """
        Get user comments.
        Relevant params: page, page_size
        https://freesound.org/docs/api/resources_apiv2.html#sound-comments

        >>> comments = sound.get_comments()
        """
        uri = URIS.uri(URIS.COMMENTS, self.id)
        return FSRequest.request(uri, params, self.client, GenericPager)

    def __repr__(self):
        return f'<Sound: id="{self.id}", name="{self.name}">'


class User(FreesoundObject):
    """
    Freesound User resources.

    >>> u = c.get_user("xserra")
    """

    def get_sounds(self, **params):
        """
        Get user sounds.
        Relevant params: page, page_size, fields
        https://freesound.org/docs/api/resources_apiv2.html#user-sounds

        >>> u.get_sounds()
        """
        uri = URIS.uri(URIS.USER_SOUNDS, self.username)
        return FSRequest.request(uri, params, self.client, Pager)

    def get_packs(self, **params):
        """
        Get user packs.
        Relevant params: page, page_size
        https://freesound.org/docs/api/resources_apiv2.html#user-packs

        >>> u.get_packs()
        """
        uri = URIS.uri(URIS.USER_PACKS, self.username)
        return FSRequest.request(uri, params, self.client, GenericPager)

    def __repr__(self):
        return '<User: "%s">' % self.username


class Pack(FreesoundObject):
    """
    Freesound Pack resources.

    >>> p = c.get_pack(3416)
    """

    def get_sounds(self, **params):
        """
        Get pack sounds
        Relevant params: page, page_size, fields
        https://freesound.org/docs/api/resources_apiv2.html#pack-sounds

        >>> sounds = p.get_sounds()
        """
        uri = URIS.uri(URIS.PACK_SOUNDS, self.id)
        return FSRequest.request(uri, params, self.client, Pager)

    def __repr__(self):
        return '<Pack:  name="%s">' % self.name
