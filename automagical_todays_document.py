#!/usr/bin/env python
# -*- coding: utf-8 -*-

import settings, tweepy, requests, json, datetime, random, time, argparse, os
from datetime import date

# This is where the script logs into the Twitter API using your application's settings.

auth = tweepy.OAuthHandler(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
auth.set_access_token(settings.ACCESS_KEY, settings.ACCESS_SECRET)
api = tweepy.API(auth)

# Here we read the optional arguments given.

parser = argparse.ArgumentParser()
parser.add_argument('--keyword', dest='keyword', metavar='KEYWORD',
                    action='store')
parser.add_argument('--upperyear', dest='upperyear', metavar='UPPERYEAR',
                    action='store')
parser.add_argument('--loweryear', dest='loweryear', metavar='LOWERYEAR',
                    action='store')
parser.add_argument('--rate', dest='rate', metavar='RATE',
                    action='store')
args = parser.parse_args()

# If a keyword is not given, the variable "q" is set to null, but if it is present, we use the argument to generate the keyword parameter for the OPA API call later on.

q = ""                   
if args.keyword :
	q = "&q=" + args.keyword

# If a date range is not given, the variables "loweryear" and "upperyear" are set to 0 and 9999, respectively, but either or both arguments are present, we use them to set the boundaries of the search later on.

loweryear = 0
upperyear = 9999
if args.upperyear :
	upperyear = int(args.upperyear)
if args.loweryear :
	loweryear = int(args.loweryear)

# If a rate is not given, the variable variable defaults to "600" (in seconds) for 10 minutes, but if it is present, we multiply by 60 to convert minutes to seconds.

rate = 600
if args.rate :
	rate = int(args.rate) * 60

# This part takes today's date and uses it to generate the OPA API query based on the month and day. This first API query is just to find out the number of results in the result set, and the rest is not used. We are searching for items with the record type of "Photographs and other Graphic Materials (NAID 10035674), produced on the current day and month. Then we parse the JSON and extract the total number of results for the query. We print the total results and API call in the command line for the user's information.

d = date.today()

rowsurl = 'https://uat.research.archives.gov/api/v1/?resultTypes=item&rows=1&description.item.generalRecordsTypeArray.generalRecordsType.naId=10035674&description.item.productionDateArray.proposableQualifiableDate.month=' + str(d.month) + '&description.item.productionDateArray.proposableQualifiableDate.day=' + str(d.day) + q
rowsparse = json.loads(requests.get(rowsurl).text)
rows = rowsparse['opaResponse']['results']['total'] - 1

print "----\nThere were *" + str(rows) + "* records found for this run using the following search query:\n\n" + rowsurl + "\n----"

# The hackish way to make this script continue infinitely.

x = 0
while x == 0 :

# This is where we actually construct the API query that we will use to extract the NAID and title for our tweet. This is the exact same query as above, using today's date, except that we are using the API's "offset" parameter to specify a particular record. We are using the total number of results which we determined above (the variable "rows") so that each time the script defines "geturl", it does it by picking a random result inside the bounds of the result set total, which will change each day. This is why we subtracted 1 from the results set total to define rows, since the API numbers starting from 0, and it will thrown an error if offset=rows.

	geturl = 'https://uat.research.archives.gov/api/v1/?resultTypes=item&rows=1&description.item.generalRecordsTypeArray.generalRecordsType.naId=10035674&description.item.productionDateArray.proposableQualifiableDate.month=' + str(d.month) + '&description.item.productionDateArray.proposableQualifiableDate.day=' + str(d.day) + '&offset=' + str(random.randint(0,rows)) + q

# Get the API query and parse the JSON.

	tweet = requests.get(geturl)
	parsed = json.loads(tweet.text)
	
# Setting title, NAID, year, image url, and name for readability later on.
	
	title = parsed['opaResponse']['results']['result'][0]['description']['item']['title']
	NAID = parsed['opaResponse']['results']['result'][0]['naId']
	year = parsed['opaResponse']['results']['result'][0]['description']['item']['productionDateArray']['proposableQualifiableDate']['year']
	imageurl = parsed['opaResponse']['results']['result'][0]['objects']['object']['file']['@url']
	filename = str(parsed['opaResponse']['results']['result'][0]['objects']['object']['file']['@name'])

# Because OPA's API does not have range searching enabled for this field, we are limiting the year manually, by using this if statement to make the script re-run the search with a new random integer until it finds a result within the range.

	if loweryear < int(year) < upperyear :

# This prints the image URL and tweet text just so we can watch the bot in the command line as it works. It will print before actually posting the tweet, so that if there is an error, we can see what the last tweet it tried was.
		
		print "\n\nImage found to tweet:   " + imageurl
		print "Text of tweet:   'On today's date (" + str(d.month) + "/" + str(d.day) + ") in " + year + ":\n\"" +  title [0:42] + "...\" #OTD #TDiH\nuat.research.archives.gov/id/" + NAID + "'" if len(title) > 45 else "Text of tweet:          'On today's date (" + str(d.month) + "/" + str(d.day) + ") in " + year + ":\n                       \"" +  title + "\" #OTD #TDiH\n                       uat.research.archives.gov/id/" + NAID + "'"

# This will download the file using the URL from the query.

		r = requests.get(imageurl, stream=True)
		with open(filename, "wb") as image :
			image.write(r.content)

# Here's the actual posting of the tweet, using tweepy. If the title is already 60 characters or less, it does not truncate. Otherwise, the title field is automatically truncated at 57 characters (the extra three characters for the "..."), so that the tweets are all 140 characters exactly, or less.

		api.update_with_media(filename, "On today's date (" + str(d.month) + "/" + str(d.day) + ") in " + year + ":\n\"" +  title [0:42] + "...\" #OTD #TDiH\nuat.research.archives.gov/id/" + NAID if len(title) > 45 else "On today's date (" + str(d.month) + "/" + str(d.day) + ") in " + year + ":\n\"" +  title + "\" #OTD #TDiH\nuat.research.archives.gov/id/" + NAID)
		
# Wait until after successful update to print "posted" in command line, and then delete the file it downloaded.
		print "...posted!"
		os.remove(filename)
		
# This tells the script to run the bit inside the while loop again, randomly generating a new tweet every 10 minutes. 

		time.sleep(rate)

# When the script encounters a result outside of a date range specified, it prints the NAID and year and immediately restarts without sleeping. This is how it retries continuously until it finds a record within the range.

	else :
		print "                       Found NAID " + NAID + " from " + year + ". Repeating..."
