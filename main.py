#!/usr/bin/env python

import json
import time
import cloudscraper
from threading import Thread

CONFIG = json.loads(open("./configuration.json", "r").read())
SCRAPER = cloudscraper.create_scraper()

VERIFY_TOKENS = CONFIG.get("verify_tokens")
TRACK_COOLDOWN = CONFIG.get("track_cooldown")
TOKENS_PATH = CONFIG.get("tokens_path")

assert VERIFY_TOKENS is not None, "verify tokens isn't set in your configuration"
assert TRACK_COOLDOWN is not None, "track cooldown isn't set in your configuration"
assert TOKENS_PATH is not None, "tokens path isn't set in your configuration"

class GiveawayJoiner:
    def __init__(self, token):
        self.token = token
        self.joinedGiveaways = []

        if VERIFY_TOKENS and not self.verifyToken(): return

        Thread(
            target = self.trackGiveaways
        ).start()

    def verifyToken(self):
        verifyRequest = SCRAPER.get("https://api.bloxybet.com/profile", headers = {
            "authorization": self.token,
            "referer": "https://www.bloxybet.com/"
        })

        return verifyRequest.status_code == 200

    def trackGiveaways(self):
        while True:
            if giveaways != self.joinedGiveaways:
                if len(giveaways) == 0:
                    self.joinedGiveaways = []
                    continue

                nonJoinedGiveaways = [giveaway for giveaway in giveaways if giveaway not in self.joinedGiveaways]
                self.joinedGiveaways += nonJoinedGiveaways
                
                for nonJoinedGiveaway in nonJoinedGiveaways:
                    self.joinGiveaway(nonJoinedGiveaway)

    def joinGiveaway(self, giveawayId):
        SCRAPER.post("https://api.bloxybet.com/join_giveaway", headers = {
            "authorization": self.token,
            "referer": "https://www.bloxybet.com/"
        }, 
        json = {
            "giveaway_id": giveawayId
        })
        

def main():
    global giveaways
    giveaways = []
    tokens = [token.strip() for token in open(TOKENS_PATH, "r").readlines()]

    print("""lilyscripts giveaway joiner
          
future updates so i dont forget:
> token cache for performance
> discord webhook functionality
> remove invalid tokens from tokens file
> exception handling
> code annotations""")

    for token in tokens:
        GiveawayJoiner(token)

    while True:
        time.sleep(TRACK_COOLDOWN)

        giveawaysRequest = SCRAPER.get("https://api.bloxybet.com/giveaways/active", headers = {
            "referer": "https://www.bloxybet.com/"
        })

        if giveawaysRequest.status_code == 200:
            giveawaysJson = giveawaysRequest.json()["giveaways"]
            giveaways = [giveaway.get("_id") for giveaway in giveawaysJson]

if __name__ == "__main__":
    main()
