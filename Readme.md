freesound.py
============

A python client for the [Freesound](http://freesound.org) API.

Find the API documentation at http://www.freesound.org/docs/api/. Apply for an API key at http://www.freesound.org/api/apply/. 

The client automatically maps function arguments to http parameters of the API. JSON results are converted to python objects. The main object types (Sound, User, Pack) are augmented with the corresponding API calls.

Note that POST resources are not supported. Downloading full quality sounds requires Oauth2 authentication (see http://freesound.org/docs/api/authentication.html). Oauth2 authentication is supported, but you are expected to implement the workflow.

Example usage:

```
import freesound, sys,os

c = freesound.FreesoundClient()
c.set_token("<your_api_key","token")

results = c.text_search(query="dubstep",fields="id,name,previews")

for sound in results:
	sound.retrieve_preview(".",sound.name+".mp3")
	print(sound.name)

```
