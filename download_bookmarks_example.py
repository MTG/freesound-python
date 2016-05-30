# Downloads all bookmarks in a user's categories on freesound, 
# Requires OAUTH key, follow instructions on -
# https://freesound.org/docs/api/authentication.html#oauth2-authentication
# Make sure you use the actual oauth token and not the authorisation token in step 2
import freesound
import os

freesound_client = freesound.FreesoundClient()
# Settings required:
# Set oauth token here, note 'token' changes to 'oauth' compared to other examples
freesound_client.set_token("<YOUR_API_KEY_HERE>", "oauth")
# Set the username you want to download all bookmarks from
user = freesound_client.get_user("frederic.font")
path_name = os.path.join(os.getcwd(), "tmp")
try:
    # Create Path for downloads in workingdir/tmp
    os.mkdir(path_name)
except:
    # Incase Path already exists
    print("Path Already exists")
print "User Bookmark Download:"
print "-----------"
print "User name: ", user.username
# Get all bookmark categories
results_pager = user.get_bookmark_categories(page_size=10)
# Create an array to store the bookmark_id
bookmarks = [0]
for bookmark in results_pager.results[1:]:
    # Split Bookmark url into an array and take just the id which is then passed to the bookmark_id array
    # Note starting at 1 to len because The first result is always the default bookmark directory (0)
    # which I include in the array by default.
    bookmark_category = bookmark['url'].split('/')[7]
    bookmarks.append(bookmark_category)
print len(bookmarks), "Bookmark Categories \n"
# Loop for count of bookmark categories
for index, bookmark_category in enumerate(bookmarks):
    print "Category", index + 1, " Downloading..."
    # Create a generic results_pager and get all the sounds from the first category
    results_pager = user.get_bookmark_category_sounds(bookmark_category)
    # Get the number of sounds per category
    number_sounds = results_pager.count
    print "Num Sounds:", number_sounds
    # Try/Except the next page of the result pager. If there is no exception there is another page
    # Else if it runs out of pages break the loop
    try:
        while True:
            # Loop for the amount of sounder per this category
            for sound_index, sound in enumerate(results_pager):
                print sound_index + 1, "Downloading -", sound.name
                # Retrieve Sound to tmp directory
                sound_type = freesound_client.get_sound(sound.id, fields="type").type
                # Set file type
                # https://github.com/MTG/freesound-python/issues/9
                sound.retrieve(path_name, name="%s.%s" % (sound.name, sound_type))
            results_pager = results_pager.next_page()
    except AttributeError:
        # Attribute error is returned if pager runs out, so break at attribute error, no pages left.
        print"Downloaded", number_sounds, "Sounds to /tmp \n"
        # All Sounds downloaded
