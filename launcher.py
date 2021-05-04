import requests
import os
import json
import time
import sys
import warnings
import msvcrt
import pathlib
from subprocess import Popen

currentpath = str(pathlib.Path(__file__).parent.absolute())

def die(msg):
    print(msg, end = "")
    input()
    sys.exit()

def selectGame():
    print("\n> ", end = "")
    keystroke = msvcrt.getch().decode("utf-8")
    print(keystroke)

    if keystroke.lower() == "j":
        join(int(input("\nenter the place ID of the game you want to join: ")))
    elif keystroke in quickPlayGames:
        join(quickPlayGames[keystroke.lower()])
    else:
        print("\ninvalid option")
        selectGame()

def join(placeID):
    print("\nchecking latest version of ROBLOX... ", end = "")
    version = requests.get("http://setup.roblox.com/version.txt").content.decode("ascii")
    path = os.getenv("LOCALAPPDATA")+"\\Roblox\\Versions\\"+version
    print("done! ("+version+")")

    if not os.path.exists(path):
        print("\nupdating ROBLOX, please wait... ", end = "")

        bootstrapper = requests.get("http://setup.roblox.com/RobloxPlayerLauncher.exe", verify=False)
        open(currentpath+"\\RobloxPlayerLauncher.exe", "wb").write(bootstrapper.content)

        os.system('"'+currentpath+'\\RobloxPlayerLauncher.exe" -install')
        os.remove(currentpath+"\\RobloxPlayerLauncher.exe")

        print("done!")

    print("fetching CSRF token... ", end = "")
    req = requests.post(
        "https://auth.roblox.com/v1/authentication-ticket",
        headers = {"Cookie": ".ROBLOSECURITY="+config['.ROBLOSECURITY']}
    )
    csrf = req.headers['x-csrf-token']
    print("done!")

    print("fetching authentication ticket... ", end = "")
    req = requests.post(
        "https://auth.roblox.com/v1/authentication-ticket",
        headers =
        {
            "Cookie": ".ROBLOSECURITY="+config['.ROBLOSECURITY'],
            "Origin": "https://www.roblox.com",
            "Referer": "https://www.roblox.com/",
            "X-CSRF-TOKEN": csrf
        }
    )

    if(len(req.content) > 2):
        die("failed!\n\ncould not fetch authentication ticket - check that your .ROBLOSECURITY cookie is valid")

    ticket = req.headers['rbx-authentication-ticket']
    print("done!")

    print("\nstarting ROBLOX... ")

    if config['LaunchMode'] == "RobloxBootstrapper":
        location = path+"\\RobloxPlayerLauncher.exe"
        args = "roblox-player:1+launchmode:play+gameinfo:{ticket}+launchtime:{timestamp}+placelauncherurl:https%3A%2F%2Fassetgame.roblox.com%2Fgame%2FPlaceLauncher.ashx%3Frequest%3DRequestGame%26placeId%3D{placeID}%26isPlayTogetherGame%3Dfalse"
    elif config['LaunchMode'] == "DirectLaunch":
        location = path+"\\RobloxPlayerBeta.exe"
        args = "--play -a https://auth.roblox.com/v1/authentication-ticket/redeem -t {ticket} -j https://assetgame.roblox.com/game/PlaceLauncher.ashx?request=RequestGame^&placeId={placeID}^&isPlayTogetherGame=false --launchtime={timestamp}"

    Popen([location, args.format(ticket = ticket, timestamp = '{0:.0f}'.format(round(time.time() * 1000)), placeID = placeID)])

    time.sleep(5)

os.system("cls")
print("ROBLOX desktop launcher - who needs a web browser?\n")

if not os.path.exists(currentpath+"\\config.json"):
	print("could not find config.json, is it in the same folder as the python script?")

config = json.loads(open(currentpath+"\\config.json", "r").read())

if "!!!" in config['.ROBLOSECURITY']:
    die("please configure your .ROBLOSECURITY cookie in config.json - you can obtain it using a browser cookie editor")

if not config['LaunchMode'] in ["RobloxBootstrapper", "DirectLaunch"]:
    die("LaunchMode option is invalid - configure it in config.json to be either 'RobloxBootstrapper' or 'DirectLaunch'")

if config['QuickPlay']:
    print("choose a game to play:")
    quickPlayGames = {}
    for game in config['QuickPlay']:
        quickPlayGames[game['KeyIndex']] = game['ID']
        print("[{0}] {1}".format(game['KeyIndex'], game['Name']))

print("\n[j] Join via place ID")

selectGame()