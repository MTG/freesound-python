from freesound.__init__ import *
Freesound.set_api_key('YOUR_API_KEY_HERE')

# Get sound info example
print "Sound info:"
print "-----------"
s = Sound.get_sound(96541)
print "Getting sound: " + s['original_filename']
print "Url: " + s['url']
print "Description: " + s['description']
print "Tags: " + str(s['tags'])
print "\n"

# Get sound analysis example
print "Get analysis:"
print "-------------"
analysis = s.get_analysis()
mfcc = analysis['lowlevel']['mfcc']
print "Mfccs: " + str(mfcc)
print "\n"

# Get similar sounds example
print "Similar sounds: "
print "---------------"
similar_sounds = s.get_similar()
for sound in similar_sounds['sounds']:
    print "\t- " + sound['original_filename'] + " by " + sound['user']['username']
print "\n"

# Search Example
print "Searching for 'violoncello':"
print "----------------------------"
results = Sound.search(q="violoncello",filter="tag:tenuto duration:[1.0 TO 15.0]",sort="rating_desc")
print "Num results: " + str(results['num_results'])
print "\t ----- PAGE 1 -----"
for sound in results['sounds']:
    print "\t- " + sound['original_filename'] + " by " + sound['user']['username']
print "\n"


# Content based search example
print "Content based search:"
print "---------------------"
results = Sound.content_based_search(f=".lowlevel.pitch.var:[* TO 20]",
    t='.lowlevel.pitch_salience.mean:1.0 .lowlevel.pitch.mean:440',
    fields="preview-hq-ogg,duration,tags,url",
    max_results="15",
    sounds_per_page="10")

print "Num results: " + str(results['num_results'])
for sound in results['sounds']:
    print "\t- " + sound['url']
print "\n"


# Query for geotags example
print "Geoquery example:"
print "-----------------"
results = Sound.geotag(min_lon=2.005176544189453,
                       max_lon=2.334766387939453,
                       min_lat=41.3265528618605,
                       max_lat=41.4504467428547)
print "Num results: " + str(results['num_results'])
for sound in results['sounds']:
    print "\t- " + sound['url']
print "\n"



# Getting sounds from a user example
print "User sounds:"
print "-----------"
u = User.get_user("Jovica")
print "User name: " + u['username']
pager = u.sounds()
print "\t ----- PAGE 1 -----"
for s in pager['sounds']:
    print "\t- " + str(s['id'])
pager.next()
print "\t ----- PAGE 2 -----"
for s in pager['sounds']:
    print "\t- " + str(s['id'])
