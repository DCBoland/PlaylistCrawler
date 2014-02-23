from scrapy.spider import Spider
from scrapy.selector import Selector
from playlists.items import Playlist, Track
from scrapy.http import Request, Response
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

class LastFMCrawler(Spider):
    name = "lastfm"
    allowed_domains = ["last.fm","audioscrobbler.com"]
    start_urls = ["http://www.last.fm/community/users/active"]
    
    def __init__(self, apikey=None, *args, **kwargs):
        super(LastFMCrawler, self).__init__(*args, **kwargs)
        self.apikey = apikey
    
    def parse(self, response):        
        sel = Selector(response)
        
        # We already got the first page, so yield playlists & tracks from it
        # In python3 this would be the nicer 'yield from..'
        for item in self.parseUserList(response):
            yield item
            
        for i in range(1,20):
            URL = 'http://www.last.fm/community/users/active?page=' + str(i)
            yield Request(URL, self.parseUserList)    
        
    def parseUserList(self, response):
        sel = Selector(response)
        users = sel.css('.vcard strong a::text').extract()
        
        for user in users:
            for item in self.grabPlaylists(user[1:]):
                yield item
            
    def grabPlaylists(self, user):
        URL = 'http://ws.audioscrobbler.com/2.0/?method=user.getPlaylists&user=' + user + '&api_key=' + self.apikey
        yield Request(URL, self.parsePlaylistsXML)
        
    def parsePlaylistsXML(self, response):
        sel = Selector(response)
        user = sel.xpath('playlists/@user')[0].extract()
        playlists = sel.xpath('//playlist')
        for playlist in playlists:
            size = int(playlist.xpath('size/text()')[0].extract())
            if size > 10:
                pl = Playlist()
                pl['url'] = playlist.xpath('url/text()')[0].extract()
                pl['name'] = playlist.xpath('title/text()')[0].extract()
                pl['user'] = user
                pl['foreignid'] = playlist.xpath('id/text()')[0].extract()
                pl['duration'] = playlist.xpath('duration/text()')[0].extract()
                pl['tracks'] = []
                yield Request(pl['url'],self.parsePlaylist,meta={'playlist': pl})
                
    def parsePlaylist(self, response):
        sel = Selector(response)
        
        pl = response.meta['playlist']
        #pl['name'] = sel.css('#playlistTitle::text')[0].extract()
        
        tracks = sel.css('tbody > tr')
        for t in tracks:
            track = Track()
            spotifyid = t.css('.spotify-inline-play-button::attr(data-uri)')
            if not spotifyid:
                # Hard to analyse features without audio!
                continue
            
            track['foreignid'] = spotifyid[0].extract()
            #track['artist'], track['name'] = t.css('.track > a::text').extract()
            
            # TODO: convert duration from string
            #duration = t.css('.duration::text')
            #if duration:
            #    track['duration'] = duration[0].extract()
            pl['tracks'].append(track['foreignid'])
            #yield track
        yield pl