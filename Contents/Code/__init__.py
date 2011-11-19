import re

####################################################################################################

VIDEO_PREFIX = "/video/playon"

BASE_URL = "%s%s"
BASE_ID_URL = "%s/data/data.xml?id=%s"
BASE_VIDEO_URL = "%s/%s/main.m3u8"

NAME = L('Title')

# Default artwork and icon(s)
ART           = 'art-default.jpg'
ICON          = 'icon-default.png'
NEXT          = 'icon-more.png'

####################################################################################################
def Start():
    Plugin.AddPrefixHandler(VIDEO_PREFIX, ChannelMainMenu, L('VideoTitle'), ICON, ART)

    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

    # Set the default ObjectContainer attributes
    ObjectContainer.art = R(ART)
    ObjectContainer.title1 = NAME
    ObjectContainer.view_group = "List"

    # Default icons for DirectoryObject and WebVideoItem
    DirectoryObject.thumb = R(ICON)
    DirectoryObject.art = R(ART)
    VideoClipObject.thumb = R(ICON)
    VideoClipObject.art = R(ART)

    # Set the default cache time
    HTTP.CacheTime = CACHE_1HOUR
    HTTP.Headers['User-Agent'] = "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2.16) Gecko/20110319 Firefox/3.6.16"

####################################################################################################
def GetBaseUrl(data):
    return BASE_URL % ('http://192.168.1.107:54479', data)

def GetBaseIdUrl(data):
    return BASE_ID_URL % ('http://192.168.1.107:54479', data)

def GetBaseVideoUrl(data):
    return BASE_VIDEO_URL % ('http://192.168.1.107:54479', data)

####################################################################################################
def ChannelMainMenu():
    oc = ObjectContainer(view_group='InfoList')
    
    xmlResult = XML.ObjectFromURL(GetBaseUrl('/data/data.xml'), timeout = 120)
    nodeList = xmlResult.xpath('/catalog/group')
    
    for xmlObj in nodeList:
        channelName = xmlObj.attrib['name']
        
        channelHref = xmlObj.attrib['href']
        idIndex = channelHref.find('id=')
        channelId = channelHref[idIndex+3:]
        
        channelArt = xmlObj.attrib['art']
        channelArtUrl = GetBaseUrl(channelArt)
        Log.Debug('Show Art: %s' % channelArtUrl)
        
        oc.add(DirectoryObject(key = Callback(FolderListMenu, id = channelId, showName = channelName, showArt = channelArtUrl, name = channelName), title = channelName, thumb = channelArtUrl))
    
    return oc

####################################################################################################
def FolderListMenu(id, showName, showArt, name):
    oc = ObjectContainer(view_group='InfoList', title2 = showName)
    
    xmlResult = XML.ObjectFromURL(GetBaseIdUrl(id), timeout = 120)
    nodeList = xmlResult.xpath('/group/group')
    for xmlObj in nodeList:
        nodeName = xmlObj.attrib['name']
        nodeHref = xmlObj.attrib['href']
        nodeType = xmlObj.attrib['type']
        
        idIndex = nodeHref.find('id=')
        folderId = nodeHref[idIndex+3:]
        
        if nodeType == 'folder':
            oc.add(DirectoryObject(key = Callback(FolderListMenu, id = folderId, showName = showName, showArt = showArt, name = nodeName), title = nodeName, thumb = showArt))
        else:
        
            if 'art' in xmlObj:
                nodeArt = xmlObj.attrib['art']
                nodeArt = nodeArt.replace('size=tiny','size=large')
                Log.Debug('Video Art: %s' % GetBaseUrl(nodeArt))
            else:
                nodeArt=''
                Log.Debug('Video Art: None')
            
            x = XML.ObjectFromURL(GetBaseIdUrl(folderId), timeout = 120)
            
            mediaTitleObj = x.xpath('/group/media_title')
            mediaTitle = mediaTitleObj[0].attrib['name']
            Log.Debug(mediaTitle)
            
            timeObj = x.xpath('/group/time')
            if len(timeObj) > 0:
                timeData = timeObj[0].attrib['name']
                timeList = timeData.split(':')
                
                hours = int(timeList[0])
                mins = int(timeList[1])
                secs = int(timeList[2])
                duration = ((hours * 60 * 60) + (mins * 60) + secs) * 1000
            else:
                duration = 0
            
            oc.add(VideoClipObject(
                url = GetBaseVideoUrl(folderId), 
                title = mediaTitle, 
                summary = '', 
                thumb = GetBaseUrl(nodeArt),
                duration = duration))
    
    if len(oc) == 0:
        return MessageContainer(name, "There are no videos available for the requested item.")

    return oc
