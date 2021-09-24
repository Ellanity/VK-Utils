import vk_api
import requests
import os


class VKSessionClass:

    def __init__(self, login, password):
        # Open vk session
        try:
            session = requests.Session()
            vk_session = vk_api.VkApi(login, password)
            try:
                vk_session.auth(token_only=True)
            except vk_api.AuthError as error_msg:
                print(error_msg)
                exit()
            vk = vk_session.get_api()

            if os.path.exists('vk_config.v2.json'):
                os.remove('vk_config.v2.json')

            self.__session = vk
        except:
            print("Unable to log in to the VK")
            self.__session = None

    def get_session(self):
        return self.__session
