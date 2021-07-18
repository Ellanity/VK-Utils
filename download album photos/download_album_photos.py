import argparse
from vk_api.longpoll import VkLongPoll, VkEventType
import vk_api
import requests
import os, time, math
import getpass
import urllib.request


def parseArgs():
    
    parser = argparse.ArgumentParser(description='Videos to images')
    parser.add_argument('-v', action='store_true', help="Show some information while downloading", default=False)
    parser.add_argument('-vv', action='store_true', help="Show more information while downloading", default=False)
    parser.add_argument('-vvv', action='store_true', help="Show more than more information while downloading", default=False)
    
    args = parser.parse_args()
    
    args.login = input("Enter your login: ")
    args.password = getpass.getpass("Enter password: ")

    return args
    

def main():
    
    args = parseArgs()
    matches = []
    if args.vvv != False:
        args.vv == True
    if args.vv != False:
        args.v == True
    
    if args.password != None and args.login != None:

        # Open vk session
        session = requests.Session()
        vk_session = vk_api.VkApi(args.login, args.password)
        try:
            vk_session.auth(token_only=True)
        except vk_api.AuthError as error_msg:
            print(error_msg)
            exit()
        vk = vk_session.get_api()
        os.remove('vk_config.v2.json')
        print("Authorization was successful")
        
        args.album = input("Enter albums url: ")
        while args.album != None:
            # Get album info from url
            album_id_ = str(args.album.split('/')[-1].split('_')[1])
            owner_id_ = args.album.split('/')[-1].split('_')[0].replace('album', '')
            print("Owner id: " + owner_id_ + " album id: " + album_id_)
            if args.vv != False:
                print("Getting album:\n")
            
            if album_id_ != "0" and album_id_ != "00" and album_id_ != "000":
                try:
                    response = vk.photos.getAlbums(owner_id=owner_id_, album_ids=album_id_)['items']
                    
                    if args.vv != False:
                        print(response)
                    
                    if len(response) > 1:
                        raise AlbumError("No such album")
                    else:
                        photos_count = response[0]['size']
                        if args.vv != False:
                            print("Photos count: " + str(photos_count))
                except Exception:
                    print("No such album")
                    exit()
            
            elif album_id_ == "0":
                album_id_ = "profile"
            elif album_id_ == "00":
                album_id_ = "wall"
            elif album_id_ == "000":
                album_id_ = "saved"

            photos_count = 0
            
            if album_id_ == "profile" or album_id_ == "wall" or album_id_ == "saved":    
                response = vk.photos.get(owner_id=owner_id_, album_id=album_id_)
                photos_count = response['count']
                if args.vv != False:
                    print(str(response) + "\n")
                print("Photos count: " + str(photos_count))

            counter = 0 # of photo
            prog = 0 # percentage of downloads
            breaked = 0 # not downloaded due to an error
            time_now = time.time() # start time
            
            #Creating directories
            if not os.path.exists('saved'):
                os.mkdir('saved')
            photo_folder = 'saved/{0}_{1}'.format(owner_id_, album_id_)
            if not os.path.exists(photo_folder):
                os.mkdir(photo_folder)
            
            print("Start download:")
            # Let's calculate how many times you need to get a list of photos, since the number will not be an integer - we round it up
            for j in range(math.ceil(photos_count / 1000)): 
                
                #Getting a list of photos
                photos = vk.photos.get(owner_id=owner_id_, album_id=album_id_, count=1000, offset=j*1000)
                for photo in photos['items']:
                    
                    counter += 1
                    prog = round(100/photos_count*counter,2)
                    
                    #Getting the address of the image with the largest number of pixels
                    biggest = photo['sizes'][0]
                    for size in photo['sizes']:
                        if size['width'] >= biggest['width']:
                            biggest = size
                    
                    url = biggest['url']
                    file = str(os.path.split(url)[1].split('uniq_tag=')[1].split("&")[0] + ".png")
                    if args.vv != False:
                        print(('- - - Downloading #{} / {}. Progress: {}% \nfile: {} \ninfo: {}').format(counter, photos_count, prog, file, biggest))
                    elif args.v != False:
                        print(('- - - Downloading #{} / {}. Progress: {}% \nfile: {}').format(counter, photos_count, prog, file))
                    else:
                        out = ("- - - Downloading #{} / {} Progress[").format(counter, photos_count)
                        for i in range(int(prog/4)):
                            out += chr(9608)
                        for i in range(25 - int(prog/4)):
                            out += chr(9617)
                        out += ("] {}%").format(prog)
                        
                        if (prog < 100):
                            print(out, end="\r")
                        else:
                            print(out)

                    try:
                        pass
                        response = urllib.request.urlopen(url)  # Open photo with url
                        image = response.read()
                        
                        if args.vvv != False:
                            print(response)
                            print(image)
                            
                        if photos_count > 100:  # Making special path with directories for this photo
                            path = str(photo_folder + "/" + str(int((counter-1) / 100)))
                        else:
                            path = photo_folder
                        
                        if not os.path.exists(path):
                            os.mkdir(path)
                            
                        with open (str(path + "/" + file), "wb") as file:
                            file.write(image)
                    except Exception:
                        print('- - - Error, file skipped.')
                        breaked += 1
                        continue                       
            
            # Results
            time_for_dw = time.time() - time_now
            print("{} successfully \n{} failed \nTime spent: {} sec.\n\n". format(photos_count-breaked, breaked, round(time_for_dw,1)))
            
            # More albums?
            print("Download another album? (y/n)")
            answer = input()
            if answer == "y" or answer == "Y":
                args.album = input("Enter albums url: ")
            else:
                exit()
        else:
            print("No permission for this album or it doesnt exist\n\n")


if __name__ == '__main__':
    main()