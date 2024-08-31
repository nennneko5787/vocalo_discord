import json

from yt_dlp import YoutubeDL, cookies


def main():
    global videos
    ydl_opts = {
        "noplaylist": False,
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.cookiejar = cookies.extract_cookies_from_browser("firefox")
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
