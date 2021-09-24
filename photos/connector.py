from photos.views import *


class ConnectorClass:

    def __init__(self, session, user_url):
        self.__album = PhotosAlbum(session, user_url)
        self.__album.download_album()