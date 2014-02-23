# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class Playlist(Item):
    # define the fields for your item here like:
    # name = Field()
    name = Field()
    user = Field()
    url = Field()
    duration = Field()
    foreignid = Field()
    tracks = Field()

class Track(Item):
    name = Field()
    foreignid = Field()
    artist = Field()
    duration = Field()