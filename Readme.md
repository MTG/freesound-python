freesound.py
============

A Python client for the [Freesound](https://freesound.org) APIv2.

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

## Installation
1) clone or download

2) run:
```
python setup.py install
```

Alternatively you should also be able to install directly from GitHub with:
```
pip install git+https://github.com/MTG/freesound-python
```

## Advanced usage

### Modifying the requests' session:

You can easily extend/modify the way how requests are done by interacting directly with
the session object of the client.

For example, adding proxies:
```python
proxies = {
  'http': 'http://10.10.1.10:3128',
  'https': 'http://10.10.1.10:1080',
}
client.session.proxies.update(proxies)
```

or adding [rate limiting](https://github.com/JWCook/requests-ratelimiter):
```python
from requests_ratelimiter import LimiterSession

# Apply a rate-limit (59 requests per minute) to all requests
client.session = LimiterSession(per_minute=59)
```

### Authenticating with OAuth
Here is an example authentication flow with the help of [Requests-OAuthlib](https://requests-oauthlib.readthedocs.io/).
```python
from requests_oauthlib import OAuth2Session

import freesound

client_id = "<your_client_id>"
client_secret = "<your_client_secret>"

# do the OAuth dance
oauth = OAuth2Session(client_id)

authorization_url, state = oauth.authorization_url(
    "https://freesound.org/apiv2/oauth2/authorize/"
)
print(f"Please go to {authorization_url} and authorize access.")

authorization_code = input("Please enter the authorization code:")
oauth_token = oauth.fetch_token(
    "https://freesound.org/apiv2/oauth2/access_token/",
    authorization_code,
    client_secret=client_secret,
)

client = freesound.FreesoundClient()
client.set_token(oauth_token["access_token"], "oauth")
```
