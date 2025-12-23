import os
import sys

import freesound

api_key = os.getenv('FREESOUND_API_KEY', None)
if api_key is None:
    print("You need to set your API key as an environment variable")
    print("named FREESOUND_API_KEY")
    sys.exit(-1)

freesound_client = freesound.FreesoundClient()
freesound_client.set_token(api_key)

# Get sound info example
print("Sound info:")
print("-----------")
sound = freesound_client.get_sound(6)
print("Getting sound:", sound.name)
print("Url:", sound.url)
print("Description:", sound.description)
print("Tags:", " ".join(sound.tags))
print()

# Get sound info example specifying some request parameters
print("Sound info specifying some request parameters:")
print("-----------")
sound = freesound_client.get_sound(
    6, fields="id,name,username,duration,spectral_centroid")
print("Getting sound:", sound.name)
print("Username:", sound.username)
print("Duration:", str(sound.duration), "(s)")
print("Spectral centroid:",str(sound.spectral_centroid), "(Hz)")
print()

# Get sound analysis example
print("Get analysis:")
print("-------------")
analysis = sound.get_analysis()
mfcc = analysis.mfcc
print("Mfccs:", mfcc)
# you can also get the original json (this applies to any FreesoundObject):
print(analysis.as_dict())
print()

# Get similar sounds example
print("Similar sounds: ")
print("---------------")
results_pager = sound.get_similar()
for similar_sound in results_pager:
    print("\t-", similar_sound.name, "by", similar_sound.username)
print()

# Search Example
print("Searching for 'violoncello':")
print("----------------------------")
results_pager = freesound_client.search(
    query="violoncello",
    filter="tag:tenuto duration:[1.0 TO 15.0]",
    sort="rating_desc",
    fields="id,name,previews,username"
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

# Search all sounds that match some audio descriptor filter
print("Filter by audio descriptors:")
print("---------------------")
results_pager = freesound_client.search(
    filter="spectral_centroid:[1000 TO 2000] AND pitch:[200 TO 300]",
    fields="name,username,spectral_centroid,pitch",
)

print("Num results:", results_pager.count)
for sound in results_pager:
    print("\t-", sound.name, "by", sound.username, "with spectral centroid of", sound.spectral_centroid, "Hz and pitch of", sound.pitch, "Hz")
print()

# We can use the search endpoint for a similarity search which also filters results
print("Searching for similar sounds and filtering by a descriptor value:")
print("---------------")
results_pager = freesound_client.search(
    page_size=10, fields="name,username", similar_to=6, filter="pitch:[110 TO 180]"
)
for similar_sound in results_pager:
    print("\t-", similar_sound.name, "by", similar_sound.username)
print()

# Find sounds simialar to a target vector extracted from an existing sound which might not be in Freesound
# Note that "similarity_space" must match with the similarity space used to extract the target vector
print("Searching for sounds similar to a target vector:")
print("---------------")
target_vector = [0.84835537,-0.06019006,0.35139768,-0.01221892,-0.23172645,-0.03798686,-0.03869437,0.02199453,-0.10143687,-0.03342770,0.05464298,-0.02654354,0.05424048,0.04912830,0.01449411,-0.02995046,0.04584143,0.03731462,0.06914231,-0.00702387,-0.02202889,0.01644059,-0.00153376,0.11042101,0.05432773,0.05736105,-0.03779107,-0.00909068,-0.08996461,-0.04300615,0.05610843,0.02214170,-0.02155820,0.05158299,-0.00717155,-0.04345755,-0.00519616,0.02887811,-0.02205723,0.01658933,0.02485796,-0.06228176,0.03574570,-0.04556302,-0.00497004,0.00300936,-0.01974736,-0.01391953,-0.02898939,0.01041939,-0.02836645,0.00853050,-0.03129587,0.00454572,0.00898315,-0.01371797,-0.00918297,-0.01049032,0.02800968,-0.04248178,0.02648444,-0.01034762,0.02105908,-0.01137279,0.02845560,-0.04284714,0.00797986,0.00973879,-0.00850114,-0.01093731,-0.00629640,-0.01862817,0.00829806,0.01137537,0.02601988,0.03015542,-0.01091145,0.00547907,-0.00426657,0.01001693,0.00793383,0.00082211,-0.02848534,-0.00823537,0.01392606,-0.02012341,-0.00788319,0.02797560,-0.01470957,-0.01917517,-0.01177181,0.00952904,-0.00223396,-0.01586017,-0.00566903,0.01150901,-0.00361810,-0.00257769,-0.01509761,0.00552032]
results_pager = freesound_client.search(
    page_size=10, fields="name,username", similar_to=target_vector, similarity_space="freesound_classic"
)
for similar_sound in results_pager:
    print("\t-", similar_sound.name, "by", similar_sound.username)
print()

# Search sounds and sort them by distance to a given audio descriptors target
print("Sort sounds by distance to audio descriptors target:")
print("---------------")
results_pager = freesound_client.search(
    filter="pitch_var:[* TO 20]",
    sort='pitch_salience:1.0,pitch:440'
)

for sound in results_pager:
    print("\t-", sound.name, "by", sound.username, "distance:", sound.distance_to_target)
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
    page_size=10, fields="name,username,samplerate,duration" 
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
    page_size=5, fields="id,name,username,duration,spectral_flatness"
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
        "s and a spectral flatness of",
    )
    print(sound.spectral_flatness)
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
        "s and a spectral flatness of",
    )
    print(sound.spectral_flatness)
print()
