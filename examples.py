import freesound
import os
c = freesound.FreesoundClient()
c.set_token("<YOUR_API_KEY_HERE>","token")

# Get sound info example
print "Sound info:"
print "-----------"
s = c.get_sound(96541)
print "Getting sound: " + s.name
print "Url: " + s.url
print "Description: " + s.description
print "Tags: " + str(s.tags)
print "\n"

# Get sound info example specifying some request parameters
print "Sound info specifying some request parameters:"
print "-----------"
s = c.get_sound(96541, fields = "id,name,username,duration,analysis", descriptors = "lowlevel.spectral_centroid", normalized = 1)
print "Getting sound: " + s.name
print "Username: " + s.username
print "Duration: " + str(s.duration) + " (s)"
print "Spectral centroid: " + str(s.analysis.lowlevel.spectral_centroid.as_dict())
print "\n"

# Get sound analysis example
print "Get analysis:"
print "-------------"
analysis = s.get_analysis()

mfcc = analysis.lowlevel.mfcc.mean
print "Mfccs: " + str(mfcc)
print analysis.as_dict()  # you can also get the original json (this apply to any FreesoundObject)
print "\n"

# Get sound analysis example specifying some request parameters
print "Get analysis with specific normalized descriptor:"
print "-------------"
analysis = s.get_analysis(descriptors = "lowlevel.spectral_centroid.mean", normalized = 1)
spectral_centroid_mean = analysis.lowlevel.spectral_centroid.mean
print "Normalized mean of spectral centroid: " + str(spectral_centroid_mean)
print "\n"

# Get similar sounds example
print "Similar sounds: "
print "---------------"
results_pager = s.get_similar()
for i in range(0, len(results_pager.results)):
    sound = results_pager[i]
    print "\t- " + sound.name + " by " + sound.username
print "\n"

# Get similar sounds example specifying some request parameters
print "Similar sounds specifying some request parameters: "
print "---------------"
results_pager = s.get_similar(page_size = 10, fields = "name,username", descriptors_filter = "lowlevel.pitch.mean:[110 TO 180]")
for i in range(0, len(results_pager.results)):
    sound = results_pager[i]
    print "\t- " + sound.name + " by " + sound.username
print "\n"

# Search Example
print "Searching for 'violoncello':"
print "----------------------------"
results_pager = c.text_search(query="violoncello",filter="tag:tenuto duration:[1.0 TO 15.0]",sort="rating_desc",fields="id,name,previews,username")
print "Num results: " + str(results_pager.count)
print "\t ----- PAGE 1 -----"
for i in range(0, len(results_pager.results)):
    sound = results_pager[i]
    print "\t- " + sound.name + " by " + sound.username
print "\t ----- PAGE 2 -----"
results_pager = results_pager.next_page()
for i in range(0, len(results_pager.results)):
    sound = results_pager[i]
    print "\t- " + sound.name + " by " + sound.username
print "\n"
results_pager[0].retrieve_preview('.')

# Content based search example
print "Content based search:"
print "---------------------"
results_pager = c.content_based_search(descriptors_filter="lowlevel.pitch.var:[* TO 20]",
    target='lowlevel.pitch_salience.mean:1.0 lowlevel.pitch.mean:440')

print "Num results: " + str(results_pager.count)
for i in range(0, len(results_pager.results)):
    sound = results_pager[i]
    print "\t- " + sound.name + " by " + sound.username
print "\n"

# Getting sounds from a user example
print "User sounds:"
print "-----------"
u = c.get_user("Jovica")
print "User name: " + u.username
results_pager = u.get_sounds()
print "Num results: " + str(results_pager.count)
print "\t ----- PAGE 1 -----"
for i in range(0, len(results_pager.results)):
    sound = results_pager[i]
    print "\t- " + sound.name + " by " + sound.username
print "\t ----- PAGE 2 -----"
results_pager = results_pager.next_page()
for i in range(0, len(results_pager.results)):
    sound = results_pager[i]
    print "\t- " + sound.name + " by " + sound.username
print "\n"

# Getting sounds from a user example specifying some request parameters
print "User sounds specifying some request parameters:"
print "-----------"
u = c.get_user("Jovica")
print "User name: " + u.username
results_pager = u.get_sounds(page_size = 10, fields = "name,username,samplerate,duration,analysis", descriptors = "rhythm.bpm")
print "Num results: " + str(results_pager.count)
print "\t ----- PAGE 1 -----"
for i in range(0, len(results_pager.results)):
    sound = results_pager[i]
    print "\t- " + sound.name + " by " + sound.username + ", with sample rate of " + str(sound.samplerate) + " Hz and duration of " + str(sound.duration) + " s"
print "\t ----- PAGE 2 -----"
results_pager = results_pager.next_page()
for i in range(0, len(results_pager.results)):
    sound = results_pager[i]
    print "\t- " + sound.name + " by " + sound.username + ", with sample rate of " + str(sound.samplerate) + " Hz and duration of " + str(sound.duration) + " s"
print "\n"

# Getting sounds from a pack example specifying some request parameters
print "Pack sounds specifying some request parameters:"
print "-----------"
p = c.get_pack(3524)
print "Pack name: " + p.name
results_pager = p.get_sounds(page_size = 5, fields = "id,name,username,duration,analysis", descriptors = "lowlevel.spectral_flatness_db")
print "Num results: " + str(results_pager.count)
print "\t ----- PAGE 1 -----"
for i in range(0, len(results_pager.results)):
    sound = results_pager[i]
    print "\t- " + sound.name + " by " + sound.username + ", with duration of " + str(sound.duration) + " s and a mean spectral flatness of " + str(sound.analysis.lowlevel.spectral_flatness_db.mean)
print "\t ----- PAGE 2 -----"
results_pager = results_pager.next_page()
for i in range(0, len(results_pager.results)):
    sound = results_pager[i]
    print "\t- " + sound.name + " by " + sound.username + ", with duration of " + str(sound.duration) + " s and a mean spectral flatness of " + str(sound.analysis.lowlevel.spectral_flatness_db.mean)
print "\n"

# Getting bookmark categories from a user example
print "User bookmark categories:"
print "-----------"
u = c.get_user("frederic.font")
print "User name: " + u.username
results_pager = u.get_bookmark_categories(page_size = 10)
print "Num results: " + str(results_pager.count)
print "\t ----- PAGE 1 -----"
for i in range(0, len(results_pager.results)):
    bookmark_cat = results_pager[i]
    print "\t- " + bookmark_cat.name + " with " + str(bookmark_cat.num_sounds)+ " sounds at " + bookmark_cat.url

print "\n"