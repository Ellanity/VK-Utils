import os
import time
import math
import urllib.request


class PhotosAlbum:

    def __init__(self, session, user_url):
        self.__user_url = user_url
        self.__session = session
        self.__album_owner = self.get_album_owner()
        self.__album_id = self.get_album_id()
        self.__photos_count = self.get_photos_count()
        self.__photo_folder = self.create_directory_to_save()

    class AlbumError(PermissionError, ConnectionError):
        def __init__(self):
            print("This album is not available")

    def get_album_owner(self):
        return str(self.__user_url).split('/')[-1].split('_')[0].replace('album', '')

    def get_album_id(self):
        album_id = str(self.__user_url).split('/')[-1].split('_')[1]
        # Custom id's
        if album_id == "0":
            album_id = "profile"
        if album_id == "00":
            album_id = "wall"
        if album_id == "000":
            album_id = "saved"
        return album_id

    def get_photos_count(self):
        album_owner = self.__album_owner
        album_id = self.__album_id
        # start counting
        photos_count = 0
        if album_id != "0" and album_id != "00" and album_id != "000":
            try:
                # Get album and count of photos in album
                response = self.__session.photos.getAlbums(owner_id=int(album_owner), album_ids=album_id)['items']
                photos_count = response[0]['size']
            except PermissionError:
                raise PhotosAlbum.AlbumError

        if album_id == "profile" or album_id == "wall" or album_id == "saved":
            try:
                response = self.__session.photos.get(owner_id=album_owner, album_id=album_id)
                photos_count = response['count']
            except PermissionError:
                raise PhotosAlbum.AlbumError

        return photos_count

    def create_directory_to_save(self):
        if not os.path.exists('saved_photos'):
            os.mkdir('saved_photos')
        photo_folder = 'saved_photos/{0}_{1}'.format(self.__album_owner, self.__album_id)
        if not os.path.exists(photo_folder):
            os.mkdir(photo_folder)
        return photo_folder

    def download_album(self):
        photos_count = self.__photos_count
        album_id = self.__album_id
        album_owner = self.__album_owner
        photo_folder = self.__photo_folder

        counter = 0  # of photo
        percentage_of_downloads = 0
        aborted = 0  # not downloaded due to an error
        time_now = time.time()  # start time

        print("Start downloading...")
        # Let's calculate how many times you need to get a list of photos,
        # since the number will not be an integer - we round it up
        for j in range(math.ceil(photos_count / 1000)):

            # Getting a list of photos
            photos = self.__session.photos.get(owner_id=album_owner, album_id=album_id, count=1000, offset=j * 1000)

            for photo in photos['items']:
                counter += 1
                percentage_of_downloads = round(100 / photos_count * counter, 2)

                # Getting the address of the image with the largest number of pixels
                biggest = photo['sizes'][0]
                for size in photo['sizes']:
                    if size['width'] >= biggest['width']:
                        biggest = size

                url = biggest['url']
                file = str(os.path.split(url)[1].split('uniq_tag=')[1].split("&")[0] + ".png")

                try:
                    response = urllib.request.urlopen(url)  # Open photo with url
                    image = response.read()

                    # Making special path with directories for this photo
                    if photos_count > 100:
                        path = str(photo_folder + "/" + str(int((counter - 1) / 100)))
                    else:
                        path = photo_folder

                    if not os.path.exists(path):
                        os.mkdir(path)

                    with open(str(path + "/" + file), "wb") as file:
                        file.write(image)

                except ConnectionError:
                    print('- - - Error, file skipped.')
                    aborted += 1
                    continue

                # Beautiful output
                out = f"- - - Downloading #{counter} / {photos_count} Progress["
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
        print(f"{photos_count - aborted} successfully\n{aborted} failed\nTime spent: {round(time_for_dw, 1)} sec.\n")
