import json

from yt_dlp import YoutubeDL


def main():
    global videos
    ydl_opts = {
        "outtmpl": "%(id)s",
        "format": "bestaudio/best",
        "noplaylist": False,
        "default_search": "ytsearch",
    }
    with YoutubeDL(ydl_opts) as ydl:
        playList = ydl.extract_info(
            "https://www.youtube.com/playlist?list=PLD4GDVLEEp6wi73_170Dmv_QC_KyOc7Yp",
            download=False,
        )
        videos = playList.get("entries", [])
        data = json.dumps(videos)
        with open("songs.txt", "w") as f:
            print(data, file=f)


if __name__ == "__main__":
    main()
