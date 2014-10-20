# NARA-twitterbot
===============

This is a Twitter bot created to experiment with using NARA's test API (https://uat.research.archives.gov/api/v1/).

The script tweets out titles and links to NARA photographic item records from the current date in history, selected at random. It has optional arguments for a keyword and date ranges to restrict the set of results the bot selects from. The rate at which the bot tweets is also configurable.

The bot works by constructing a fielded search query to NARA's online catalog API using the parameters provided, and then extracting the necessary metadata fields to form the tweet. Titles are currently truncated if over 60 characters so that tweets are kept at 140 or less.

## Dependencies

This script relies on python with the `tweepy` (https://github.com/tweepy/tweepy) library, which can be installed with `easy_install` or `pip`. Note, `tweepy` only works with python 2.6 and 2.7.

The script also requires a Twitter account set up to post via the API. You'll have to create an application at https://apps.twitter.com/ to get the credential keys for the setup. There is a one-time authentication process for setting up the application for "Read and Write" permissions.

## Setup

`settings` is imported from a settings.py file which is saved in the same directory as the script, so that the script can be shared without revealing credentials for the Twitter account. The settings file looks like (with credentials filled in):

```python
CONSUMER_KEY = 'XXX'
CONSUMER_SECRET = 'XXX'
ACCESS_KEY = 'XXX'
ACCESS_SECRET = 'XXX'
```

## Instructions

To run the script, just use `python nara-twitterbot.py`. In the command line window, the script will display the number of results it is randomly selecting from for the search for that day's date and any other options used. It will then print the text of each tweet as it tweets it.

You can also use several optional arguments to change the bot's parameters.

### Arguments

There are 4 optional arguments: `rate`, `keyword`, `loweryear`, and `upperyear`.

- `rate`: This is an integer value which will set the rate of how often the bot tweets. The unit is minutes. For example, use `python nara-twitterbot.py --rate 2` to make the bot tweet every 2 minutes. If omitted, the bot will tweet every 10 minutes.
- `keyword`: This is a string which will limit the records the bot tweets to only ones matching with that keyword. For example, use the command `python nara-twitterbot.py --keyword navy` if you want the bot to only tweet about records with the keyword "navy" (for an anniversary, for example).
- `loweryear` and `upperyear`: These are integer values which can be used to specify the date range for the records you would like to tweet. If omitted, `loweryear` defaults to 0 (e.g. no lower limit) and `upperyear` defaults to 9999 (e.g. no upper limit). For example, `python nara-twitterbot.py --loweryear 1941 --upperyear 1945` will only tweet records from the years 1942, 1943, and 1944.
