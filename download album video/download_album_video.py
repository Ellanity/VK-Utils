import argparse
from vk_api.longpoll import VkLongPoll, VkEventType
import vk_api
import requests
import os, time, math
import getpass

from bs4 import BeautifulSoup
import lxml

from pytube import YouTube
import urllib.request
import urllib.parse


def parseArgs():
    
    parser = argparse.ArgumentParser(description='Videos to videos')
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
            
            try:
                # Get album info from url
                album_id_ = str(args.album.split('/')[-1].split('=')[-1].replace('album_', ''))
                owner_id_ = args.album.split('/')[-1].split('?')[0].replace('videos', '')
                
                print("Owner id: " + owner_id_ + " album id: " + album_id_)
                if args.vv != False:
                    print("Getting album:\n")

                response = vk.video.getAlbumById(owner_id=owner_id_, album_id=album_id_)#['items']
                video_count = response['count']
            
                if args.vv != False:
                    print(response)
                    print(video_count)

            except Exception:
                print("This album is not available")
                args.album = None
            
            counter = 0 # of video
            prog = 0 # percentage of downloads
            breaked = 0 # not downloaded due to an error
            time_now = time.time() # start time
            
            #Creating directories
            if not os.path.exists('saved'):
                os.mkdir('saved')
            video_folder = 'saved/{0}_{1}'.format(owner_id_, album_id_)
            if not os.path.exists(video_folder):
                os.mkdir(video_folder)

            print("Start download:")
            # Let's calculate how many times you need to get a list of video, since the number will not be an integer - we round it up
            for j in range(math.ceil(video_count / 100)): 
                
                #Getting a list of video
                video_pack = vk.video.get(owner_id=owner_id_, album_id=album_id_, count=100, offset=j*100)
                if args.vvv != False:
                    print(video_pack)
                for video in video_pack['items']:
                    counter += 1
                    file = str(str(video['owner_id']) + "_" + str(video['id']) + ".mp4")
                    
                    prog = round(100/video_count*counter,2)
                    if args.vv != False:
                        print(('- - - Downloading #{} / {}. Progress: {}% \nfile: {} \ninfo: {}').format(counter, video_count, prog, file, video))
                    elif args.v != False:
                        print(('- - - Downloading #{} / {}. Progress: {}% \nfile: {}').format(counter, video_count, prog, file))
                    else:
                        out = ("- - - Downloading #{} / {} Progress[").format(counter, video_count)
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
                        
                        #Getting the address of the video
                        video_info = parseVideoUrl(video, args)
                        
                        if video_count > 100:  # Making special path with directories for this video
                            path = str(video_folder + "/" + str(int((counter-1) / 100)))
                        else:
                            path = video_folder
                        if not os.path.exists(path):
                            os.mkdir(path)
                            
                        # Downloading video
                        if video_info['host'] == "vk":
                            
                            if args.vv != False:
                                print(str(video_info))
                            
                            r = requests.get(video_info['url'], stream=True)
                            with open (str(path + "/" + file), "wb") as video_file:
                                for chunk in r.iter_content(1024000):
                                    video_file.write(chunk)

                        elif video_info['host'] == "youtube":
                            
                            if args.vv != False:
                                print(str(video_info))
                            
                            yt = YouTube(video_info['url'])
                            yt = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
                            yt.download(path)
                            
                        else:
                            breaked += 1
                        
                    except Exception:
                        #print('- - - Error, file skipped.')
                        breaked += 1
                        continue  
                    
            # Results
            time_for_dw = time.time() - time_now
            print("{} successfully \n{} failed \nTime spent: {} sec.\n\n". format(video_count-breaked, breaked, round(time_for_dw,1)))
            
            # More albums?
            print("Download another album? (y/n)")
            answer = input()
            if answer == "y" or answer == "Y":
                args.album = input("Enter albums url: ")
            else:
                exit()
        else:
            print("No permission for this album or it doesnt exist\n\n")


def parseVideoUrl(video, args):

    html_url = str(video['player'])
    video_info = {}
    
    # Checking host
   
    if 'vk.com' in str(html_url):
    
        # Get html with url for page with video
        html = requests.get(html_url).text
        soup = BeautifulSoup(html, 'lxml')
        
        # Parse video url from page
        video_url = soup.find('div', id = 'page_wrap').find('source').get('src')
        
        if args.vvv != False:
            print(video_url)
        
        url_encoded = urllib.parse.unquote(video_url)
        if args.vvv != False:
            print(url_encoded)

        # Create url for video
        pre_url = str(url_encoded.split(("&path"))[0].split("&dirs")[-1].split("=")[1])
        tag = str(url_encoded.split("&tag=")[1].split("&")[0])
        best_quality = str(url_encoded.split(("&path"))[0].split("&dirs")[-1].split("[")[1].split("]")[0])
        
        url = str(pre_url + tag + "." + best_quality + ".mp4")
        
        if args.vv != False:
            print(url)
            
        video_info = dict(url=url, host="vk")
        
    elif 'youtube.com' in str(html_url):
        
        video_url = video['player'].split("?")[0]
        video_info = dict(url=video_url, host="youtube")
        
    return video_info


if __name__ == '__main__':
    main()