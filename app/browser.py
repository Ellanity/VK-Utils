# Class consist of session, url. Performs the role of a navigator between apps
import photos.connector
# import video.navigator


class AppBrowser:

    def __init__(self, session):
        self.__session = session
        self.BROWSER = {
            "photos": photos.connector.ConnectorClass,
            "*": AppBrowser.NotRightUrlException,
            # "video": video.navigator.NavigatorClass
        }

    class NotRightUrlException(Exception):
        def __init__(self, session, user_url):
            print("The link was not defined")

    def download(self, user_url):
        url_type = self.define_type_of_url(user_url)
        self.BROWSER[url_type](self.__session, user_url)

    def define_type_of_url(self, user_url):
        if user_url[:20] == "https://vk.com/album":
            return "photos"
        else:
            return "*"
