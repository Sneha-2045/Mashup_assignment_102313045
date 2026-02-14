import sys
import os
import yt_dlp
from moviepy.editor import VideoFileClip
from pydub import AudioSegment

def download_videos(singer, n):
    os.makedirs("videos", exist_ok=True)
    
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'videos/%(title)s.%(ext)s',
        'quiet': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([f"ytsearch{n}:{singer} songs"])

def convert_to_audio():
    os.makedirs("audios", exist_ok=True)

    for file in os.listdir("videos"):
        if file.endswith((".mp4", ".mkv", ".webm")):
            video_path = os.path.join("videos", file)
            audio_path = os.path.join("audios", file.split(".")[0] + ".mp3")

            clip = VideoFileClip(video_path)
            clip.audio.write_audiofile(audio_path)
            clip.close()

def cut_and_merge(duration, output_name):
    final_audio = AudioSegment.empty()

    for file in os.listdir("audios"):
        if file.endswith(".mp3"):
            audio = AudioSegment.from_mp3(os.path.join("audios", file))
            clipped = audio[:duration * 1000]
            final_audio += clipped

    final_audio.export(output_name, format="mp3")

def main():
    try:
        if len(sys.argv) != 5:
            print("Usage: python <program.py> <SingerName> <NumberOfVideos> <AudioDuration> <OutputFileName>")
            sys.exit(1)

        singer = sys.argv[1]
        num_videos = int(sys.argv[2])
        duration = int(sys.argv[3])
        output = sys.argv[4]

        if num_videos <= 10:
            print("Number of videos must be greater than 10")
            sys.exit(1)

        if duration <= 20:
            print("Audio duration must be greater than 20 seconds")
            sys.exit(1)

        print("Downloading videos...")
        download_videos(singer, num_videos)

        print("Converting to audio...")
        convert_to_audio()

        print("Cutting and merging...")
        cut_and_merge(duration, output)

        print("Mashup created successfully:", output)

    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
