#!/usr/bin/env python

import argparse
from rdioapi import Rdio

CONSUMER_KEY = ""
CONSUMER_SECRET = ""

parser = argparse.ArgumentParser(
        description="Creates an Rdio playlist based on artists in <input_file>")
parser.add_argument('-f',
        dest='input_file',
        action='store',
        default=None,
        help="Input file containing names of artists")
parser.add_argument('-n',
        dest='pl_name',
        action='store',
        default=None,
        help="Name for playlist")
parser.add_argument('-d',
        dest='pl_desc',
        action='store',
        default=None,
        help="Description for playlist")
parser.add_argument('-c',
        dest='track_count',
        action='store',
        default=3,
        help="How many tracks per artists to add to playlist. Defaults to 3")
args = parser.parse_args()

if not args.input_file or not args.pl_name or not args.pl_desc:
    raise InputError('You must specify an input file containing a list of artists, \
            a name for your playlist, and a description for the playlist')

# Oauth authentication needed for creating the new playlist
state = {}
r = Rdio(CONSUMER_KEY, CONSUMER_SECRET, state)
print 'Get PIN code from the following URL: %s' % r.begin_authentication('oob')
r.complete_authentication(raw_input('enter pin code:'))

# Read the list of artists
artists = open(args.input_file, 'r').readlines()

# Find track keys for top 3 tracks per artist
pl_tracks = []
for a in artists:
    try:
        url = '/artist/' + a.strip().title().replace(' ', '_').replace('&', '') + '/'
        artist_key = r.getObjectFromUrl(url=url)['key']
        tracks = r.getTracksForArtist(artist=artist_key, count=args.track_count)
        # make sure key is for a track and for the right artist
        track_keys = [t['key'] for t in tracks \
                if t['artistUrl'].lower() == url.lower() \
                and t['key'].startswith('t')]
        for t in track_keys:
            pl_tracks.append(t)
    except:
        print 'artist DNE: %s' % a
        continue

# create the playlist
try:
    r.call("createPlaylist", name=args.pl_name, description=args.pl_desc, \
            tracks=','.join(pl_tracks))
except:
    print 'error creating playlist'


class InputError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)
