import os
import sys

import freesound

api_key = os.getenv("FREESOUND_API_KEY", None)
if api_key is None:
    print("You need to set your API key as an environment variable")
    print("named FREESOUND_API_KEY")
    sys.exit(-1)

freesound_client = freesound.FreesoundClient()
freesound_client.set_token(api_key)

# Get sound info example
print("Sound info:")
print("-----------")
sound = freesound_client.get_sound(96541)
print("Getting sound:", sound.name)
print("Url:", sound.url)
print("Description:", sound.description)
print("Tags:", " ".join(sound.tags))
print()

# Get sound info example specifying some request parameters
print("Sound info specifying some request parameters:")
print("-----------")
sound = freesound_client.get_sound(
    96541,
    fields="id,name,username,duration,analysis",
    descriptors="lowlevel.spectral_centroid",
    normalized=1,
)
print("Getting sound:", sound.name)
print("Username:", sound.username)
print("Duration:", str(sound.duration), "(s)")
print(
    "Spectral centroid:",
)
print(sound.analysis.lowlevel.spectral_centroid.as_dict())
print()

# Get sound analysis example
print("Get analysis:")
print("-------------")
analysis = sound.get_analysis()

mfcc = analysis.lowlevel.mfcc.mean
print("Mfccs:", mfcc)
# you can also get the original json (this applies to any FreesoundObject):
print(analysis.as_dict())
print()

# Get sound analysis example specifying some request parameters
print("Get analysis with specific normalized descriptor:")
print("-------------")
analysis = sound.get_analysis(
    descriptors="lowlevel.spectral_centroid.mean", normalized=1
)
spectral_centroid_mean = analysis.lowlevel.spectral_centroid.mean
print("Normalized mean of spectral centroid:", spectral_centroid_mean)
print()

# Get similar sounds example
print("Similar sounds: ")
print("---------------")
results_pager = sound.get_similar()
for similar_sound in results_pager:
    print("\t-", similar_sound.name, "by", similar_sound.username)
print()

# Get similar sounds example specifying some request parameters
print("Similar sounds specifying some request parameters:")
print("---------------")
results_pager = sound.get_similar(
    page_size=10,
    fields="name,username",
    descriptors_filter="lowlevel.pitch.mean:[110 TO 180]",
)
for similar_sound in results_pager:
    print("\t-", similar_sound.name, "by", similar_sound.username)
print()

# Search Example
print("Searching for 'violoncello':")
print("----------------------------")
results_pager = freesound_client.text_search(
    query="violoncello",
    filter="tag:tenuto duration:[1.0 TO 15.0]",
    sort="rating_desc",
    fields="id,name,previews,username",
)
print("Num results:", results_pager.count)
print("\t----- PAGE 1 -----")
for sound in results_pager:
    print("\t-", sound.name, "by", sound.username)
print("\t----- PAGE 2 -----")
results_pager = results_pager.next_page()
for sound in results_pager:
    print("\t-", sound.name, "by", sound.username)
print()

# Content based search example
print("Content based search:")
print("---------------------")
results_pager = freesound_client.content_based_search(
    descriptors_filter="lowlevel.pitch.var:[* TO 20]",
    target="lowlevel.pitch_salience.mean:1.0 lowlevel.pitch.mean:440",
)

print("Num results:", results_pager.count)
for sound in results_pager:
    print("\t-", sound.name, "by", sound.username)
print()

# Getting sounds from a user example
print("User sounds:")
print("-----------")
user = freesound_client.get_user("InspectorJ")
print("User name:", user.username)
results_pager = user.get_sounds()
print("Num results:", results_pager.count)
print("\t----- PAGE 1 -----")
for sound in results_pager:
    print("\t-", sound.name, "by", sound.username)
print("\t----- PAGE 2 -----")
results_pager = results_pager.next_page()
for sound in results_pager:
    print("\t-", sound.name, "by", sound.username)
print()


# Getting sounds from a user example specifying some request parameters
print("User sounds specifying some request parameters:")
print("-----------")
user = freesound_client.get_user("Headphaze")
print("User name:", user.username)
results_pager = user.get_sounds(
    page_size=10,
    fields="name,username,samplerate,duration,analysis",
    descriptors="rhythm.bpm",
)

print("Num results:", results_pager.count)
print("\t----- PAGE 1 -----")
for sound in results_pager:
    print(
        "\t-",
        sound.name,
        "by",
        sound.username,
    )
    print(
        ", with sample rate of",
        sound.samplerate,
        "Hz and duration of",
    )
    print(sound.duration, "s")
print("\t----- PAGE 2 -----")
results_pager = results_pager.next_page()
for sound in results_pager:
    print(
        "\t-",
        sound.name,
        "by",
        sound.username,
    )
    print(
        ", with sample rate of",
        sound.samplerate,
        "Hz and duration of",
    )
    print(sound.duration, "s")
print()

# Getting sounds from a pack example specifying some request parameters
print("Pack sounds specifying some request parameters:")
print("-----------")
pack = freesound_client.get_pack(3524)
print("Pack name:", pack.name)
results_pager = pack.get_sounds(
    page_size=5,
    fields="id,name,username,duration,analysis",
    descriptors="lowlevel.spectral_flatness_db",
)
print("Num results:", results_pager.count)
print("\t----- PAGE 1 -----")
for sound in results_pager:
    print(
        "\t-",
        sound.name,
        "by",
        sound.username,
        ", with duration of",
    )
    print(
        sound.duration,
        "s and a mean spectral flatness of",
    )
    print(sound.analysis.lowlevel.spectral_flatness_db.mean)
print("\t----- PAGE 2 -----")
results_pager = results_pager.next_page()
for sound in results_pager:
    print(
        "\t-",
        sound.name,
        "by",
        sound.username,
        ", with duration of",
    )
    print(
        sound.duration,
        "s and a mean spectral flatness of",
    )
    print(sound.analysis.lowlevel.spectral_flatness_db.mean)
print()

# Getting bookmark categories from a user example
print("User bookmark categories:")
print("-----------")
user = freesound_client.get_user("frederic.font")
print("User name:", user.username)
results_pager = user.get_bookmark_categories(page_size=10)
print("Num results:", results_pager.count)
print("\t----- PAGE 1 -----")
for bookmark_category in results_pager:
    print(
        "\t-",
        bookmark_category.name,
        "with",
        bookmark_category.num_sounds,
    )
    print("sounds at", bookmark_category.url)
print()
