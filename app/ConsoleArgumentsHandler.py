import argparse
import getpass
import json
import os.path


class ConsoleArgumentsHandlerClass:

    # Read args from terminal, save them to private variable
    def __init__(self):
        parser = argparse.ArgumentParser(description='Download albums from VK')

        # Flag read credentials from file
        parser.add_argument('-f', '--file', action='store_true', help="Login from file", default=False)
        # Flag read credentials from terminal
        parser.add_argument('-t', '--terminal', action='store_true', help="Login from terminal", default=True)
        parser.add_argument('-u', '--url', help="Url of album to download", type=str)

        args = parser.parse_args()
        self.__args = args
        self.define_credentials()

    # Return private args
    def get_args(self):
        return self.__args

    # Read credentials
    def define_credentials(self):
        if self.__args.file:
            try:
                self.define_credentials_file()
            except:
                print("Unable to get login data from file")
                self.define_credentials_terminal()
        else:
            self.define_credentials_terminal()

    # Read credentials from file
    def define_credentials_file(self):
        # Create file if it does not exists
        if not os.path.exists('credentials.json'):
            credential_file = open("credentials.json", "x")
            credential_file.close()

        # Open file, convert json to py dict
        credentials_json = open('credentials.json', 'r')
        credentials_text = credentials_json.read()
        credentials_dict = json.loads(credentials_text)
        # Fill variables
        self.__args.login = credentials_dict["login"]
        self.__args.password = credentials_dict["password"]
        # Close file
        credentials_json.close()

    # Read credentials from terminal
    def define_credentials_terminal(self):
        self.__args.login = input("Enter your login: ")
        self.__args.password = getpass.getpass("Enter password: ")
        self.update_credentials()

    # Update credentials in file
    def update_credentials(self):
        try:
            print("You can update login and password in file in order not to enter them every time[y/n]:")
            save_credentials = input().lower()
            if save_credentials == 'y':
                # Create file if it does not exists
                if not os.path.exists('credentials.json'):
                    credential_file = open("credentials.json", "x")
                    credential_file.close()
                # Json format for credentials
                credentials = {
                    "login": str(self.__args.login),
                    "password": str(self.__args.password)
                }
                credentials_json = open('credentials.json', 'w')
                credentials_json.write(str(json.dumps(credentials)))
                credentials_json.close()
        except:
            print("Unable to save login data")
