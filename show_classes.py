import bs4 as BeautifulSoup

# target classes where information is stored
div_dict = {'host': 'gs-u-display-block',
            'title': 'sc-c-marquee--non-touch sc-c-marquee sc-c-herospace__details-titles-secondary',
            'date_aired': 'gel-pica gs-u-display-inline@s sc-c-episode__metadata__data',
            'details': 'sc-c-synopsis gel-1/1 gs-u-box-size gs-u-pr+'
}

class Song():
    def __init__(self, artist, title):
        self.artist = artist
        self.title = title
    
    def __str__(self):
        return f'{self.artist} - {self.title}'
    
class Show():
    def __init__(self, html_page):
        self.html_page = html_page

    def get_track_list(self):
        songs = self.html_page.find_all('div', class_ = 'sc-u-flex-grow sc-c-basic-tile__text')
        song_list = [song.get('title').split('-') for song in songs]
        self.track_list = [Song(song[0].strip(), song[1].strip()) for song in song_list]
    
    def access_metadata(self):
        meta_dict = {}
        for key, value in div_dict.items():
            div_element = self.html_page.find("div", class_=value)
            if div_element:
                if key == 'title':
                    meta_dict[key] = div_element.find("span").text
                    self.title = meta_dict[key]
                elif key == 'date_aired':
                    meta_dict[key] = div_element.text.split(':')[-1].strip()
                    self.date_aired = meta_dict[key]
                elif key == 'details':
                    meta_dict[key] = div_element.text.split('Read more')[0].strip()
                    self.details = meta_dict[key]
                else:
                    meta_dict[key] = div_element.text
                    self.host = meta_dict[key]
        self.show_metadata = meta_dict

    def __repr__(self):
        return f'{self.show_metadata["host"]} - {self.show_metadata["title"]} - {self.show_metadata["date_aired"]}'
    