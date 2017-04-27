####How to obtain oauth permissions for freesound so you can download high quality tracks

 1. Get API access from [here](https://www.freesound.org/apiv2/apply/) 
 
 2.  Then get an authorisation code by creating a GET request to https://www.freesound.org/apiv2/oauth2/authorize/ with the paramaters: 

		client_id = The code you just got in the last step
		response_type = 'code' [Literally just set it equal to the word 'code']
						 
	*You can use something like POSTMAN on chrome to do this*
 3. Now finally you create a POST request to https://www.freesound.org/apiv2/oauth2/access_token/ with the paramaters

        client_id=Same as in step 2
        client_secret = Listed under the table where you apply for api
        grant_type = 'authorization_code' [the word]
        code = The thing we got in step 2 at the end
This should return the final oauth token that you can plug into the program like so

  

         __author__ = 'Someone'
	    import freesound
	    c = freesound.FreesoundClient()
	    c.set_token("TOKEN FROM STEP 3","oauth")
       
    
	    print "User bookmark categories:"
	    print "-----------"
	    u = c.get_user("USERNAME")
	    print "User name: " + u.username
    
	    results_pager = u.get_bookmark_category_sounds(54289)
	    print "Num results: " + str(results_pager.count)
	    for k in range(4):
	        for i in range(0, len(results_pager.results)):
	            sound = results_pager[i]
	            print "\t- " + sound.name
	            sound.retrieve("tmp2/")
        results_pager = results_pager.next_page()

 This doesn't seem to totally work for me, if the sound name does not have the extension it just saves sounds as [FILE] instead of wav or something. 

	I'm also not sure how to add a fullproof method to loop through the pager until it's complete. It just loops 4 times here. 

	Hope this was useful, it took me longer than expected to get up and running with all these different tokens, wish there was a summary like this :P

*All of this is from :*
> https://www.freesound.org/docs/api/overview.html
