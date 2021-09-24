# Add upper level to path
import sys

sys.path.append('../')

from app.browser import AppBrowser
from app.ConsoleArgumentsHandler import ConsoleArgumentsHandlerClass
from app.VKSession import VKSessionClass
import validators


def main():
    # Get login and password
    args = ConsoleArgumentsHandlerClass().get_args()

    # If have not all the necessary login data
    if not hasattr(args, "login") or not hasattr(args, "password"):
        print("The necessary login data is missing. Please check input and restart programm.")
        exit()

    # Get session
    vk = VKSessionClass(args.login, args.password).get_session()
    if vk is None:
        exit()

    # Download only one album and close program
    if hasattr(args, "url"):
        if args.url is not None:
            AppBrowser(vk).download(args.url)
            exit()

    # While user download albums open menu
    try:
        manual_file = open("manual.txt", "r")
        manual = manual_file.read()
        print(manual)
    except FileNotFoundError:
        print("[No manual]\n> /exit - to exit")

    # Downloading albums
    browser = AppBrowser(vk)
    while True:
        # try:
        user_url = input()
        # Check if it is one of the command [one of the urls]
        if user_url.lower() == "/exit":
            break
        # Check if it is web url
        valid = validators.url(user_url)
        if valid:
            browser.download(user_url)
        else:
            print("Unknown command")
        # except:
        #     print("An unexpected error occurred")
    exit()


if __name__ == '__main__':
    main()
