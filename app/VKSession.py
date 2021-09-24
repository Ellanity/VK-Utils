import vk_api
# import requests
import os
import io
from PIL import Image


class VKSessionClass:

    def __init__(self, login, password):
        try:
            # session = requests.Session()
            vk_session = vk_api.VkApi(login, password, captcha_handler=captcha_handler)
            try:
                # Open vk session
                vk_session.auth(token_only=True)
            except vk_api.AuthError as error_msg:
                print(error_msg)
                exit()

            vk = vk_session.get_api()

            # Delete system files
            if os.path.exists('vk_config.v2.json'):
                os.remove('vk_config.v2.json')

            self.__session = vk
        except:
            print("Unable to log in to the VK")
            self.__session = None

    def get_session(self):
        return self.__session


def captcha_handler(captcha):
    # Enter captcha if it is needed
    # print(captcha.__dict__)
    # sid = captcha.sid
    print("[Need to enter a captcha]")
    print("Code from img {}: ".format(str(captcha.get_url())))
    # Make image from bytes and open it
    image = Image.open(io.BytesIO(captcha.get_image()))
    image.show()
    code = input()
    # Try log in once more
    return captcha.try_again(code)
