import os
import re
import logging
from pathlib import Path
import yt_dlp
from spleeter.separator import Separator

from pitch_algorithm import yin
from plot_notes import plot_pitch_contour

logging.getLogger('spleeter').setLevel(logging.ERROR)

def sanitize_filename(filename):
    """
    Sanitizes a string to be a valid filename.
    Removes invalid characters and replaces spaces with underscores.
    """
    s = re.sub(r'[^\w\s-]', '', filename)
    s = re.sub(r'\s+', '_', s)
    return s.strip()

def download_and_split(youtube_url, stems: int, hz_threshold:int):
    """
    Downloads a YouTube video as an MP3 and splits it into the specified number of stems.
    """
    try:
        print(f"Downloading audio from {youtube_url}...")
        yt_opts_title = {
            'noplaylist': True,
            'quiet': True,
            'skip_download': True,
        }
        with yt_dlp.YoutubeDL(yt_opts_title) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            video_title = info.get('title', 'video')

        sanitized_title = sanitize_filename(video_title)
        output_path_template = os.path.join('raw_videos', f'{sanitized_title}.%(ext)s')

        yt_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_path_template,
            'noplaylist': True,
            'quiet': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        
        with yt_dlp.YoutubeDL(yt_opts) as ydl:
            ydl.download([youtube_url])
        
        mp3_path = os.path.join('raw_videos', f'{sanitized_title}.mp3')
        if not os.path.exists(mp3_path):
            raise FileNotFoundError(f"Downloaded file not found at {mp3_path}")

        print("Download complete.")
        print(f"Splitting audio from '{sanitized_title}' into {stems} stems...")
        
        separator = Separator(f'spleeter:{stems}stems')
        output_folder = "splitted_audios"
        separator.separate_to_file(mp3_path, output_folder)
        print("###################")
        print("###################")
        print("#######     #######")
        
        print(f"Splitting complete. The files are located in the '{os.path.join(output_folder, sanitized_title)}' folder.")
        
        vocals_path = os.path.join(output_folder, sanitized_title, 'vocals.wav')

        if os.path.exists(vocals_path):
            print("Getting the notes with the YIN algorithm...")
            times, freqs, notes = yin(vocals_path)
            
            if len(times) > 0:
                print("I have the notes now. Generating pitch plot...")
                plot_filename = f'{sanitized_title}_pitch_contour.png'
                plot_pitch_contour(times,
                                   freqs,
                                   notes,
                                   plot_filename,
                                  hz_threshold = hz_threshold)
                
            else:
                print("Something happened IDK I blame you.")
        else:
            print(f"Could not find vocals file at {vocals_path}. Skipping analysis.")
        print("#######     #######")
        print("###################")
        print("###################")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Please check the URL or try again or IDK.")

def check_folders():
    """Ensures necessary directories exist."""
    os.makedirs('raw_videos', exist_ok=True)
    os.makedirs('splitted_audios', exist_ok=True)
    os.makedirs('note_plots', exist_ok=True)
    

if __name__ == '__main__':
    check_folders()
    while True:
        try:
            youtube_url = input("YouTube URL (or press Enter to exit): ")
            if not youtube_url:
                print("Bye bye then")
                break
            
            stems_input = input("Enter number of stems (2, 4, or 5): ")
            stems = int(stems_input) if stems_input in ['2', '4', '5'] else "IDK"
            
            if stems == "IDK":
                print(f"I don't know what {stems_input} means. I'll just assume is 2")
                stems = 2
            hz_threshold_input = input("Enter the lowest Hz of the voice:\n \
            (or just Enter if you have no idea what i'm talking about): ")
            if not hz_threshold_input:
                hz_threshold_input = 60
            try:
                hz_threshold_input = int(hz_threshold_input)
            except:
                hz_threshold_input = 60
            if hz_threshold_input < 60:
                hz_threshold_input = 60
            if hz_threshold_input > 400:
                hz_threshold_input = 400
            
            download_and_split(youtube_url, stems, hz_threshold_input)
        except Exception as e:
            print(f"SOMETHING HAPPENED!!!!!!!!: {e}")