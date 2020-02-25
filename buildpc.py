import praw
import os
import re
import csv
from twilio.rest import Client
from datetime import datetime

def sendText (message):
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    client = Client(account_sid, auth_token)

    message = client.messages \
        .create(
            body = message,
            from_ = os.getenv('TWILIO_PHONE'),
            to = os.getenv('MY_PHONE')
        )


reddit = praw.Reddit('PC_BOT')
reddit.read_only = True

deals = {
    'buildapcsales':  ['SSD', 'RAM', 'Prebuilt']
}

csvfilepath = "log.csv"
body = ""
frame = []

with open (csvfilepath, 'r') as csvfile: 
    csvreader = csv.reader(csvfile, delimiter = '|') 
    for line in csvreader:
        frame.append(line)

LoggedPostIDs = [item[1] for item in frame]  

for subs in deals: 
    subreddit = reddit.subreddit(subs)

    for submission in subreddit.new(limit=20):
        postID = submission.id

        time = int((datetime.utcnow() - datetime.utcfromtimestamp(submission.created_utc)).seconds /60)
        score = submission.score

        if score > 30 and postID not in LoggedPostIDs: 
            parts = submission.title.partition('$')
            part2 = parts[0].split(']')
            cate = re.findall(r"\[(.+)", part2[0])[0].strip()
            price = re.findall(r"^.+?\.\d\d", parts[2])[0].strip() if '.' in parts[2] else parts[2].split(' ')[0]
            title = part2[-1].strip()
        
            with open(csvfilepath,'a',newline='\n') as csvFile:                        
                csvWriter = csv.writer(csvFile,delimiter='|')
                csvWriter.writerow([submission.subreddit
                                    ,submission.id
                                    ,datetime.fromtimestamp(submission.created_utc)
                                    ,cate
                                    ,title
                                    ,price
                                    ,submission.url])

            msgbody = "\nType: " + cate + "\nScore: " + str(score) + "\nPrice: " + price + \
                "\n" + title + "\nold.reddit.com" + str(submission.permalink.strip())
            sendText(msgbody)
            print(msgbody)

print ("Program run!")


        




