VERSION = 1.0.1

CONFIG = {
    "USERS": {
        "USERID": { # The users ID
            "WEBHOOK": "", # The webhook to send the data to
            "PING": True, # Wether to ping when the users status changes or when the user gets a new badge
        }
    },
    "DELAY": 5, # This is the amount of time between checks, a delay of 30-60 is recommended to not get ratelimited
    "COOKIE": False # Using Cookie allows you to get join link if their joins are on, if you decide to enable this, put your cookie in .ROBLOSECURITY.txt
}




























########################## DO NOT EDIT BELOW HERE IF YOU DO NOT KNOW WHAT YOU ARE DOING ##########################

import requests
import time
from collections import Counter

if CONFIG["COOKIE"]:
    with open(".ROBLOSECURITY.txt", "r") as Cookie:
        CONFIG["COOKIE"] = Cookie.read()
else:
    CONFIG["COOKIE"] = None

SAVE_TEMPLATE = {
    "LAST_STATUS": None,
    "USERNAME": None,
    "DISPLAYNAME": None,
    "THUMBNAIL": None,
    "DESCRIPTION": None,
    "LASTBADGEID": None
}

SAVES = {}

def GetUsers():
    return list(CONFIG["USERS"].keys())

def GetUserData(ID):
    return requests.get(f"https://users.roblox.com/v1/users/{ID}")

