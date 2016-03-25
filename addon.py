import sys
import urllib
import urlparse
import xbmcgui
import xbmcplugin
import xbmcaddon
import requests
from xbmc import log as xbmc_log
from urlparse import parse_qsl

requests.packages.urllib3.disable_warnings()

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

xbmcplugin.setContent(addon_handle, 'movies')

my_addon = xbmcaddon.Addon()

def build_url(query):
    return base_url + '?' + urllib.urlencode(query)

mode = args.get('mode', None)

# begin to write api logic

username = my_addon.getSetting('username')
password = my_addon.getSetting('password')

print(username + " " + password)

api_base = 'https://storage.rcs-rds.ro'

s = requests.Session()

# get auth token

token = s.get(api_base + '/token', headers = {'X-Koofr-Email': username, 'X-Koofr-Password': password}).headers['X-Koofr-Token']

s.headers['Authorization'] = 'Token ' + token

# get mount (Digi Cloud, Dropbox...)

mounts = s.get(api_base + '/api/v2/mounts').json()['mounts']

mount = [x for x in mounts if x['name'] == 'Digi Cloud'][0]

print(mount['name'] + mount['id'])

if mode is None:
    xbmc_log(u'%s: %s' % ('Digi Storage Player', 'Mode none'))
    files = s.get(api_base + '/api/v2/mounts/' + mount['id'] + '/files/list', params = {'path': '/'}).json()['files']
    for file in files:
        if file['type'] == 'dir':
            url = build_url({'mode': 'folder', 'foldername': '/' + file['name'], 'action': 'folder'})
            li = xbmcgui.ListItem('/' + file['name'], iconImage='DefaultFolder.png')
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                listitem=li, isFolder=True)
        elif '.mp3' in file['name'] or '.mkv' in file['name']:
##            url = s.get(api_base + '/api/v2/mounts/' + mount['id'] + '/files/download', params = {'path': '/'+file['name']}, verify=False).json()['link']
##            li = xbmcgui.ListItem(file['name'], iconImage='media.png')
##            li.setProperty('IsPlayable', 'true')
##            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)
            url = build_url({'mode': 'video', 'foldername': '/' + file['name']})
            li = xbmcgui.ListItem(file['name'], iconImage='DefaultFolder.png')
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                listitem=li, isFolder=False)
        elif '.jpg' in file['name'] or '.png' in file['name'] or '.jpeg' in file['name']:
            url = build_url({'mode': 'picture', 'foldername': '/' + file['name']})
            li = xbmcgui.ListItem(file['name'], iconImage='DefaultFolder.png')
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)

    xbmcplugin.endOfDirectory(addon_handle)
elif mode[0] == 'folder':
    xbmc_log(u'%s: %s' % ('Digi Storage Player', 'Mode folder'))
    listing = []
    foldername = args['foldername'][0]
    files = s.get(api_base + '/api/v2/mounts/' + mount['id'] + '/files/list', params = {'path': foldername + '/'}).json()['files']
    for file in files:
        if file['type'] == 'dir':
            xbmc_log(u'%s: %s' % ('Digi Storage Player', file['name']))
            url = build_url({'mode': 'folder', 'foldername': foldername + '/' + file['name']})
            li = xbmcgui.ListItem(foldername + '/' + file['name'], iconImage='DefaultFolder.png')
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                listitem=li, isFolder=True)
        elif '.mp3' in file['name'] or '.mkv' in file['name']:
            tempoUrl = s.get(api_base + '/api/v2/mounts/' + mount['id'] + '/files/download', params = {'path': foldername + '/' + file['name']}, verify=False).json()['link']
            url = build_url({'mode': 'picture', 'foldername': tempoUrl})
            li = xbmcgui.ListItem(file['name'], iconImage='DefaultFolder.png')
            li.addContextMenuItems([ ('Play', 'PlayMedia('+tempoUrl+')')])
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                listitem=li, isFolder=False)
            
##            tempoUrl = s.get(api_base + '/api/v2/mounts/' + mount['id'] + '/files/download', params = {'path': foldername + '/' + file['name']}, verify=False).json()['link']
##            list_item = xbmcgui.ListItem(label=file['name'], thumbnailImage='thumbnail.jpg')
##            list_item.setProperty('fanart_image', 'thumbnail.jpg')
##            list_item.setInfo('video', {'title': file['name'], 'genre': 'Video'})
##            list_item.setProperty('IsPlayable', 'true')
##            url = build_url({'mode': 'video', 'url': tempoUrl})
##            is_folder = False
##            listing.append((url, list_item, is_folder))

        elif '.jpg' in file['name'] or '.png' in file['name'] or '.jpeg' in file['name']:
            url = build_url({'mode': 'picture', 'foldername': foldername + '/' + file['name']})
            li = xbmcgui.ListItem(file['name'], iconImage='DefaultFolder.png')
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                listitem=li, isFolder=False)
##    xbmcplugin.addDirectoryItems(addon_handle, listing, len(listing))
##    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
##    xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(addon_handle)
elif mode[0] == 'picture':
    if 'https://' in args['foldername'][0]:
        xbmc_log(u'%s: %s' % ('Digi Storage Player', 'Mode video ###########################################################################'))
##        play_item = xbmcgui.ListItem(path=args['foldername'][0])
##        xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)
        xbmc.executebuiltin('PlayMedia('+args['foldername'][0]+')')
    else:
        xbmc_log(u'%s: %s' % ('Digi Storage Player', 'Mode picture'))
        url = s.get(api_base + '/api/v2/mounts/' + mount['id'] + '/files/download', params = {'path': args['foldername'][0]}, verify=False).json()['link']
        xbmc.executebuiltin('ShowPicture('+url+')')
else:
    if mode[0] == 'play':
        xbmc_log(u'%s: %s' % ('Digi Storage Player', 'Mode video ###########################################################################'))
        xbmc_log(u'%s: %s' % ('Digi Storage Player', 'Url = '+args['foldername'][0]))
        play_item = xbmcgui.ListItem(path=args['foldername'][0])
        xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)
