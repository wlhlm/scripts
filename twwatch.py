#!/usr/bin/env python3
# This script uses dmenu to select on of the current top streams on
# twitch and let's you play it with livestreamer.
#
# Twitch API: <https://github.com/justintv/twitch-api>
#
# Requirements:
#   dmenu
#   livestreamer

import subprocess
import json
import sys, os
import urllib.request, urllib.error, urllib.parse
from argparse import ArgumentParser

class Twitch:
    base_url = "https://api.twitch.tv/kraken"
    base_url_header = {"Accept": "application/vnd.twitchtv.v3+json"}

    def request_json(self, api_path):
        request = urllib.request.Request(self.base_url + api_path, data=None, headers=self.base_url_header)
        f = urllib.request.urlopen(request)
        return json.loads(f.read().decode("utf-8"))

class Top(Twitch):
    def __init__(self):
        self.games = []

    def load_games(self, num):
        games = self.request_json("/games/top?" + urllib.parse.urlencode({"limit": num}))
        for game in games["top"]:
            self.games.append(Game(game["game"]["name"], game["viewers"]))

class Game(Twitch):
    def __init__(self, name, viewers=0):
        self.name = name
        self.viewers = viewers
        self.streams = []

    def load_streams(self, num):
        streams = self.request_json("/streams?" + urllib.parse.urlencode({"limit": num, "game": self.name}))
        for stream in streams["streams"]:
            self.streams.append(Stream(stream["channel"]["display_name"], stream["channel"]["url"], stream["viewers"]))

class Stream(Twitch):
    def __init__(self, name, url, viewers=0):
        self.name = name
        self.url = url
        self.viewers = viewers

    def play(self, args):
        return subprocess.call("livestreamer " + self.url, shell=True, stdout=subprocess.DEVNULL)

# Construct the game name for dmenu: <game> [<viewers>]
def make_dmenu_string(game_name, viewers):
    return game_name + " [" + str(viewers) + "]"

def call_dmenu(args, input):
    try:
        output = subprocess.check_output("dmenu " + args, input=input, shell=True, universal_newlines=True)
        return output

    except subprocess.CalledProcessError as error:
        print("dmenu returned non-zero exit status", file=sys.stderr)
        returncode = error.returncode

    exit(returncode)

if __name__ == "__main__":
    dmenu_game_list = {}
    dmenu_stream_list = {}

    # Handle arguments
    arg_parser = ArgumentParser()
    arg_parser.add_argument("-r", "--results", default=15, type=int, metavar="NUM", help="number of results to get with each query")
    arg_parser.add_argument("--dmenu", default="", metavar="ARGS", help="parameters passed to dmenu")
    arg_parser.add_argument("--livestreamer", default="", metavar="ARGS", help="parameters passed to livestreamer")
    arguments = arg_parser.parse_args()

    top = Top()
    # Get the list of the currently top viewed games
    top.load_games(arguments.results)

    for game in top.games:
        dmenu_game_list[make_dmenu_string(game.name, game.viewers)] = game

    dmenu_input = ""
    for game in sorted(dmenu_game_list, key=lambda k: dmenu_game_list[k].viewers, reverse=True):
        dmenu_input = dmenu_input + game + "\n"

    game = dmenu_game_list[call_dmenu(arguments.dmenu + " -p \"Games >>\"", dmenu_input)[:-1]]
    game.load_streams(arguments.results)

    for stream in game.streams:
        dmenu_stream_list[make_dmenu_string(stream.name, stream.viewers)] = stream

    dmenu_input = ""
    for stream in sorted(dmenu_stream_list, key=lambda k: dmenu_stream_list[k].viewers, reverse=True):
        dmenu_input = dmenu_input + stream + "\n"

    stream = dmenu_stream_list[call_dmenu(arguments.dmenu + " -p \"Streams >>\"", dmenu_input)[:-1]]
    stream.play(arguments.livestreamer)
