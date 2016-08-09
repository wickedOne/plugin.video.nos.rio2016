import xbmcplugin
import xbmcgui
import xbmcaddon
import sys
import re
import urllib
import urllib2
import urlparse
import json

# uris
plugin_url = sys.argv[0]
base_url = 'http://nos.nl/rio2016/live/'

# regex
re_stream = re.compile('.*\("([^"]+)"\)')

# args
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
mode = args.get('mode', None)
loc = args.get('location', None)
xbmcplugin.setContent(addon_handle, 'episodes')

def build_url(query):
    return plugin_url + '?' + urllib.urlencode(query)
    
def addLink(channel, location, mode):
    url = build_url({'mode': mode, 'location': location})
    li = xbmcgui.ListItem(channel)
    li.setProperty('IsPlayable', 'true')
    xbmcplugin.addDirectoryItem(addon_handle, url = url, listitem = li, isFolder=False)
    
    return urllib2.urlopen(req).read().replace('\n', '')

def playStream(location):
    stream = getStream('http://www-ipv4.nos.nl/livestream/resolve/', location)
    listItem = xbmcgui.ListItem(path=stream)
    listItem.setProperty('IsPlayable', 'true')
        
    xbmcplugin.setResolvedUrl(addon_handle, True, listItem)

        
def getStream(url, data):
    # first we'll retrieve a token
    req = urllib2.Request(url)
    response = urllib2.urlopen(req, '{"stream":"' + data + '"}').read().replace('\\', '')
    response_json = json.loads(response)

    # then we'll use the token to retrieve the stream uri
    stream_req = urllib2.Request(response_json['url'])
    stream_response = urllib2.urlopen(stream_req).read().replace('\\', '')
    streams = re.findall(re_stream, stream_response)

    # return the first match (should be one)
    for stream in streams:
        return stream

if mode is None:
    req = urllib2.Request(base_url)
    req.add_header('X-Requested-With', 'XMLHttpRequest')
    response_json = json.loads(urllib2.urlopen(req).read())
    
    for channel in response_json['live']:
        title = channel['title']
        
        if (channel['is_live'] == 1) or (channel['has_dutch_participants'] == 1):
            if (channel['is_live'] == 1):
                title = title + ' (live)'
            if (channel['has_dutch_participants'] == 1):
                title = title + ' (NL)'
                
        addLink(title, channel['channel']['stream'], 'channel')

    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'channel':
    playStream(loc[0])
        
    xbmcplugin.endOfDirectory(addon_handle)