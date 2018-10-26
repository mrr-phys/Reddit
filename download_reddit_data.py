"""
This module downloads comments from Reddit and saves them to our SQL database. 
We choose the subreddits we're interested in, and set the maximal number of 
comments to download. We then connect via PRAW package to Reddit's API,
start downloading the comments, and report progress along the way.
"""

import os
import pandas as pd
import praw
import sys
import time

sys.path.append('/Users/mohammad/Desktop/Reddit/contodb.py')
from contodb import con # Connect to SQL
cur = con.cursor()

# Choose the subreddits to download and max comments to download
chosen_subreddits = ['youtube', 'Best_Of_YouTube', 'youtube_recommended', 'funny', 'todayilearned',
'mildlyinteresting', 'announcements', 'aww', 'kiddet', 'justforkids', 'KidSafeVideos', 
'childrensbooks', 'reallifedoodles', 'BeAmazed', 'Parenting', 'DoesAnybodyElse']

comments_threshold = 20000

# Connect to Reddit's API
reddit = praw.Reddit(client_id = '',
                     client_secret = '',
                     password = '',
                     user_agent = 'trendfinding by /u/mrr-phys',
                     username = 'mrr-phys')

# Get the relevant data for each of the subreddits and store them in SQL
for i in range(len(chosen_subreddits)):
    subreddit = reddit.subreddit(chosen_subreddits[i])
    db_tuple = (subreddit.id, chosen_subreddits[i], subreddit.title, 
                int(subreddit.created), 0)
    sql_query = """
                INSERT INTO main_subreddits
                VALUES (%s, %s, %s, %s, %s)
                """
    cur.execute(sql_query, db_tuple)


# Put the subreddits to be downloaded in pull_df DataFrame 
# (useful for adding other subreddits later on)
all_df = pd.read_sql("SELECT * FROM main_subreddits", con)
pull_df = all_df
pull_df.index = range(pull_df.shape[0])

# Loop over the above subreddits, submissions and comments and save them to SQL
for i in range(pull_df.shape[0]):
    t_start = time.time()
    print ("Subreddit " + str(i + 1) + " / " + 
           str(pull_df.shape[0]) + ": " + pull_df['title'][i])
    # Get relevant subreddit info
    subreddit = reddit.subreddit(pull_df['name'][i])
    subreddit_id = pull_df['id'][i]
    comment_count = 0
    # Loop over all the submissions
    for submission in subreddit.submissions():
        submission.comments.replace_more(limit = 0); # For deep comments
        submission_tuple = (submission.id, subreddit_id, int(submission.created), submission.selftext)
        comment_tuples = []
        # Loop over all the comments in this submission
        comment_list = submission.comments.list()
        for comment in comment_list:
            comment_tuples.append((comment.id , subreddit_id, 
                                   submission.id, comment.body))
        if len(comment_tuples) > 0:
            comment_str = ','.join(cur.mogrify("(%s,%s,%s,%s)", x) 
                                   for x in comment_tuples)
            cur.execute("INSERT INTO main_comments VALUES " + comment_str)
        submission_query =  "INSERT INTO main_submissions VALUES (%s, %s, %s, %s)"
        cur.execute(submission_query, submission_tuple)
        comment_count = comment_count + len(comment_list)
        # The rest is for pretty tracking of progress
        sys.stdout.write("\rComments processed: %d" % comment_count)
        sys.stdout.flush()
        # Exit if you've downloaded more than comments_threshold comments
        if comment_count > comments_threshold: break
    t_finish = time.time()
    print 'Runtime: ' + (t_finish - t_start)

#Check the total amount of submissions and comments downloaded:
all_comments = pd.read_sql("SELECT * FROM main_comments", con)
all_submissions = pd.read_sql("SELECT * FROM main_submissions", con)
print "Total number of comments downloaded:", all_comments.shape[0]
print "Total number of submissions downloaded:", all_submissions.shape[0]

con.commit()
cur.close()
con.close()