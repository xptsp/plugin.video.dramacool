import httplib,ast
import urllib,urllib2,re,sys
import cookielib,os,string,cookielib,StringIO,gzip
import os,time,base64,logging
from t0mm0.common.net import Net
import xml.dom.minidom
import xbmcaddon,xbmcplugin,xbmcgui
try: import simplejson as json
except ImportError: import json
import cgi
import datetime, time
from BeautifulSoup import BeautifulSoup
from BeautifulSoup import BeautifulStoneSoup
from BeautifulSoup import SoupStrainer
import urlresolver
import time

# Import database stuff and create database if necessary:
try:
	from sqlite3 import dbapi2
	from sqlite3 import Error
except:
	from pysqlite2 import dbapi2
	from pysqlite2mport import Error

# Addon settings:
ADDON = xbmcaddon.Addon(id='plugin.video.DramaCool')
AZ_DIRECTORIES = ['other','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y', 'Z']
strdomain ='https://www2.dramacool.video'
strdomain2 ='https://www.dramacool9.co'

# Google Analytics stuff:
if ADDON.getSetting('ga_visitor')=='':
	from random import randint
	ADDON.setSetting('ga_visitor',str(randint(0, 0x7fffffff)))
PATH = "PhumiKhmer"  #<---- PLUGIN NAME MINUS THE "plugin.video"
UATRACK="UA-40129315-1" #<---- GOOGLE ANALYTICS UA NUMBER
VERSION = "2.1.0" #<---- PLUGIN VERSION

##############################################
def HOME():
	addDir('Recently Viewed',strdomain,18,'')
	addDir('List A-Z',strdomain+"/drama-list/char-start-#.html",3,'')
	addDir('Latest Dramas',strdomain+'/recently-added',6,'')
	addDir('Most Popular Dramas',strdomain+'/most-popular-drama',6,'')
	addDir('Dramas by Country', strdomain2+"/category/drama/", 12, '')
	addDir('Dramas by Genre',strdomain+'/list-genres.html',13,'')
	addDir('Latest Movies',strdomain+'/recently-added-movie',6,'')
	addDir('Movies by Country', strdomain2+"/category/movies/", 12, '')
	addDir('Latest KShow',strdomain+'/recently-added-kshow',6,'')
	addDir('Search DramaCool',strdomain+'/search?type=movies&keyword=',4,'')
	addDir('Popular Stars',strdomain+'/list-star.html',15,'')
	addDir('Search Stars',strdomain+'/search?type=stars&keyword=',17,'')
	addDir('Refresh Database',strdomain+"/drama-list/char-start-#.html",19,'')

##############################################
def GetMenu(url,menutype):
	link = GetContent(url)
	if link == None:
		return
	try:
		link =link.encode("UTF-8")
	except: pass
	newlink = ''.join(link.splitlines()).replace('\t','')
	soup = BeautifulSoup(newlink)
	listcontent=soup.findAll('a', {"href":menutype})
	if(len(listcontent)>0):
		menuitem=listcontent[0].parent
		for item in menuitem.findAll('li'):
			if(item.a!=None and item.a.has_key("href")):
				link = strdomain2+item.a['href'].encode('utf-8', 'ignore')
				vname=str(item.a.contents[0]).strip()
				addDir(vname,link,9,"")

##############################################
def IndexLatest(url,notify=True):
	link = GetContent(url,notify)
	if link == None:
		return
	try:
		link =link.encode("UTF-8")
	except: pass
	newline = link
	try:
		newlink = ''.join(link.splitlines())
	except: pass
	newline = newline.replace('\t','')
	soup = BeautifulSoup(newlink)
	menucontent=soup.findAll('ul', {"class" : "switch-block list-episode-item"})
	if len(menucontent) > 0:
		for item in menucontent[0].findAll('li'):
			#print item
			vname=item.a.img["alt"]
			vurl=strdomain+item.a["href"]
			vimg=item.a.img["data-original"]
			info = Drama_Overview(vname, vurl, vimg)
			addDir(vname.encode('utf-8', 'ignore'),vurl,5,vimg, info)
	pagingList=soup.findAll('ul', {"class" : "pagination"})
	if(len(pagingList) >0):
		for item in pagingList[0].findAll('li'):
			#print item
			vname="Page "+ item.a["data-page"]
			vurl=url+item.a["href"]
			if(item.has_key("class")==False):
				addDir(vname.encode('utf-8', 'ignore'),vurl,6,"")

##############################################
def Index_co(url):
	link = GetContent(url)
	if link == None:
		return
	try:
		link =link.encode("UTF-8")
	except: pass
	newline = link
	try:
		newlink = ''.join(link.splitlines())
	except: pass
	newline = newline.replace('\t','')
	soup = BeautifulSoup(newlink)
	menucontent=soup.findAll('main', {"id" : "main"})
	if len(menucontent) > 0:
		for item in menucontent[0].findAll('li'):
			#print item
			vname=item.a["title"]
			vurl=item.a["href"]
			vimg=item.a.img["data-original"]
			info = Drama_Overview(vname, vurl, vimg)
			addDir(vname.encode('utf-8', 'ignore'),vurl,10,vimg,info=info)
		pagingList=menucontent[0].findAll('div', {"class" : "nav-links"})
		if(len(pagingList) >0):
			for item in pagingList[0].findAll('a',{"class" : "page-numbers"}):
				vname="Page "+ item.contents[0]
				vurl=item["href"]
				if(vurl.find(strdomain2)==-1):
					vurl=strdomain2+item["href"]
				addDir(vname.encode('utf-8', 'ignore'),vurl,9,"")

##############################################
def ListSource(url,series):
	link = GetContent(url)
	if link == None:
		return
	try:
		link =link.encode("UTF-8")
	except: pass
	newlink = ''.join(link.splitlines()).replace('\t','')
	setLastPlayed(url,series)
	soup = BeautifulSoup(newlink)
	listcontent=soup.findAll('div', {"class" : "anime_muti_link"})[0]
	srclist=listcontent.findAll('ul')
	info = Drama_Overview(series)
	if(len(srclist) >0):
		for item in srclist[0].findAll('li'):
			#print item
			vname=item.contents[0].encode('utf-8', 'ignore')
			vurl=item["data-video"]
			if vurl[0:2] == '//':
				vurl = "https:" + vurl
			addLink(vname,vurl,8,info[7])

##############################################
def ListSource_co(url,series):
	link = GetContent(url)
	if link == None:
		return
	try:
		link =link.encode("UTF-8")
	except: pass
	newlink = ''.join(link.splitlines()).replace('\t','')
	setLastPlayed(url, series)
	soup = BeautifulSoup(newlink)
	srclist=soup.findAll('div', {"id" : "w-server"})
	if(len(srclist) >0):
		for item in srclist[0].findAll('div',{"class":re.compile("serverslist*")}):
			#print item
			vname=item.contents[0].encode('utf-8', 'ignore')
			vurl=item["data-server"]
			if vurl[0:2] == '//':
				vurl = "https:" + vurl
			addLink(vname,vurl,8,"")

##############################################
def ListAZ(url,mode):
	for character in AZ_DIRECTORIES:
		chrUrl= url.replace('#',character)
		addDir(character.capitalize(),chrUrl,mode,"")

##############################################
def log(description, level=0):
	print description

