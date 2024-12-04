import asyncio, websockets, random, json, os
from uuid import uuid4

dbdir = "./Pickups/db.json"
tempdir = "./Pickups/temp.json"

scoreboard = {"Gytis5089": 0}

with open(dbdir, "r+") as f:
    data = json.load(f)

async def mineproxy(websocket):
    print("Connected")
    async def send(cmd):
        msg = {
            "header": {
                "version": 1,
                "requestId": f"{uuid4()}",
                "messagePurpose": "commandRequest",
                "messageType": "commandRequest"
            },
            "body": {
                "version": 1,
                "commandLine": cmd,
                "origin": {
                    "type": "player"
                }
            }
        }
        await websocket.send(json.dumps(msg))
    
    def getItem():
        with open(tempdir, "r+") as f:
            tdata = json.load(f)
            item = tdata["item"]
        return item

    async def setItem():
        with open(tempdir, "r+") as f:
            tdata = json.load(f)
            item = random.choice(list(data.keys()))
            item = data[item][random.choice(list(data[item].keys()))]
            tdata["item"] = item
            f.seek(0)
            f.truncate()
            json.dump(tdata, f, indent=4)
        await send(f"/say {item}")
        await send(f"/title @a title {item}")

    await send("/say WebSocket Successfully Connected")
    await websocket.send(
        json.dumps({
            "body": {
                "eventName": "ItemAcquired"
            },
            "header": {
                "requestId": f"{uuid4()}",
                "messagePurpose": "subscribe",
                "version": 1,
                "messageType": "commandRequest"
            }
        })
    )
    await websocket.send(
        json.dumps({
            "body": {
                "eventName": "PlayerMessage"
            },
            "header": {
                "requestId": f"{uuid4()}",
                "messagePurpose": "subscribe",
                "version": 1,
                "messageType": "commandRequest"
            }
        })
    )

    async for req in websocket:
        req = json.loads(req)
        print(req)
        try:
            if "acquisitionMethodId" in req["body"]:
                #item pickup
                #print(req["body"]["item"]["id"], req["body"]["item"]["aux"])
                if req["body"]["item"]["id"] in ["suspicious_stew"]:
                    req["body"]["item"]["aux"] = "0"
                item = getItem()
                if not item:
                    await setItem()
                elif data[req["body"]["item"]["id"]][str(req["body"]["item"]["aux"])] == item:
                    if req["body"]["player"]["name"] not in scoreboard:
                        scoreboard[req["body"]["player"]["name"]] = 0
                    scoreboard[req["body"]["player"]["name"]] += 1
                    await send(f"/say {req['body']['player']['name']} +1")
                    await setItem()
            elif "message" in req["body"]:
                #player message
                if "sender" in req["body"]:
                    #ensure real user, not ws message
                    if req["body"]["sender"] != "External":
                        #ensure player accounted for/in scoreboard
                        if req["body"]["sender"] not in scoreboard:
                            scoreboard[req["body"]["sender"]] = 0
                        #commands
                        if req["body"]["message"].lower() in ["!scores", "!score", "!leaderboard", "!lb", "!sb", "!scoreboard"]:
                            for player in scoreboard:
                                await send(f"/say {player} - {scoreboard[player]}")
                        
                        elif req["body"]["message"].lower() in ["!item", "!curritem", "!items", "!curritems"]:
                            item = getItem()
                            if not item:
                                await setItem()
                            else:
                                await send(f"/say {item}")
                        
                        elif req["body"]["sender"] == "Gytis5089":
                            #if msg sent by me
                            if req["body"]["message"].lower() == "!new":
                                await setItem()
                            elif req["body"]["message"].lower().startswith("!add"):
                                cmd = req["body"]["message"].split(" ")
                                if cmd[1].startswith('"') and cmd[1].endswith('"'):
                                    cmd[1] = cmd[1].split('"')[1]
                                if cmd[1] in scoreboard:
                                    try:
                                        cmd[2] = int(cmd[2])
                                        scoreboard[cmd[1]] += cmd[2]
                                    except:
                                        pass
            else:
                #idfk
                pass
        except Exception as e:
            raise e
        """
        {
            'body': {
                'acquisitionMethodId': 1,
                'count': 1,
                'item': {
                    'aux': 0,
                    'id': 'dirt',
                    'namespace': 'minecraft'
                },
                'player': {
                    'color': 'ffededed',
                    'dimension': 0,
                    'id': -4294967295,
                    'name': 'Gytis5089',
                    'position': {
                        'x': 243.1495666503906,
                        'y': 67.62001037597656,
                        'z': 135.1028442382812
                    },
                    'type': 'minecraft:player',
                    'variant': 0,
                    'yRot': -166.9980163574219
                }
            },
            'header': {
                'eventName': 'ItemAcquired',
                'messagePurpose': 'event',
                'version': 17039360
            }
        }
        
        
        
        {
            'body': {
                'acquisitionMethodId': 1,
                'count': 1,
                'item': {
                    'aux': 0,
                    'id': 'birch_log',
                    'namespace': 'minecraft'
                },
                'player': {
                    'color': 'ffededed',
                    'dimension': 0,
                    'id': -4294967295,
                    'name': 'Gytis5089',
                    'position': {
                        'x': 241.2298736572266,
                        'y': 67.62001037597656,
                        'z': 138.3257141113281
                    },
                    'type': 'minecraft:player',
                    'variant': 0,
                    'yRot': -77.78263854980469
                }
            },
            'header': {
                'eventName': 'ItemAcquired',
                'messagePurpose': 'event',
                'version': 17039360
            }
        }
        
        
        
        {
            'body': {
                'acquisitionMethodId': 2,
                'count': 4,
                'item': {
                    'aux': 0,
                    'id': 'birch_planks',
                    'namespace': 'minecraft'
                },
                'player': {
                    'color': 'ffededed',
                    'dimension': 0,
                    'id': -4294967295,
                    'name': 'Gytis5089',
                    'position': {
                        'x': 241.3385314941406,
                        'y': 67.62001037597656,
                        'z': 137.9034423828125
                    },
                    'type': 'minecraft:player',
                    'variant': 0,
                    'yRot': -74.14474487304688
                }
            },
            'header': {
                'eventName': 'ItemAcquired',
                'messagePurpose': 'event',
                'version': 17039360
            }
        }
        
        
        
        {
            'body': {
                'acquisitionMethodId': 1,
                'count': 1,
                'item': {
                    'aux': 0,
                    'id': 'spruce_planks',
                    'namespace': 'minecraft'
                },
                'player': {
                    'color': 'ffededed',
                    'dimension': 0,
                    'id': -4294967295,
                    'name': 'Gytis5089',
                    'position': {
                        'x': 241.1057891845703,
                        'y': 67.62001037597656,
                        'z': 137.8562622070312
                    },
                    'type': 'minecraft:player',
                    'variant': 0,
                    'yRot': -72.58562469482422
                }
            },
            'header': {
                'eventName': 'ItemAcquired',
                'messagePurpose': 'event',
                'version': 17039360
            }
        }
        """

async def main():
    async with websockets.serve(mineproxy, '0.0.0.0', 8134):
        print("Ready")
        await asyncio.Future()

asyncio.run(main())