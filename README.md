# RBXStalker
RBXStalker allows you to track down actions of specific users

## Configuration Options

```py
CONFIG = {
    "USERS": {
        "USERID": { # The users ID
            "WEBHOOK": "", # The webhook to send the data to
            "PING": True, # Wether to ping when the users status changes or when the user gets a new badge
        }
    },
    "DELAY": 30, # This is the amount of time between checks, a delay of 30-60 is recommended to not get ratelimited
    "COOKIE": False # Using Cookie allows you to get join link if their joins are on, if you decide to enable this, put your cookie in .ROBLOSECURITY.txt
}
```
The `DELAY` option decides how long the delay is between checks, a delay of 30-60 seconds is recommended to prevent ratelimiting.\
The `COOKIE` option is to get join links if the user has joins on. If you would like to enable this, put your `.ROBLOSECURITY` cookie in .ROBLOSECURITY.txt and set `COOKIE` to True. This is completely optional.\
For each user you would like to add, you can copy and paste the table `USERID` into the `USERS` table.\
The `PING` option decides wether to ping you once something happens/changes.\
In the `WEBHOOK` option, put the Discord webhook where you will recieve the messages\

Once all of that is done, just run `Bot.py`. You will need [Python](https://www.python.org/downloads/) to run the program.\
If you get an error, try running `pip install requests` in your Command Terminal and run `Bot.py` again.\

## Features

### Status Checker
Check when users status change, such as when they are online or in game.\
![image](https://github.com/user-attachments/assets/36e0a9b1-dc9f-40d3-b1a2-55c5b32f27d6)

### Joins Checker
Check if user has joins on, and if yes provide to link to join their server, this requires you to put your .ROBLOSECURITY cookie but is completely optional.\
![image](https://github.com/user-attachments/assets/b478ebff-096d-4ad6-a9e0-c6c528a9be0c)

### Game Guesser
The bot will automatically try and guess what game the user is playing based on their badges.\
![image](https://github.com/user-attachments/assets/81fc96c2-640f-47a0-a71f-8f22ba6dfc66)

### Badge Checker
Whenever the user earns a new badge, our bot will send you a notification. This can be extremely useful as it gets the exact game they are playing.\
![image](https://github.com/user-attachments/assets/cf297f8e-aa4f-4d0b-9457-c0667cf5540e)
