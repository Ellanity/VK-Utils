# Download album photos 
Download all photos from any available for u album in vk

To start just downlolad files and try to start exe from command line or terminal:

```download_album_photos.exe -a ALBUM_URL -t TOKEN```

- ALBUM_URL - it's url in vk for album
- TOKEN - it's key, need for athorization. Read in internet how to get it.

If it does not work, you need to download python 3.7 or higher, download library "vk_api" and start program with next command:

```python download_album_photos.py -a ALBUM_URL -t TOKEN```

For more arguments:
> python download_album_photos.py -h