##############################################
def fetchPage(params={}):
	get = params.get
	link = get("link")
	ret_obj = {}
	if get("post_data"):
		log("called for : " + repr(params['link']))
	else:
		log("called for : " + repr(params))

	if not link or int(get("error", "0")) > 2:
		log("giving up")
		ret_obj["status"] = 500
		return ret_obj

	if get("post_data"):
		if get("hide_post_data"):
			log("Posting data", 2)
		else:
			log("Posting data: " + urllib.urlencode(get("post_data")), 2)

		request = urllib2.Request(link, urllib.urlencode(get("post_data")))
		request.add_header('Content-Type', 'application/x-www-form-urlencoded')
	else:
		log("Got request", 2)
		request = urllib2.Request(link)

	if get("headers"):
		for head in get("headers"):
			request.add_header(head[0], head[1])

	request.add_header('User-Agent', "Mozilla/5.0 (Windows NT 6.2; Win64; x64; rv:16.0.1) Gecko/20121011 Firefox/16.0.1")

	if get("cookie"):
		request.add_header('Cookie', get("cookie"))

	if get("refering"):
		request.add_header('Referer', get("refering"))

	try:
		log("connecting to server...", 1)

		con = urllib2.urlopen(request)
		ret_obj["header"] = con.info()
		ret_obj["new_url"] = con.geturl()
		if get("no-content", "false") == u"false" or get("no-content", "false") == "false":
			inputdata = con.read()
			#data_type = chardet.detect(inputdata)
			#inputdata = inputdata.decode(data_type["encoding"])
			ret_obj["content"] = inputdata.decode("utf-8")

		con.close()

		log("Done")
		ret_obj["status"] = 200
		return ret_obj

	except urllib2.HTTPError, e:
		err = str(e)
		log("HTTPError : " + err)
		log("HTTPError - Headers: " + str(e.headers) + " - Content: " + e.fp.read())

		params["error"] = str(int(get("error", "0")) + 1)
		ret = fetchPage(params)

		if not "content" in ret and e.fp:
			ret["content"] = e.fp.read()
			return ret

		ret_obj["status"] = 500
		return ret_obj

	except urllib2.URLError, e:
		err = str(e)
		log("URLError : " + err)

		time.sleep(3)
		params["error"] = str(int(get("error", "0")) + 1)
		ret_obj = fetchPage(params)
		return ret_obj

##############################################
def getVimeoUrl(videoid,currentdomain=""):
	result = fetchPage({"link": "http://player.vimeo.com/video/%s?title=0&byline=0&portrait=0" % videoid,"refering": currentdomain})
	collection = {}
	if result["status"] == 200:
		html = result["content"]
		html = html[html.find('={')+1:]
		html = html[:html.find('}};')]+"}}"
		try:
			  collection = json.loads(html)
			  return collection["request"]["files"]["h264"]["sd"]["url"]
		except:
			  return getVimeoVideourl(videoid,currentdomain)

##############################################
def scrapeVideoInfo(videoid,currentdomain):
	result = fetchPage({"link": "http://player.vimeo.com/video/%s?title=0&byline=0&portrait=0" % videoid,"refering": currentdomain})
	collection = {}
	if result["status"] == 200:
		html = result["content"]
		html = html[html.find('{config:{'):]
		html = html[:html.find('}}},') + 3]
		html = html.replace("{config:{", '{"config":{') + "}"
		collection = json.loads(html)
	return collection

##############################################
def getVideoInfo(videoid,currentdomain):
	collection = scrapeVideoInfo(videoid)

	video = {}
	if collection.has_key("config"):
		video['videoid'] = videoid
		title = collection["config"]["video"]["title"]
		if len(title) == 0:
			title = "No Title"
		#title = common.replaceHTMLCodes(title)
		video['Title'] = title
		video['Duration'] = collection["config"]["video"]["duration"]
		video['thumbnail'] = collection["config"]["video"]["thumbnail"]
		video['Studio'] = collection["config"]["video"]["owner"]["name"]
		video['request_signature'] = collection["config"]["request"]["signature"]
		video['request_signature_expires'] = collection["config"]["request"]["timestamp"]

		isHD = collection["config"]["video"]["hd"]
		if str(isHD) == "1":
			video['isHD'] = "1"


	if len(video) == 0:
		log("- Couldn't parse API output, Vimeo doesn't seem to know this video id?")
		video = {}
		video["apierror"] = ""
		return (video, 303)

	log("Done")
	return (video, 200)

##############################################
def getVimeoVideourl(videoid,currentdomain):
	(video, status) = getVideoInfo(videoid,currentdomain)

	urlstream="http://player.vimeo.com/play_redirect?clip_id=%s&sig=%s&time=%s&quality=%s&codecs=H264,VP8,VP6&type=moogaloop_local&embed_location="
	get = video.get
	if not video:
		# we need a scrape the homepage fallback when the api doesn't want to give us the URL
		log("getVideoObject failed because of missing video from getVideoInfo")
		return ""

	quality = "sd"

	if ('apierror' not in video):
		video_url =  urlstream % (get("videoid"), video['request_signature'], video['request_signature_expires'], quality)
		result = fetchPage({"link": video_url, "no-content": "true"})
		video['video_url'] = result["new_url"]

		log("Done")
		return video['video_url']
	else:
		log("Got apierror: " + video['apierror'])
		return ""

##############################################
def SEARCH():
	try:
		keyb = xbmc.Keyboard('', 'Enter search text')
		keyb.doModal()
		#searchText = '01'
		if (keyb.isConfirmed()):
				searchText = urllib.quote_plus(keyb.getText())
		url = strdomain+'/search?type=movies&keyword='+searchText
		IndexLatest(url)
	except: pass

##############################################
def INDEX(url, index=-1):
	link = GetContent(url)
	if link == None:
		return
	try:
		link =link.encode("UTF-8")
	except: pass
	newline = link
	try:
		newlink = ''.join(link.splitlines())
	except: pass
	newline = newline.replace('\t','')
	soup = BeautifulSoup(newlink)
	listcontent=soup.findAll('ul', {"class" : "switch-block list-episode-item"})
	items = listcontent[0].findAll('li')
	pDialog = xbmcgui.DialogProgress()
	title = 'DramaCool'
	if index :
		title = title + ': Processing ' + AZ_DIRECTORIES[index] + "'s..."
	pDialog.create(title, 'Processing Drama list...', '')
	max = len(items)
	cnt = 1
	for item in items:
		#print item
		vname=item.a["title"]
		if vname == "":
			vname = item.a.h3.text
		vname=vname.strip()
		per = cnt * 100 / max
		pDialog.update( per, '(' + str(per) + '%) Processing Drama ' + str(cnt) + ' of ' + str(max) + '...', 'Drama: ' + vname)
		cnt += 1
		vurl=strdomain+item.a["href"]
		vimg=item.a.img["data-original"]
		canceled = pDialog.iscanceled()
		info = Drama_Overview(vname, vurl, vimg, cancelled=canceled)
		if index == -1:
			addDir(vname.encode('utf-8', 'ignore'),vurl,5,vimg,info)
	pDialog.close()

	#pagecontent=soup.findAll('div', {"class" : re.compile("page-nav*")})
	# label=""#re.compile("/label/(.+?)\?").findall(url)[0]
	# pagenum=re.compile("PageNo=(.+?)").findall(url)
	# prev="0"
	# if(len(pagenum)>0):
		  # prev=str(int(pagenum[0])-1)
		  # pagenum=str(int(pagenum[0])+1)

	# else:
		  # pagenum="2"
	# nexurl=buildNextPage(pagenum,label)

	# if(int(pagenum)>2 and prev=="1"):
		  # urlhome=url.split("?")[0]+"?"
		  # addDir("<< Previous",urlhome,2,"")
	# elif(int(pagenum)>2):
		  # addDir("<< Previous",buildNextPage(prev,label),2,"")
	# if(nexurl!=""):
		  # addDir("Next >>",nexurl,2,"")

	return canceled

