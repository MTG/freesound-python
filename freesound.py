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
    TEXT_SEARCH = '/search/text/'
    CONTENT_SEARCH = '/search/content/'
    COMBINED_SEARCH = '/search/combined/'
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
    USER = '/users/<username>/'
    USER_SOUNDS = '/users/<username>/sounds/'
    USER_PACKS = '/users/<username>/packs/'
    USER_BOOKMARK_CATEGORIES = '/users/<username>/bookmark_categories/'
    USER_BOOKMARK_CATEGORY_SOUNDS = '/users/<username>/bookmark_categories/<category_id>/sounds/'  # noqa
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
        self.auth = None  # should be set later
        self.session = Session()

    def get_sound(self, sound_id, **params):
        """
        Get a sound object by id
        Relevant params: descriptors, fields, normalized
        https://freesound.org/docs/api/resources_apiv2.html#sound-resources

        >>> sound = c.get_sound(6)
        """
        uri = URIS.uri(URIS.SOUND, sound_id)
        return FSRequest.request(uri, params, self, Sound)

    def text_search(self, **params):
        """
        Search sounds using a text query and/or filter. Returns an iterable
        Pager object. The fields parameter allows you to specify the
        information you want in the results list
        https://freesound.org/docs/api/resources_apiv2.html#text-search

        >>> sounds = c.text_search(
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

        uri = URIS.uri(URIS.TEXT_SEARCH)
        return FSRequest.request(uri, params, self, Pager)

    def content_based_search(self, **params):
        """
        Search sounds using a content-based descriptor target and/or filter
        See essentia_example.py for an example using essentia
        https://freesound.org/docs/api/resources_apiv2.html#content-search

        >>> sounds = c.content_based_search(
        >>>     target="lowlevel.pitch.mean:220",
        >>>     descriptors_filter="lowlevel.pitch_instantaneous_confidence.mean:[0.8 TO 1]",  # noqa
        >>>     fields="id,name,url")
        >>> for snd in sounds: print snd.name
        """
        if 'fields' not in params:
            # See comment in text_search method above
            params['fields'] = 'id,name,tags,username,license,previews'

        uri = URIS.uri(URIS.CONTENT_SEARCH)
        return FSRequest.request(uri, params, self, Pager)

    def combined_search(self, **params):
        """
        Combine both text and content-based queries.
        https://freesound.org/docs/api/resources_apiv2.html#combined-search

        >>> sounds = c.combined_search(
        >>>     target="lowlevel.pitch.mean:220",
        >>>     filter="single-note"
        >>> )
        """
        if 'fields' not in params:
            # See comment in text_search method above
            params['fields'] = 'id,name,tags,username,license,previews'

        uri = URIS.uri(URIS.COMBINED_SEARCH)
        return FSRequest.request(uri, params, self, CombinedSearchPager)

    def get_user(self, username):
        """
        Get a user object by username
        https://freesound.org/docs/api/resources_apiv2.html#combined-search

        >>> u = c.get_user("xserra")
        """
        uri = URIS.uri(URIS.USER, username)
        return FSRequest.request(uri, {}, self, User)

    def get_pack(self, pack_id):
        """
        Get a user object by username
        https://freesound.org/docs/api/resources_apiv2.html#combined-search

        >>> p = c.get_pack(3416)
        """
        uri = URIS.uri(URIS.PACK, pack_id)
        return FSRequest.request(uri, {}, self, Pack)

    def set_token(self, token, auth_type="token"):
        """
        Set your API key or Oauth2 token
        https://freesound.org/docs/api/authentication.html
        https://freesound.org/docs/api/resources_apiv2.html#combined-search

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


class CombinedSearchPager(FreesoundObject):
    """
    Combined search uses a different pagination style.
    The total amount of results is not available, and the size of the page is
    not guaranteed.
    Use :py:meth:`~freesound.CombinedSearchPager.more` to get more results if
    available.
    """

    def __getitem__(self, key):
        return Sound(self.results[key], self.client)

    def more(self):
        """
        Get more results
        """
        return FSRequest.request(
            self.more, {}, self.client, CombinedSearchPager
        )


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

    def retrieve_preview(self, directory, name=None):
        """
        Download the low quality mp3 preview.

        >>> sound.retrieve_preview("/tmp")
        """
        try:
            path = Path(directory,
                        name if name else self.previews.preview_lq_mp3.split("/")[-1],
                        )
        except AttributeError as exc:
            raise FreesoundException(
                '-',
                'Preview uris are not present in your sound object. Please add'
                ' them using the fields parameter in your request. See '
                ' https://www.freesound.org/docs/api/resources_apiv2.html#response-sound-list.'  # noqa
            ) from exc
        return FSRequest.retrieve(
            self.previews.preview_lq_mp3,
            self.client,
            path
        )

    def get_analysis(self, descriptors=None, normalized=0):
        """
        Get content-based descriptors.
        Returns the statistical aggregation as a Sound object.
        https://freesound.org/docs/api/resources_apiv2.html#sound-analysis

        Example:
        >>> analysis_object = sound.get_analysis(descriptors="lowlevel.pitch.mean")
        >>> mffc_mean = analysis_object.lowlevel.mfcc.mean # <-- access analysis results by using object properties
        >>> mffc_mean = analysis_object.as_dict()['lowlevel']['mfcc']['mean'] # <-- Is possible to convert it to a Dictionary
        """
        uri = URIS.uri(URIS.SOUND_ANALYSIS, self.id)
        params = {}
        if descriptors:
            params['descriptors'] = descriptors
        if normalized:
            params['normalized'] = normalized
        return FSRequest.request(uri, params, self.client, FreesoundObject)

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
        Get similar sounds based on content-based descriptors.
        Relevant params: page, page_size, fields, descriptors, normalized,
        descriptors_filter
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
        Relevant params: page, page_size, fields, descriptors, normalized
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

    def get_bookmark_categories(self, **params):
        """
        Get user bookmark categories.
        Relevant params: page, page_size
        https://freesound.org/docs/api/resources_apiv2.html#user-bookmark-categories

        >>> u.get_bookmark_categories()
        """
        uri = URIS.uri(URIS.USER_BOOKMARK_CATEGORIES, self.username)
        return FSRequest.request(uri, params, self.client, GenericPager)

    def get_bookmark_category_sounds(self, category_id, **params):
        """
        Get user bookmarks.
        Relevant params: page, page_size, fields, descriptors, normalized
        https://freesound.org/docs/api/resources_apiv2.html#user-bookmark-category-sounds

        >>> p = u.get_bookmark_category_sounds(0)
        """
        uri = URIS.uri(
            URIS.USER_BOOKMARK_CATEGORY_SOUNDS, self.username, category_id
        )
        return FSRequest.request(uri, params, self.client, Pager)

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
        Relevant params: page, page_size, fields, descriptors, normalized
        https://freesound.org/docs/api/resources_apiv2.html#pack-sounds

        >>> sounds = p.get_sounds()
        """
        uri = URIS.uri(URIS.PACK_SOUNDS, self.id)
        return FSRequest.request(uri, params, self.client, Pager)

    def __repr__(self):
        return '<Pack:  name="%s">' % self.name
