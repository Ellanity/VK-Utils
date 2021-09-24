import requests
import os
import time
import math

from bs4 import BeautifulSoup
# import lxml

from pytube import YouTube
import urllib.request
import urllib.parse


class VideosAlbum:
    pass

    def __init__(self, session, user_url):
        self.__user_url = user_url
        self.__session = session
        self.__album_owner = self.get_album_owner()
        self.__album_id = self.get_album_id()
        self.__videos_count = self.get_videos_count()
        self.__videos_folder = self.create_directory_to_save()

    class AlbumError(PermissionError, ConnectionError):
        def __init__(self):
            print("This album is not available")

    def get_album_owner(self):
        return str(self.__user_url).split('/')[-1].split('?')[0].replace('videos', '')

    def get_album_id(self):
        album_id = str(self.__user_url).split('/')[-1].split('=')[-1].replace('album_', '')

        # Custom id's
        if album_id == "uploaded":
            album_id = "-1"
        if album_id[:6] == "videos":
            album_id = "-2"

        return album_id

    def get_videos_count(self):
        videos_count = 0
        try:
            album_owner = self.__album_owner
            album_id = self.__album_id
            response = self.__session.video.getAlbumById(owner_id=album_owner, album_id=int(album_id))
            videos_count = response['count']
        except PermissionError:
            raise VideosAlbum.AlbumError
        return videos_count

    def create_directory_to_save(self):
        if not os.path.exists('saved_videos'):
            os.mkdir('saved_videos')
        videos_folder = 'saved_videos/{0}_{1}'.format(self.__album_owner, self.__album_id)
        if not os.path.exists(videos_folder):
            os.mkdir(videos_folder)
        return videos_folder

    def parse_video_url(self, video):
        html_url = str(video['player'])
        video_info = {}

        # Checking host
        if 'vk.com' in str(html_url):

            # Get html with url for page with video
            html = requests.get(html_url).text
            soup = BeautifulSoup(html, 'lxml')

            # Parse video url from page
            video_url = soup.find('div', id='page_wrap').find('source').get('src')
            url_encoded = urllib.parse.unquote(video_url)

            # print(url_encoded)
            # Create url for video
            pre_url = str(url_encoded.split(("&path"))[0].split("&dirs")[-1].split("=")[1])
            # print(pre_url)
            tag = str(url_encoded.split("&tag=")[1].split("&")[0])
            # print(tag)

            best_quality = str(url_encoded.split(("&path"))[0].split("&dirs")[-1].split("[")[1].split("]")[0])
            # print(best_quality)

            url = str(pre_url + tag + "." + best_quality + ".mp4")

            video_info = dict(url=url, host="vk")

        elif 'youtube.com' in str(html_url):

            video_url = video['player'].split("?")[0]
            video_info = dict(url=video_url, host="youtube")

        return video_info

    def download_album(self):
        videos_count = self.__videos_count
        album_id = self.__album_id
        album_owner = self.__album_owner
        videos_folder = self.__videos_folder

        counter = 0  # of photo
        percentage_of_downloads = 0
        aborted = 0  # not downloaded due to an error
        time_now = time.time()  # start time

        print("Start downloading...")
        for j in range(math.ceil(videos_count / 100)):
            # Getting a list of video
            video_pack = self.__session.video.get(owner_id=int(album_owner), album_id=int(album_id),
                                                  count=100, offset=j * 100)
            # print(video_pack)
            for video in video_pack['items']:
                counter += 1
                file = str(str(video['owner_id']) + "_" + str(video['id']) + ".mp4")

                percentage_of_downloads = round(100 / videos_count * counter, 2)
                try:
                    # Getting the address of the video
                    video_info = self.parse_video_url(video)

                    if videos_count > 100:  # Making special path with directories for this video
                        path = str(videos_folder + "/" + str(int((counter - 1) / 100)))
                    else:
                        path = videos_folder
                    if not os.path.exists(path):
                        os.mkdir(path)

                    # Downloading video
                    if video_info['host'] == "vk":

                        r = requests.get(video_info['url'], stream=True)
                        with open(str(path + "/" + file), "wb") as video_file:
                            for chunk in r.iter_content(1024000):
                                video_file.write(chunk)

                    elif video_info['host'] == "youtube":

                        yt = YouTube(video_info['url'])
                        yt = yt.streams.filter(progressive=True, file_extension='mp4').order_by(
                            'resolution').desc().first()
                        yt.download(path)

                    else:
                        aborted += 1
                except Exception:
                    # print('- - - Error, file skipped.')
                    aborted += 1
                    continue

                # Beautiful output
                out = f"- - - Downloading #{counter} / {videos_count} Progress["
                for i in range(int(percentage_of_downloads / 4)):
                    out += chr(9608)
                for i in range(25 - int(percentage_of_downloads / 4)):
                    out += chr(9617)
                out += f"] {percentage_of_downloads}%"
                if percentage_of_downloads < 100:
                    print(out, end="\r")
                else:
                    print(out)

        # Results
        time_for_dw = time.time() - time_now
        print(f"\n{videos_count - aborted} successfully\n{aborted} failed\nTime spent: {round(time_for_dw, 1)} sec.\n")