##############################################
def is_number(s):
	try:
		float(s)
		return True
	except ValueError:
		return False

##############################################
def SearchResults(url):
	link = GetContent(url)
	if link == None:
		return
	newlink = ''.join(link.splitlines()).replace('\t','')
	match=re.compile('<h2 class="title"><a href="(.+?)" rel="bookmark" title="">(.+?)</a></h2>').findall(newlink)
	if(len(match) >= 1):
			for vLink, vLinkName in match:
				addDir(vLinkName,vLink,5,'')
	match=re.compile('<a class="next page-numbers" href="(.+?)">').findall(link)
	if(len(match) >= 1):
		nexurl= match[0]
		addDir('Next>',nexurl,6,'')

##############################################
def Episodes(url,name):
	d = xbmcgui.Dialog()
	link = GetContent(url)
	if link == None:
		return
	try:
		link =link.encode("UTF-8")
	except: pass
	newline = link
	try:
		newlink = ''.join(link.splitlines())
	except: pass
	newline = newline.replace('\t','')
	soup = BeautifulSoup(newlink)
	menucontent=soup.findAll('ul', {"class" : "list-episode-item-2 all-episode"})
	if len(menucontent) > 0:
		row = Drama_Overview(name, url)
		last_played = getLastPlayed(name)
		if last_played != None:
			addLink("[ Remove Series from Recently Viewed ]", name, 20, "")
		for item in menucontent[0].findAll('li'):
			#print item
			vname=item.h3.contents[0].replace(' Episode', ': Episode')
			vname=vname.strip()
			vepi = vname.split(": Episode ")[-1]
			vurl=strdomain+item.a["href"]
			info = Drama_Overview(vname, vurl, row[7], row)
			vname = info[11]
			vimg = info[7]
			vsubbed=item.findAll('span', {"class": "type subbed"})
			if (len(vsubbed) == 0):
				vsubbed=item.findAll('span', {"class": "type SUB"})
			if (len(vsubbed) == 0):
				vname = '[RAW] '+vname
			vselected = False
			if last_played != None:
				tname = vname+" "
				vselected = (tname.find(last_played+" ") != -1)
			info[6] = item.findAll('span', {"class": "time"})[0].text.split("?")[0]
			addDir(vname.encode('utf-8', 'ignore'),vurl,7,vimg,selected=vselected,info=info)

##############################################
def Episodes_co(url,name):
	link = GetContent(url)
	if link == None:
		return
	try:
		link =link.encode("UTF-8")
	except: pass
	newline = link
	try:
		newlink = ''.join(link.splitlines())
	except: pass
	newline = newline.replace('\t','')
	soup = BeautifulSoup(newlink)
	menucontent=soup.findAll('div', {"id" : "all-episodes"})
	if len(menucontent) > 0:
		row = Drama_Overview(name, url)
		last_played = getLastPlayed(name)
		if last_played != None:
			addLink("[ Remove Series from Recently Viewed ]", name, 20, "")
		for item in menucontent[0].findAll('li'):
			#print item
			vname=item.h3.a["title"].replace(' Episode', ': Episode')
			vname=vname.strip()
			vurl=item.h3.a["href"]
			vepi = vname.split(": Episode ")[-1]
			info = Drama_Overview(vname, vurl, row[7], row)
			vname = info[11]
			vimg = info[7]
			vsubbed=item.findAll('span', {"class": "type subbed"})
			if (len(vsubbed) == 0):
				vsubbed=item.findAll('span', {"class": "type SUB"})
			if (len(vsubbed) == 0):
				vname = '[RAW] '+vname
			vselected = False
			if last_played != None:
				tname = vname+" "
				vselected = (tname.find(last_played+" ") != -1)
			addDir(vname.encode('utf-8', 'ignore'),vurl,11,vimg,selected=vselected)

##############################################
def ParseSeparate(vcontent,namesearch,urlsearch):
	newlink = ''.join(vcontent.splitlines()).replace('\t','')
	match2=re.compile(urlsearch).findall(newlink)
	match3=re.compile(namesearch).findall(newlink)
	imglen = len(match3)
	if(len(match2) >= 1):
			for i in range(len(match2)):
				if(i < imglen ):
					namelink = match3[i]
				else:
					namelink ='part ' + str(i+1)
				addLink(namelink.encode("utf-8"),match2[i],3,"")
			return True
	return False

