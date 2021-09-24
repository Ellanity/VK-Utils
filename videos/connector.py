from videos.views import *


class ConnectorClass:

    def __init__(self, session, user_url):
        self.__album = VideosAlbum(session, user_url)
        self.__album.download_album()