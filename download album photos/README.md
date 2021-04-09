# Download album photos 
Download all photos from any available for u album in vk

To start just downlolad files and try to start exe from command line or terminal:

```download_album_photos.exe -a ALBUM_URL -p PASSWORD -l LOGIN```

- ALBUM_URL - it's url in vk for album
- LOGIN - email/phone 
- PASSWORD - password

If it does not work, you need to download python 3.7 or higher, download library "vk_api" and start program with next command:

```python3 download_album_photos.py -a ALBUM_URL -p PASSWORD -l LOGIN```

For more arguments:
> python download_album_photos.py -h
> 
> download_album_photos.exe -h