##############################################
def GetContent2(url,referr, cj):
	if cj is None:
		cj = cookielib.LWPCookieJar()
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
	opener.addheaders = [
		('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
		('Accept-Encoding', 'gzip, deflate'),
		('Referer', referr),
		('Content-Type', 'application/x-www-form-urlencoded'),
		('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:13.0) Gecko/20100101 Firefox/13.0'),
		('Connection', 'keep-alive'),
		('Accept-Language', 'en-us,en;q=0.5'),
		('Pragma', 'no-cache')]
	usock = opener.open(url)
	if usock.info().get('Content-Encoding') == 'gzip':
		buf = StringIO.StringIO(usock.read())
		f = gzip.GzipFile(fileobj=buf)
		response = f.read()
	else:
		response = usock.read()
	usock.close()
	return (cj, response)

##############################################
def GetContent(url,notify=True):
	try:
		net = Net()
		second_response = net.http_GET(url)
		return second_response.content
	except:
		print url
		if notify == True:
			xbmcgui.Dialog().ok(url,"Can't Connect to site",'Try again in a moment')

##############################################
def postContent(url,data,referr):
	opener = urllib2.build_opener()
	opener.addheaders = [
		('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
		('Accept-Encoding','gzip, deflate'),
		('Referer', referr),
		('Content-Type', 'application/x-www-form-urlencoded'),
		('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:13.0) Gecko/20100101 Firefox/13.0'),
		('Connection','keep-alive'),
		('Accept-Language','en-us,en;q=0.5'),
		('Pragma','no-cache'),
		('Host','www.phim.li')]
	usock=opener.open(url,data)
	if usock.info().get('Content-Encoding') == 'gzip':
		buf = StringIO.StringIO(usock.read())
		f = gzip.GzipFile(fileobj=buf)
		response = f.read()
	else:
		response = usock.read()
	usock.close()
	return response

##############################################
def playVideo(videoType,videoId):
	url = ""
	#print videoType + '=' + videoId
	win = xbmcgui.Window(10000)
	win.setProperty('1ch.playing.title', videoId)
	win.setProperty('1ch.playing.season', str(3))
	win.setProperty('1ch.playing.episode', str(4))
	if (videoId == ""):
		xbmcgui.Dialog().ok("DramaCool", "HTML parsing error encountered!", "Unable to determine video URL to play video!", "Please try another source!")
		return
	if (videoType == "youtube"):
		try:
			url = getYoutube(videoId)
			xbmcPlayer = xbmc.Player()
			xbmcPlayer.play(url)
		except:
			url = 'plugin://plugin.video.youtube?path=/root/video&action=play_video&videoid=' + videoId.replace('?','')
			xbmc.executebuiltin("xbmc.PlayMedia("+url+")")
	elif (videoType == "vimeo"):
		url = getVimeoUrl(videoId,strdomain)
		xbmcPlayer = xbmc.Player()
		xbmcPlayer.play(url)
	elif (videoType == "tudou"):
		url = 'plugin://plugin.video.tudou/?mode=3&url=' + videoId
		xbmcPlayer = xbmc.Player()
		xbmcPlayer.play(url)
	else:
		xbmcPlayer = xbmc.Player()
		xbmcPlayer.play(videoId)

##############################################
def GetDirVideoUrl(url, cj):
	if cj is None:
		cj = cookielib.LWPCookieJar()

	class MyHTTPRedirectHandler(urllib2.HTTPRedirectHandler):

		def http_error_302(self, req, fp, code, msg, headers):
			self.video_url = headers['Location']
			return urllib2.HTTPRedirectHandler.http_error_302(self, req, fp, code, msg, headers)

		http_error_301 = http_error_303 = http_error_307 = http_error_302

	redirhndler = MyHTTPRedirectHandler()

	opener = urllib2.build_opener(redirhndler, urllib2.HTTPCookieProcessor(cj))
	opener.addheaders = [(
		'Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
		('Accept-Encoding', 'gzip, deflate'),
		('Referer', url),
		('Content-Type', 'application/x-www-form-urlencoded'),
		('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:13.0) Gecko/20100101 Firefox/13.0'),
		('Connection', 'keep-alive'),
		('Accept-Language', 'en-us,en;q=0.5'),
		('Pragma', 'no-cache')]
	# urllib2.install_opener(opener)
	usock = opener.open(url)
	return redirhndler.video_url

##############################################
def loadVideos(url,name):
	xbmc.executebuiltin("XBMC.Notification(Please Wait!,Loading selected video)")
	newlink=url
	print newlink
	playtype="direct"
	if (newlink.find("dailymotion") > -1):
		match=re.compile('(dailymotion\.com\/(watch\?(.*&)?v=|(embed|v|user)\/))([^\?&"\'>]+)').findall(newlink)
		lastmatch = match[0][len(match[0])-1]
		link = 'http://www.dailymotion.com/'+str(lastmatch)
		req = urllib2.Request(link)
		req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
		response = urllib2.urlopen(req)
		link=response.read()
		response.close()
		sequence=re.compile('"sequence",  "(.+?)"').findall(link)
		newseqeunce = urllib.unquote(sequence[0]).decode('utf8').replace('\\/','/')
		#print 'in dailymontion:' + str(newseqeunce)
		imgSrc=re.compile('"videoPreviewURL":"(.+?)"').findall(newseqeunce)
		if(len(imgSrc[0]) == 0):
			imgSrc=re.compile('/jpeg" href="(.+?)"').findall(link)
		dm_low=re.compile('"sdURL":"(.+?)"').findall(newseqeunce)
		dm_high=re.compile('"hqURL":"(.+?)"').findall(newseqeunce)
		vidlink=urllib2.unquote(dm_low[0]).decode("utf8")
	elif (newlink.find("4shared") > -1):
		xbmcgui.Dialog().ok('Not Implemented','Sorry 4Shared links',' not implemented yet')
	elif (newlink.find("docs.google.com") > -1 or newlink.find("drive.google.com") > -1):
		docid=re.compile('/d/(.+?)/preview').findall(newlink)[0]
		cj = cookielib.LWPCookieJar()
		(cj,vidcontent) = GetContent2("https://docs.google.com/get_video_info?docid="+docid,"", cj)
		html = urllib2.unquote(vidcontent)
		cookiestr=""
		try:
			html=html.encode("utf-8","ignore")
		except: pass
		stream_map = re.compile('fmt_stream_map=(.+?)&fmt_list').findall(html)
		if(len(stream_map) > 0):
			formatArray = stream_map[0].replace("\/", "/").split(',')
			for formatContent in formatArray:
				 formatContentInfo = formatContent.split('|')
				 qual = formatContentInfo[0]
				 url = (formatContentInfo[1]).decode('unicode-escape')

		else:
			cj = cookielib.LWPCookieJar()
			newlink1="https://docs.google.com/uc?export=download&id="+docid
			(cj,vidcontent) = GetContent2(newlink1,newlink, cj)
			soup = BeautifulSoup(vidcontent)
			downloadlink=soup.findAll('a', {"id" : "uc-download-link"})[0]
			newlink2 ="https://docs.google.com" + downloadlink["href"]
			url=GetDirVideoUrl(newlink2,cj)
		for cookie in cj:
			cookiestr += '%s=%s;' % (cookie.name, cookie.value)
		vidlink=url+ ('|Cookie=%s' % cookiestr)
	elif (newlink.find("vimeo") > -1):
		idmatch =re.compile("http://player.vimeo.com/video/([^\?&\"\'>]+)").findall(newlink)
		if(len(idmatch) > 0):
			playVideo('vimeo',idmatch[0])
	elif (newlink.find("youtube") > -1) and (newlink.find("playlists") > -1):
		playlistid=re.compile('playlists/(.+?)\?v').findall(newlink)
		vidlink="plugin://plugin.video.youtube?path=/root/video&action=play_all&playlist="+playlistid[0]
	elif (newlink.find("youtube") > -1) and (newlink.find("list=") > -1):
		playlistid=re.compile('videoseries\?list=(.+?)&').findall(newlink+"&")
		vidlink="plugin://plugin.video.youtube?path=/root/video&action=play_all&playlist="+playlistid[0]
	elif (newlink.find("youtube") > -1) and (newlink.find("/p/") > -1):
		playlistid=re.compile('/p/(.+?)\?').findall(newlink)
		vidlink="plugin://plugin.video.youtube?path=/root/video&action=play_all&playlist="+playlistid[0]
	elif (newlink.find("youtube") > -1) and (newlink.find("/embed/") > -1):
		playlistid=re.compile('/embed/(.+?)\?').findall(newlink+"?")
		vidlink=getYoutube(playlistid[0])
	elif (newlink.find("youtube") > -1):
		match=re.compile('(youtu\.be\/|youtube-nocookie\.com\/|youtube\.com\/(watch\?(.*&)?v=|(embed|v|user)\/))([^\?&"\'>]+)').findall(newlink)
		if(len(match) == 0):
			match=re.compile('http://www.youtube.com/watch\?v=(.+?)&dk;').findall(newlink1)
		if(len(match) > 0):
			lastmatch = match[0][len(match[0])-1].replace('v/','')
		print "in youtube" + lastmatch[0]
		vidlink=lastmatch
		playtype="youtube"
	else:
		sources = []
		label=name
		hosted_media = urlresolver.HostedMediaFile(url=newlink, title=label)
		try:
			sources.append(hosted_media)
		except: pass
		source = urlresolver.choose_source(sources)
		print "inresolver=" + newlink
		vidlink = ""
		if source:
			try:
				vidlink = source.resolve()
			except: pass

	playVideo(playtype,vidlink)

##############################################
def OtherContent():
	net = Net()
	response = net.http_GET('http://khmerportal.com/videos')
	print response

##############################################
def extractFlashVars(data):
	for line in data.split("\n"):
		index = line.find("ytplayer.config =")
		if index != -1:
			found = True
			p1 = line.find("=", (index-3))
			p2 = line.rfind(";")
			if p1 <= 0 or p2 <= 0:
					continue
			data = line[p1 + 1:p2]
			break
	if found:
		data=data.split(";(function()",1)[0]
		data=data.split(";ytplayer.load",1)[0]
		data = json.loads(data)
		flashvars = data["args"]
	return flashvars

##############################################
def selectVideoQuality(links):
	link = links.get
	video_url = ""
	fmt_value = {
		5: "240p h263 flv container",
		18: "360p h264 mp4 container | 270 for rtmpe?",
		22: "720p h264 mp4 container",
		26: "???",
		33: "???",
		34: "360p h264 flv container",
		35: "480p h264 flv container",
		37: "1080p h264 mp4 container",
		38: "720p vp8 webm container",
		43: "360p h264 flv container",
		44: "480p vp8 webm container",
		45: "720p vp8 webm container",
		46: "520p vp8 webm stereo",
		59: "480 for rtmpe",
		78: "seems to be around 400 for rtmpe",
		82: "360p h264 stereo",
		83: "240p h264 stereo",
		84: "720p h264 stereo",
		85: "520p h264 stereo",
		100: "360p vp8 webm stereo",
		101: "480p vp8 webm stereo",
		102: "720p vp8 webm stereo",
		120: "hd720",
		121: "hd1080"
	}
	hd_quality = 1

	# SD videos are default, but we go for the highest res
	#print video_url
	if (link(35)):
		video_url = link(35)
	elif (link(59)):
		video_url = link(59)
	elif link(44):
		video_url = link(44)
	elif (link(78)):
		video_url = link(78)
	elif (link(34)):
		video_url = link(34)
	elif (link(43)):
		video_url = link(43)
	elif (link(26)):
		video_url = link(26)
	elif (link(18)):
		video_url = link(18)
	elif (link(33)):
		video_url = link(33)
	elif (link(5)):
		video_url = link(5)

	if hd_quality > 1:  # <-- 720p
		if (link(22)):
			video_url = link(22)
		elif (link(45)):
			video_url = link(45)
		elif link(120):
			video_url = link(120)
	if hd_quality > 2:
		if (link(37)):
			video_url = link(37)
		elif link(121):
			video_url = link(121)

	if link(38) and False:
		video_url = link(38)
	for fmt_key in links.iterkeys():

		if link(int(fmt_key)):
			text = repr(fmt_key) + " - "
			if fmt_key in fmt_value:
				text += fmt_value[fmt_key]
			else:
				text += "Unknown"

			if (link(int(fmt_key)) == video_url):
				text += "*"
		else:
			print "- Missing fmt_value: " + repr(fmt_key)

	video_url += " | " + 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'


	return video_url

##############################################
def getYoutube(videoid):
	code = videoid
	linkImage = 'http://i.ytimg.com/vi/'+code+'/default.jpg'
	req = urllib2.Request('http://www.youtube.com/watch?v='+code+'&fmt=18')
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()

	if len(re.compile('shortlink" href="http://youtu.be/(.+?)"').findall(link)) == 0:
		if len(re.compile('\'VIDEO_ID\': "(.+?)"').findall(link)) == 0:
			req = urllib2.Request('http://www.youtube.com/get_video_info?video_id='+code+'&asv=3&el=detailpage&hl=en_US')
			req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
			response = urllib2.urlopen(req)
			link=response.read()
			response.close()

	flashvars = extractFlashVars(link)

	links = {}

	for url_desc in flashvars[u"url_encoded_fmt_stream_map"].split(u","):
		url_desc_map = cgi.parse_qs(url_desc)
		if not (url_desc_map.has_key(u"url") or url_desc_map.has_key(u"stream")):
			continue

		key = int(url_desc_map[u"itag"][0])
		url = u""
		if url_desc_map.has_key(u"url"):
			url = urllib.unquote(url_desc_map[u"url"][0])
		elif url_desc_map.has_key(u"stream"):
			url = urllib.unquote(url_desc_map[u"stream"][0])

		if url_desc_map.has_key(u"sig"):
			url = url + u"&signature=" + url_desc_map[u"sig"][0]
		links[key] = url
	highResoVid=selectVideoQuality(links)
	return highResoVid

##############################################
def parseDate(dateString):
	try:
		return datetime.datetime.fromtimestamp(time.mktime(time.strptime(dateString.encode('utf-8', 'replace'), "%Y-%m-%d %H:%M:%S")))
	except:
		return datetime.datetime.today() - datetime.timedelta(days = 1) #force update

##############################################
def checkGA():
	secsInHour = 60 * 60
	threshold  = 2 * secsInHour

	now   = datetime.datetime.today()
	prev  = parseDate(ADDON.getSetting('ga_time'))
	delta = now - prev
	nDays = delta.days
	nSecs = delta.seconds

	doUpdate = (nDays > 0) or (nSecs > threshold)
	if not doUpdate:
		return

	ADDON.setSetting('ga_time', str(now).split('.')[0])
	APP_LAUNCH()


def send_request_to_google_analytics(utm_url):
	ua='Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
	import urllib2
	try:
		req = urllib2.Request(utm_url, None, {'User-Agent':ua} )
		response = urllib2.urlopen(req).read()
	except:
		print ("GA fail: %s" % utm_url)
	return response

##############################################
def GA(group,name):
	try:
		try:
			from hashlib import md5
		except:
			from md5 import md5
		from random import randint
		import time
		from urllib import unquote, quote
		from os import environ
		from hashlib import sha1
		VISITOR = ADDON.getSetting('ga_visitor')
		utm_gif_location = "http://www.google-analytics.com/__utm.gif"
		if not group=="None":
			utm_track = utm_gif_location + "?" + \
					"utmwv=" + VERSION + \
					"&utmn=" + str(randint(0, 0x7fffffff)) + \
					"&utmt=" + "event" + \
					"&utme="+ quote("5("+PATH+"*"+group+"*"+name+")")+\
					"&utmp=" + quote(PATH) + \
					"&utmac=" + UATRACK + \
					"&utmcc=__utma=%s" % ".".join(["1", VISITOR, VISITOR, VISITOR,VISITOR,"2"])
			try:
				print "============================ POSTING TRACK EVENT ============================"
				send_request_to_google_analytics(utm_track)
			except:
				print "============================  CANNOT POST TRACK EVENT ============================"
		if name=="None":
			utm_url = utm_gif_location + "?" + \
					"utmwv=" + VERSION + \
					"&utmn=" + str(randint(0, 0x7fffffff)) + \
					"&utmp=" + quote(PATH) + \
					"&utmac=" + UATRACK + \
					"&utmcc=__utma=%s" % ".".join(["1", VISITOR, VISITOR, VISITOR, VISITOR,"2"])
		else:
			if group=="None":
				utm_url = utm_gif_location + "?" + \
					"utmwv=" + VERSION + \
					"&utmn=" + str(randint(0, 0x7fffffff)) + \
					"&utmp=" + quote(PATH+"/"+name) + \
					"&utmac=" + UATRACK + \
					"&utmcc=__utma=%s" % ".".join(["1", VISITOR, VISITOR, VISITOR, VISITOR,"2"])
			else:
				utm_url = utm_gif_location + "?" + \
						"utmwv=" + VERSION + \
						"&utmn=" + str(randint(0, 0x7fffffff)) + \
						"&utmp=" + quote(PATH+"/"+group+"/"+name) + \
						"&utmac=" + UATRACK + \
						"&utmcc=__utma=%s" % ".".join(["1", VISITOR, VISITOR, VISITOR, VISITOR,"2"])

		print "============================ POSTING ANALYTICS ============================"
		send_request_to_google_analytics(utm_url)

	except:
		print "================  CANNOT POST TO ANALYTICS  ================"

##############################################
def APP_LAUNCH():
	versionNumber = int(xbmc.getInfoLabel("System.BuildVersion" )[0:2])
	if versionNumber > 13:
		logname="kodi.log"
	else:
		logname="xbmc.log"
	if versionNumber < 12:
		if xbmc.getCondVisibility('system.platform.osx'):
			if xbmc.getCondVisibility('system.platform.atv2'):
				log_path = '/var/mobile/Library/Preferences'
			else:
				log_path = os.path.join(os.path.expanduser('~'), 'Library/Logs')
		elif xbmc.getCondVisibility('system.platform.ios'):
			log_path = '/var/mobile/Library/Preferences'
		elif xbmc.getCondVisibility('system.platform.windows'):
			log_path = xbmc.translatePath('special://home')
			log = os.path.join(log_path, logname)
			logfile = open(log, 'r').read()
		elif xbmc.getCondVisibility('system.platform.linux'):
			log_path = xbmc.translatePath('special://home/temp')
		else:
			log_path = xbmc.translatePath('special://logpath')
		log = os.path.join(log_path, logname)
		logfile = open(log, 'r').read()
		match=re.compile('Starting XBMC \((.+?) Git:.+?Platform: (.+?)\. Built.+?').findall(logfile)
	elif versionNumber > 11:
		print '======================= more than ===================='
		log_path = xbmc.translatePath('special://logpath')
		log = os.path.join(log_path, logname)
		logfile = open(log, 'r').read()
		match=re.compile('Starting XBMC \((.+?) Git:.+?Platform: (.+?)\. Built.+?').findall(logfile)
	else:
		logfile='Starting XBMC (Unknown Git:.+?Platform: Unknown. Built.+?'
		match=re.compile('Starting XBMC \((.+?) Git:.+?Platform: (.+?)\. Built.+?').findall(logfile)
	print '==========================   '+PATH+' '+VERSION+'  =========================='
	try:
		from hashlib import md5
	except:
		from md5 import md5
	from random import randint
	import time
	from urllib import unquote, quote
	from os import environ
	from hashlib import sha1
	import platform
	VISITOR = ADDON.getSetting('ga_visitor')
	for build, PLATFORM in match:
		if re.search('12',build[0:2],re.IGNORECASE):
			build="Frodo"
		if re.search('11',build[0:2],re.IGNORECASE):
			build="Eden"
		if re.search('13',build[0:2],re.IGNORECASE):
			build="Gotham"
		print build
		print PLATFORM
		utm_gif_location = "http://www.google-analytics.com/__utm.gif"
		utm_track = utm_gif_location + "?" + \
			"utmwv=" + VERSION + \
			"&utmn=" + str(randint(0, 0x7fffffff)) + \
			"&utmt=" + "event" + \
			"&utme="+ quote("5(APP LAUNCH*"+build+"*"+PLATFORM+")")+\
			"&utmp=" + quote(PATH) + \
			"&utmac=" + UATRACK + \
			"&utmcc=__utma=%s" % ".".join(["1", VISITOR, VISITOR, VISITOR,VISITOR,"2"])
		try:
			print "============================ POSTING APP LAUNCH TRACK EVENT ============================"
			send_request_to_google_analytics(utm_track)
		except:
			print "============================  CANNOT POST APP LAUNCH TRACK EVENT ============================"

checkGA()

##############################################
def addLink(name,url,mode,iconimage,selected=False):
	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&series="+urllib.quote_plus(name)
	ok=True
	liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
	liz.setInfo( type="Video", infoLabels={ "Title": name } )
	liz.select(selected)
	contextMenuItems = []
	liz.addContextMenuItems(contextMenuItems, replaceItems=True)
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
	return ok

##############################################
def addNext(formvar,url,mode,iconimage):
	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&formvar="+str(formvar)+"&name="+urllib.quote_plus('Next >')
	ok=True
	liz=xbmcgui.ListItem('Next >', iconImage="DefaultVideo.png", thumbnailImage=iconimage)
	liz.setInfo( type="Video", infoLabels={ "Title": 'Next >' } )
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
	return ok

##############################################
def addDir(name,url,mode,iconimage,info=None,selected=False):
	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&series="+urllib.quote_plus(name)
	ok=True
	liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
	liz.select(selected)
	data = {
		"Title": name,
		"mediatype":"episode",
	}
	if info != None:
		if info[1] > 0:
			data['episode'] = info[1]
		if info[2] != '':
			data['plot'] = info[2]
		if info[3] != '':
			liz.setCast( json.loads(info[3]) )
		if info[4] != '':
			data['country'] = info[4]
		if info[5] != '':
			data['status'] = info[5]
		if info[6] > 0:
			data['aired'] = info[6].split(" ")[0]
		#row.append(vimg)	#  7 = Image URL
		if info[8] != '':
			try:
				data['imdbnumber'] = info[8].split('/title/')[1][:-1]
			except: pass
		#row.append(0)		# 10 = Episodes count
		if info[11] != '':
			data['title'] = info[11]
		if info[12] != '':
			data['genre'] = info[12].split(" ")
	liz.setInfo( type="Video", infoLabels=data )
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
	return ok

##############################################
def get_params():
	param=[]
	paramstring=sys.argv[2]
	if len(paramstring)>=2:
		params=sys.argv[2]
		cleanedparams=params.replace('?','')
		if (params[len(params)-1]=='/'):
			params=params[0:len(params)-2]
		pairsofparams=cleanedparams.split('&')
		param={}
		for i in range(len(pairsofparams)):
			splitparams={}
			splitparams=pairsofparams[i].split('=')
			if (len(splitparams))==2:
				param[splitparams[0]]=splitparams[1]
	return param

##############################################
def List_Genres(url):
	link = GetContent(url)
	if link == None:
		return
	try:
		link =link.encode("UTF-8")
	except: pass
	newline = link
	try:
		newlink = ''.join(link.splitlines())
	except: pass
	newline = newline.replace('\t','')
	soup = BeautifulSoup(newlink)
	menucontent=soup.findAll('ul', {"class" : "switch-block list-episode-item-2"})
	if len(menucontent) > 0:
		for item in menucontent[0].findAll('li'):
			#print item
			try:
				vname=item.h3.contents[0]
				vname=vname.strip()
				vurl=strdomain+item.a["href"]
				addDir(vname.encode('utf-8', 'ignore'),vurl,14,"")
			except: pass

##############################################
def List_Stars(url):
	link = GetContent(url)
	if link == None:
		return
	try:
		link =link.encode("UTF-8")
	except: pass
	newline = link
	try:
		newlink = ''.join(link.splitlines())
	except: pass
	newline = newline.replace('\t','')
	soup = BeautifulSoup(newlink)
	menucontent=soup.findAll('ul', {"class" : "list-star"})
	if len(menucontent) > 0:
		for item in menucontent[0].findAll('li'):
			#print item
			try:
				vname=item.h3.text
				vname=vname.strip().encode('utf-8', 'ignore')
				vurl=strdomain+item.a["href"]
				vimg=item.a.img["data-original"]
				#addDir(vname,vurl,14,vimg)
				addDir(vname,vurl,16,vimg)
			except: pass
		pagingList=soup.findAll('ul', {"class" : "pagination"})
		if(len(pagingList) >0):
			for item in pagingList[0].findAll('li'):
				vname="Page "+ item.a.text.strip()
				vurl=url.split('?')[0]+item.a["href"]
				addDir(vname.encode('utf-8', 'ignore'),vurl,15,"")

##############################################
def List_Stars_In(url):
	#return
	link = GetContent(url)
	if link == None:
		return
	try:
		link =link.encode("UTF-8")
	except: pass
	newline = link
	try:
		newlink = ''.join(link.splitlines())
	except: pass
	newline = newline.replace('\t','')
	soup = BeautifulSoup(newlink)
	menucontent=soup.findAll('ul', {"class" : "list-episode-item"})
	if len(menucontent) > 0:
		for item in menucontent[0].findAll('li'):
			#print item
			vname=item.a.img["alt"].strip()
			vurl=strdomain+item.a["href"]
			vimg=item.a.img["data-original"]
			addDir(vname.encode('utf-8', 'ignore'),vurl,5,vimg)
	pagingList=soup.findAll('ul', {"class" : "pagination"})
	if(len(pagingList) >0):
		for item in pagingList[0].findAll('li'):
			#print item
			vname="Page "+ item.a["data-page"].strip()
			vurl=url+item.a["href"]
			if(item.has_key("class")==False):
				addDir(vname.encode('utf-8', 'ignore'),vurl,6,"")

##############################################
def Search_for_Stars():
	try:
		keyb = xbmc.Keyboard('', 'Enter search text')
		keyb.doModal()
		#searchText = '01'
		if (keyb.isConfirmed()):
				searchText = urllib.quote_plus(keyb.getText())
		url = strdomain+'/search?type=stars&keyword='+searchText
		List_Stars_In(url)
	except: pass

##############################################
def setLastPlayed(url, series):
	series = ExtractAlphanumeric(series.strip())
	if series == None or series == "":
		return
	pos=series.rfind(": Episode ")
	if pos > 0:
		vepisode=series[pos+2:]
		series=series[0:pos]
	con1.cursor().execute('INSERT OR REPLACE INTO recent (series, episode, last_url, last_visit) VALUES (?,?,?,?)', ( series, vepisode, url, int(time.time()) ))
	con1.commit()

##############################################
def getLastPlayed(series):
	series = ExtractAlphanumeric(series.strip())
	cur=con1.cursor()
	cur.execute("SELECT episode FROM recent WHERE series=? LIMIT 1", [series])
	for row in cur:
		return row[0]
	return None

##############################################
def Recently_Viewed():
	cur=con1.cursor()
	cur.execute("SELECT series, last_url FROM recent ORDER BY last_visit DESC")
	for item in cur:
		vname=item[0].strip()
		vurl=item[1]
		info = Drama_Overview(vname, vurl)
		vimg = info[7]
		addDir(vname.encode('utf-8', 'ignore'),vurl,5,vimg,info=info)

##############################################
def ExtractAlphanumeric(str):
    return re.sub('[^A-Za-z0-9\s\(\)\:]+', '', str)

##############################################
def Drama_Overview(series, url='', vimg='', default=None, cancelled=False):
	# Strip episode number out of the series name:
	try:
		episode = series.split(': Episode ')[1]
	except:
		episode = 0

	# Strip the season number out of the series name:
	try:
		parts = series.split(" Season ")
		season = parts[1]
		search = parts[0]
	except:
		season = 1
		search = series

	# Get the series information from the database:
	series = ExtractAlphanumeric(series)
	cur=con2.cursor()
	cur.execute('SELECT series, episode, plot, dcast, country, status, released, img, imdb, reload, total, title, genre FROM dramas WHERE series=? AND episode=?', (series,episode))
	rows = cur.fetchall()
	if len(rows) > 0:
		# If no reload required, return the row:
		row = list(rows[0])
		if row[9] == 0:
			return row
		row[0] = 0
	else:
		# Set up the database row using provided row, or default settings:
		if default == None:
			row = list()
			row.append(series)	#  0 = Series
			row.append(0)		#  1 = Episode
			row.append('')		#  2 = Plot
			row.append('[]')	#  3 = Drama Cast
			row.append('')		#  4 = Country
			row.append('')		#  5 = Status
			row.append('')		#  6 = Released
			row.append(vimg)	#  7 = Image URL
			row.append('')		#  8 = IMDB link
			row.append(0)		#  9 = Reload flag (1 = force reloading drama info)
			row.append(0)		# 10 = Episodes count
			row.append(series)	# 11 = Episode title
			row.append('')		# 12 = Genre
		else:
			row = list(default)

	# If we are asking about a particular episode, return at this point:
	if episode > 0:
		if default != None:
			row[3] = default[3]
		return row
	if cancelled:
		return row

	# Make sure we are using a URL for the drama details, not an episode:
	parts = url.split("-episode-")
	if len(parts) > 1:
		pos = parts[0].rfind('/')
		url = url[0:pos] + "/drama-detail/" + parts[0][pos+1:]
		#xbmcgui.Dialog().ok('Drama_Overview',url)

	# Get the drama information from the website:
	link = GetContent(url, False)
	if link == None:
		return row
	try:
		link =link.encode('UTF-8')
	except: pass
	newline = link
	try:
		newlink = ''.join(link.splitlines())
	except: pass
	newline = newline.replace('\t','')
	soup = BeautifulSoup(newlink)
	menucontent=soup.findAll('div', {'class' : 'info'})
	if len(menucontent) > 0:
		items = menucontent[0].findAll('p')

		# Item description:
		i = 0
		if  items[1].text == 'Description:':
			i = 1
		row[2] = items[1+i].text
		#xbmcgui.Dialog().ok('Drama_Overview','Plot',row[2])

		# Drama Country
		row[4] = items[2+i].text.split(':')[-1]
		#xbmcgui.Dialog().ok('Drama_Overview','Country',row[4])

		# Drama Status
		row[5] = items[3+i].text.split(':')[-1]
		#xbmcgui.Dialog().ok('Drama_Overview','Status',row[5])

		# Drama Genre
		row[12] = items[5+i].text.split(':')[-1]
		#xbmcgui.Dialog().ok('Drama_Overview','Genre',row[12])

	# Get first release date:
	row[10] = 0
	menucontent=soup.findAll('div', {'class' : 'block tab-container'})
	if len(menucontent) > 0:
		for item in menucontent[0].findAll('span', {'class' : 'time'}):
			row[10] += 1
			test = item.text.split(" ")[0]
			if row[6] == "" or row[6] > test:
				row[6] = test
			#xbmcgui.Dialog().ok('Drama_Overview','First Released',row[6])

	# Gather the cast together into an array:
	row[3] = []
	menucontent=soup.findAll('div', {'class' : 'slider-star'})
	if len(menucontent) > 0:
		for item in menucontent[0].findAll('div', {'class' : 'item'}):
			sname = item.text.split("(")[0].strip()
			#xbmcgui.Dialog().ok('Drama_Overview','Star Name',sname)
			simg = item.img["src"]
			#xbmcgui.Dialog().ok('Drama_Overview','Star Image URL',simg)
			star = {"name":sname, "thumbnail":simg}
			row[3].append(star)

	# Store cast as JSON string:
	row[3] = json.dumps(row[3])
	#xbmcgui.Dialog().ok('Drama_Overview','Cast JSON string',row[3])

	# Get the IMDB link from the website (if possible):
	if row[8] == '':
		try:
			link = GetContent('https://www.imdb.com/find?q='+urllib.quote_plus(search)+'&exact=true&ref_=nv_sr_sm', False)
		except:
			link = None
		if link != None:
			try:
				link =link.encode('UTF-8')
			except: pass
			newline = link
			try:
				newlink = ''.join(link.splitlines())
			except: pass
			newline = newline.replace('\t','')
			soup = BeautifulSoup(newlink)
			menucontent=soup.findAll('table', {'class' : 'findList'})
			if len(menucontent) > 0:
				row[8] = 'https://www.imdb.com'+menucontent[0].findAll('td', {'class': 'result_text'})[0].a['href'].split('?')[0]
				#xbmcgui.Dialog().ok('Drama_Overview','IMDB link: Try # 1',row[8])

	# Get the IMDB link from the website (if possible):
	if row[8] == '':
		try:
			link = GetContent('https://www.imdb.com/find?q='+urllib.quote_plus(search)+'&ref_=nv_sr_sm', False)
		except:
			link = None
		if link != None:
			try:
				link =link.encode('UTF-8')
			except: pass
			newline = link
			try:
				newlink = ''.join(link.splitlines())
			except: pass
			newline = newline.replace('\t','')
			soup = BeautifulSoup(newlink)
			menucontent=soup.findAll('table', {'class' : 'findList'})
			if len(menucontent) > 0:
				row[8] = 'https://www.imdb.com'+menucontent[0].findAll('td', {'class': 'result_text'})[0].a['href'].split('?')[0]
				#xbmcgui.Dialog().ok('Drama_Overview','IMDB link: Try # 2',row[8])

	# If no description is provided at this point, see if IMDB.com has a description that we can use:
	if row[2] == "" and row[8] != "":
		link = GetContent(row[8], False)
		if link != None:
			try:
				link =link.encode('UTF-8')
			except: pass
			newline = link
			try:
				newlink = ''.join(link.splitlines())
			except: pass
			newline = newline.replace('\t','')
			soup = BeautifulSoup(newlink)
			menucontent=soup.findAll('div', {'class' : 'summary_text'})
			if len(menucontent) > 0:
				row[2] = menucontent[0].text
				#xbmcgui.Dialog().ok('Drama_Overview','Plot',row[2])

	# Insert the drama information into the database:
	con2.cursor().execute('INSERT OR REPLACE INTO dramas (series, episode, plot, dcast, country, status, released, img, imdb, reload, total, title, genre) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)', row)
	con2.commit()

	# If only one episode and statis is completed, skip the rest!  Otherwise, gather episode information:
	if row[10] == 1 and row[5] == 'Completed':
		return row
	default = list(row)
	row[3] = '[]'
	row[2] = ''

	# Get the episode information from IMDB.com:
	try:
		link = GetContent(row[8]+'episodes?season='+str(season)+'&ref_=tt_eps_sn_'+str(season), False)
	except:
		link = None
	if link == None:
		return default
	row[9] = 0
	row2 = list(row)

	try:
		link =link.encode('UTF-8')
	except: pass
	newline = link
	try:
		newlink = ''.join(link.splitlines())
	except: pass
	newline = newline.replace('\t','')
	soup = BeautifulSoup(newlink)

	# Start by getting the links to the episode screenshots:
	default = list(row2)
	menucontent=soup.findAll('div', {'class':re.compile('list_item *')})
	if len(menucontent) > 0:
		for item in menucontent:
			# Make copy of the original row, in case stuff can't be found:
			row = list(row2)

			# Episode number:
			vimg = item.findAll('div', {'class': 'image'})[0]
			row[1] = vimg.text.split(',')[-1].replace('Ep','').strip()
			row[0] = row[0] + ': Episode ' + str(row[1])
			#xbmcgui.Dialog().ok('Drama_Overview','Episode Number', row[1])

			# Episode description:
			try:
				row[2] = desc[0].findAll('div', {'class': 'item_description'})[0].text
			except:
				row[2] = ''
			if row[2].find("Know what this is about?") > -1:
				row[2] = ''
			#xbmcgui.Dialog().ok('Drama_Overview','Episode ' + str(row[1]) + ' Plot', row[2])

			# Episode release date:
			row[11] = vimg.a['title']
			if row[11].find("Episode #") == -1:
				row[11] = "Episode " + str(row[1]) + ": " + row[11]
			else:
				row[11] = row[0]
			#xbmcgui.Dialog().ok('Drama_Overview','Episode ' + str(row[1]) + ' Title', row[10])

			# Image URL:
			try:
				row[7] = vimg.img['src']
			except:
				row[7] = row2[7]
			#xbmcgui.Dialog().ok('Drama_Overview','Episode ' + str(row[1]) + ' Image URL', row[7])

			# Save it to the database:
			con2.cursor().execute('INSERT OR REPLACE INTO dramas (series, episode, plot, dcast, country, status, released, img, imdb, reload, total, title, genre) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)', row)

	# Commit all changes to the database:
	con2.commit()
	return row

##############################################
def Refresh_Database(url):
	c = 0
	for character in AZ_DIRECTORIES:
		if INDEX(url.replace('#',character), c):
			return
		c += 1

##############################################
def Remove_Series(series):
	con1.cursor().execute("DELETE FROM recent WHERE series=?", [series])
	con1.commit()
	xbmcgui.Dialog().ok('DramaCool','Series "'+series+'" has been removed from the recently viewed page.  Go back to the main page of the DramaCool app and select "Recently Viewed" to see the updated page.')

##############################################
progress_bar = xbmcgui.DialogProgress()
def reporthook(block_number, block_size, total_size):
	if 0 == block_number & 511:
	     percent = (block_number * block_size * 100) / total_size
	     progress_bar.update(percent)

def Download_DB(dest):
	progress_bar.create('DramaCool', 'Downloading prebuilt Drama Database!')
	urllib.urlretrieve("http://www.dropbox.com/s/db1f70vloyy69nf/dramas.db?dl=1", dest, reporthook)
	progress_bar.close()

##############################################
# Make sure that the plugin userdata folder exists:
path=os.path.join(xbmc.translatePath('special://home'), 'userdata', 'addon_data', 'plugin.video.DramaCool')
if not os.path.isdir(path):
	os.mkdir(path)

# Define the recent database:
con1 = dbapi2.connect(os.path.join(path, 'recent.db'))
con1.cursor().execute("CREATE TABLE IF NOT EXISTS recent (series TEXT UNIQUE, episode TEXT, last_url TEXT, last_visit INTEGER)")

# If dramas database doesn't exist, prompt to download it.  If failed, create the database:
name = os.path.join(path, 'dramas.db')
if not os.path.isfile(name):
	Download_DB(name)
con2 = dbapi2.connect(name)
con2.cursor().execute("CREATE TABLE IF NOT EXISTS dramas (series TEXT UNIQUE, episode INTEGER, plot TEXT, dcast TEXT, country TEXT, status TEXT, released INTEGER, img TEXT, imdb TEXT, reload INTEGER, total INTEGER, title TEXT, genre TEXT)")

# Get parameters passed to script:
params=get_params()
try:
	url=urllib.unquote_plus(params["url"])
except:
	url=None
try:
	series=urllib.unquote_plus(params["series"])
except:
	series=None
try:
	name=urllib.unquote_plus(params["name"])
except:
	name=None
try:
	mode=int(params["mode"])
except:
	mode=None
try:
	formvar=int(params["formvar"])
except:
	formvar=None

#url='http://www.khmeraccess.com/video/viewvideo/6604/31end.html'
sysarg=str(sys.argv[1])
xbmcplugin.setContent(int(sys.argv[1]), "video")
if mode==None or url==None or len(url)<1:
	#OtherContent()
	HOME()
elif mode==2:
	#xbmcgui.Dialog().ok('mode 2',str(url),' ingore errors lol')
	GA("INDEX",name)
	INDEX(url)
elif mode==3:
	#sysarg="-1"
	ListAZ(strdomain+"/drama-list/char-start-#.html",2)
elif mode==4:
	#SEARCH()
	Download_DB(name)
elif mode==5:
	GA("episode",name)
	Episodes(url,name)
elif mode==6:
	IndexLatest(url)
elif mode==7:
	ListSource(url,series)
elif mode==8:
	loadVideos(url,name)
elif mode==9:
	Index_co(url)
elif mode==10:
	Episodes_co(url,name)
elif mode==11:
	ListSource_co(url,series)
elif mode==12:
	GetMenu(url,url)
elif mode==13:
	List_Genres(url)
elif mode==14:
	IndexLatest(url,False)
elif mode==15:
	List_Stars(url)
elif mode==16:
	List_Stars_In(url)
elif mode==17:
	Search_for_Stars()
elif mode==18:
	Recently_Viewed()
elif mode==19:
	Refresh_Database(strdomain+"/drama-list/char-start-#.html")
elif mode==20:
	Remove_Series(url)

xbmcplugin.endOfDirectory(int(sysarg))
con1.close()
con2.commit()
con2.close()