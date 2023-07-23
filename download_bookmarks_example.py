# Downloads all bookmarks in a user's categories on freesound,
# Requires OAUTH key, follow instructions at -
# https://freesound.org/docs/api/authentication.html#oauth2-authentication
# Make sure you use the actual oauth token and not the authorisation token in
# step 2
import os
import sys

import freesound

access_token = os.getenv("FREESOUND_ACCESS_TOKEN", None)
if access_token is None:
    print("You need to set your ACCESS TOKEN as an environment variable")
    print("named FREESOUND_ACCESS_TOKEN")
    sys.exit(-1)

freesound_client = freesound.FreesoundClient()
freesound_client.set_token(access_token, "oauth")

path_name = os.path.join(os.getcwd(), "tmp")
try:
    os.mkdir(path_name)
except:
    pass

user = freesound_client.get_user("apitest")
print("Username:", user.username)

bookmarks_results_pager = user.get_bookmark_categories(page_size=100)
print("Num categories:", bookmarks_results_pager.count)

for bookmark in bookmarks_results_pager:
    print("\tCategory:", bookmark.name)
    print("\tNum sounds:", bookmark.num_sounds)

    sounds_results_pager = user.get_bookmark_category_sounds(
        bookmark.id, fields="id,name,type", page_size=1
    )

    while True:
        for sound in sounds_results_pager:
            print("\t\tDownloading:", sound.name)

            # Some sound filenames already end with the type...
            if sound.name.endswith(sound.type):
                filename = sound.name
            else:
                filename = f"{sound.name}.{sound.type}"

            sound.retrieve(path_name, name=filename)

        if not sounds_results_pager.next:
            break

        sounds_results_pager = sounds_results_pager.next_page()