def GetUserThumbnail(ID, SizeX, SizeY):
    return requests.get(f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={ID}&size={SizeX}x{SizeY}&format=Png&isCircular=false&thumbnailType=HeadShot")

def GetAssetThumbnail(ID, SizeX, SizeY):
    return requests.get(f"https://thumbnails.roblox.com/v1/assets?assetIds={ID}&returnPolicy=PlaceHolder&size={SizeX}x{SizeY}&format=Png&isCircular=false")

def GetBadges(ID):
    return requests.get(f"https://badges.roblox.com/v1/users/{ID}/badges?sortOrder=Desc&limit=100&cursor=")

def GetOrdinalSuffix(number):
    if 11 <= number % 100 <= 13:
        return f"{number}th"
    else:
        return f"{number}{['th', 'st', 'nd', 'rd', 'th'][min(number % 10, 4)]}"

def SendWebhook(Webhook, Ping = False, Username = "RBXStalker", Avatar = "https://devforum-uploads.s3.dualstack.us-east-2.amazonaws.com/uploads/original/4X/f/6/b/f6b271550904ddeb16cec50fc9f34f84cb3ddb40.png", Title = "RBXStalker Started", Description = "You will now recieve messages about your selected users in this channel", Thumbnail = "https://avatars.githubusercontent.com/u/127895682?v=4", Color=0xFF0000):
    URL = Webhook

    Data = {
        "content": (Ping and "@everyone " or ""),
        "username": Username,
        "avatar_url": Avatar,
    }

    Data["embeds"] = [
        {
            "description": Description,
            "title": Title,
            "color": Color,
            "thumbnail": {
                "url": Thumbnail
            },
            "footer": {
                "text": "RBXStalker by astacodes"
            }
        }
    ]

    response = requests.post(URL, json=Data)
    if response.status_code != 204:
        print(f"Error sending webhook: {response.status_code} - {response.text}")

def CheckRecentBadges(UserIDStr, Webhook):
    Badges = GetBadges(UserIDStr)

    if Badges.status_code != 200:
        print(f"Error fetching Badges: {Badges.status_code} - {Badges.text}")
        return

    Badges = Badges.json()

    if not Badges["data"]:
        return

    MostRecentBadge = Badges["data"][0]
    MostRecentBadgeId = MostRecentBadge['id']
    MostRecentBadgeName = MostRecentBadge['name']
    MostRecentBadgePlace = MostRecentBadge['awarder']['id']

    if SAVES[UserIDStr]["LASTBADGEID"] != MostRecentBadgeId:
        SAVES[UserIDStr]["LASTBADGEID"] = MostRecentBadgeId

        AssetThumbnail = GetAssetThumbnail(MostRecentBadge["iconImageId"], 420, 420).json()
        Thumbnail = AssetThumbnail["data"][0]["imageUrl"]

        Title = f"{SAVES[UserIDStr]['DISPLAYNAME']} (@{SAVES[UserIDStr]['USERNAME']}) earned a new badge!"
        Description = f"[**{SAVES[UserIDStr]['DISPLAYNAME']}**](https://roblox.com/users/{UserIDStr}) just earned the badge: [**{MostRecentBadgeName}**](https://roblox.com/badges/{MostRecentBadgeId})!\nThis badge was awarded in the [**this game**](https://roblox.com/games/{MostRecentBadgePlace})!"
        Color = 0xFFFF00

        if Webhook:
            SendWebhook(
                Webhook=CONFIG["USERS"][UserIDStr]["WEBHOOK"],
                Ping=CONFIG["USERS"][UserIDStr]["PING"],
                Username=f"{SAVES[UserIDStr]['DISPLAYNAME']} (@{SAVES[UserIDStr]['USERNAME']})",
                Avatar=SAVES[UserIDStr]["THUMBNAIL"],
                Title=Title,
                Description=Description,
                Thumbnail=Thumbnail,
                Color=Color
            )

            print(f"[+] New badge detected for {SAVES[UserIDStr]['DISPLAYNAME']} (@{SAVES[UserIDStr]['USERNAME']}): {MostRecentBadgeName}")

def CheckStatus():
    Headers = {}
    if CONFIG["COOKIE"]:
        Headers["Cookie"] = f".ROBLOSECURITY={CONFIG['COOKIE']}"

    Request = requests.post(
        "https://presence.roblox.com/v1/presence/users",
        json={"userIds": GetUsers()},
        headers=Headers
    )


    if Request.status_code != 200:
        print(f"Error fetching presence data: {Request.status_code} - {Request.text}")
        return
    
    for Data in Request.json()['userPresences']:
        UserIDStr = str(Data["userId"])
        CurrentStatus = Data["userPresenceType"]
        UserConfig = SAVES[UserIDStr]
        LastStatus = UserConfig["LAST_STATUS"]

        CheckRecentBadges(UserIDStr, True)

        if CurrentStatus == LastStatus:
            continue

        Thumbnail = UserConfig["THUMBNAIL"]
        Username = UserConfig["USERNAME"]
        DisplayName = UserConfig["DISPLAYNAME"]
        Description = UserConfig["DESCRIPTION"]

        if CurrentStatus == 0:  # Offline
            #print(f"{DisplayName} (@{Username}) is Offline.")
            continue
        elif CurrentStatus == 1:  # Online
            Title = f"{DisplayName} (@{Username}) is Online!"
            Description = f"[**{DisplayName}**](https://roblox.com/users/{UserIDStr}) is now Online!"
            Color = 0x4287f5
        elif CurrentStatus == 2:  # In-Game
            Title = f"{DisplayName} (@{Username}) is In-Game!"
            Description = f"[**{DisplayName}**](https://roblox.com/users/{UserIDStr}) is now in a Game!"
            Color = 0x37B06D

            if Data["gameId"] != None:
                Description = Description + f"\n{DisplayName} has their joins on, you can join them [**here**](https://www.roblox.com/games/start?placeId={Data['placeId']}&launchData={Data['gameId']})"
    
            if Data["gameId"] is None:
                Badges = GetBadges(UserIDStr)

                if Badges.status_code != 200:
                    print(f"Error fetching Badges: {Badges.status_code} - {Badges.text}")
                else:
                    Badges = Badges.json()

                    GameToRecentBadge = {}
                    GameBadgeCount = Counter()

                    for Index, Badge in enumerate(Badges["data"]):
                        GameId = Badge['awarder']['id']
                        if GameId not in GameToRecentBadge:
                            GameToRecentBadge[GameId] = Index
                        GameBadgeCount[GameId] += 1

                    SortedGames = sorted(GameToRecentBadge.items(), key=lambda item: item[1])

                    PotentialGames = "\n\nPossible Games"
                    for GameIndex, (GameId, BadgeIndex) in enumerate(SortedGames[:5], start=1):
                        RecentText = f"{GetOrdinalSuffix(BadgeIndex + 1)} most recent badge -"
                        BadgeCountText = f"{GameBadgeCount[GameId]} badge(s) from game"

                        PotentialGames += f"\n[Game {GameIndex}](https://roblox.com/games/{GameId}) - {RecentText} {BadgeCountText}"

                    Description += PotentialGames

        elif CurrentStatus == 3:  # In-Studio
            Title = f"{DisplayName} (@{Username}) is in Studio!"
            Description = f"[**{DisplayName}**](https://roblox.com/users/{UserIDStr}) is now in Roblox Studio!"
            Color = 0xEE8700
        elif CurrentStatus == 4:  # Invisible
            Title = f"{DisplayName} (@{Username}) is Invisible!"
            Description = f"[**{DisplayName}**](https://roblox.com/users/{UserIDStr}) is now Invisible!"
            Color = 0xa3a09b

        print(f"[+] Status change detected for {DisplayName} (@{Username}): {Title}")

        UserConfig["LAST_STATUS"] = CurrentStatus

        SendWebhook(Webhook=CONFIG["USERS"][UserIDStr]["WEBHOOK"], Ping=CONFIG["USERS"][UserIDStr]["PING"], Username=f"{DisplayName} (@{Username})", Avatar=Thumbnail, Title=Title, Description=Description, Thumbnail=Thumbnail, Color=Color)

for UserIDStr in GetUsers():
    UserData = GetUserData(UserIDStr).json()
    UserThumbnail = GetUserThumbnail(UserIDStr, 420, 420).json()

    Thumbnail = UserThumbnail["data"][0]["imageUrl"]
    Username = UserData["name"]
    DisplayName = UserData["displayName"]
    Description = UserData["description"]

    SAVES[UserIDStr] = SAVE_TEMPLATE.copy()

    SAVES[UserIDStr]["USERNAME"] = Username
    SAVES[UserIDStr]["DISPLAYNAME"] = DisplayName
    SAVES[UserIDStr]["THUMBNAIL"] = Thumbnail
    SAVES[UserIDStr]["DESCRIPTION"] = Description
    SAVES[UserIDStr]["LASTBADGEID"] = None

    CheckRecentBadges(UserIDStr, False)

print(f"[+] Running RBXStalker Version {VERSION}")
print(f"[+] Developed by astacodes")

for UserIDStr, UserConfig in CONFIG["USERS"].items():
    SendWebhook(UserConfig["WEBHOOK"])

while True:
    CheckStatus()
    time.sleep(CONFIG["DELAY"])
