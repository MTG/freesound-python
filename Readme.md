freesound.py
============

A Python client for the [Freesound](https://freesound.org) APIv2.
This client should both in Python 2 and 3.

Find the API documentation at http://www.freesound.org/docs/api/. 
Apply for an API key at https://www.freesound.org/apiv2/apply/. 

The client automatically maps function arguments to http parameters of the API. 
JSON results are converted to python objects, but are also available in their original form (JSON loaded into dictionaries) using the method `.as_dict()` of returned objets (see [examples file](https://github.com/MTG/freesound-python/blob/master/examples.py)). 
The main object types (`Sound`, `User`, `Pack`) are augmented with the corresponding API calls.

Note that POST resources are not supported. Downloading full quality sounds requires Oauth2 authentication (see https://freesound.org/docs/api/authentication.html). Oauth2 authentication is supported by passing an access token, but you are expected to implement the workflow to obtain that access token. Here is an [example implementation of the Freesound OAuth2 workflow using Flask](https://gist.github.com/ffont/3607ba4af9814f3877cd42894a564222).

Example usage:

```python
import freesound

client = freesound.FreesoundClient()
client.set_token("<your_api_key>","token")

results = client.text_search(query="dubstep",fields="id,name,previews")

for sound in results:
    sound.retrieve_preview(".",sound.name+".mp3")
    print(sound.name)

```

Installation
============
1) clone or download

2) run:
```
python setup.py install
```

Alternatively you should also be able to install directly from Github with:
```
pip install git+https://github.com/MTG/freesound-python
```
