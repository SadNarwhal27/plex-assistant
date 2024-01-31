import os, time, datetime, os, re, sys
import feedparser, requests
from mutagen.mp3 import MP3
# from name_change import change_file_name

def flush():
    sys.stdout.flush()
    sys.stderr.flush()

def create_folder(folder_path):
    """Creates a folder at a specified location"""
    os.makedirs(folder_path, exist_ok=True)

def organize_folders(folder_path):
    """Creates folders and organizes files into corresponding directories"""

    # Different regex patterns for detecting type of media
    movie_pattern = r"^([\w.-]+)\.\d+p"
    show_pattern = r"^([\w.-]+)\.S\d{2,3}E\d{2,3}"
    year_pattern = r"\d{4}\b"

    for file in os.listdir(folder_path):
        if re.search(show_pattern, file):
            match = re.search(show_pattern, file).group(1)
        elif re.search(movie_pattern, file):
            match = re.search(movie_pattern, file).group(1)
            if re.search(year_pattern, match):
                year = re.search(year_pattern, match).group(0)
                match = match.replace(year, f"({year})")
        else:
            continue

        match = match.replace('.', ' ')
        destination_folder_path = f"{folder_path}/{match}" 
        create_folder(destination_folder_path)
        os.rename(f"{folder_path}\{file}", f"{destination_folder_path}\{file}")

def organize_albums(folder_path):
    for file in os.listdir(folder_path):
        if '.mp3' in file:
            audio = MP3(f"{folder_path}\{file}")
            
            if ',' in str(audio['TPE1']):
                artist = str(audio['TPE1']).split(',')[0]
            else:
                artist = audio['TPE1']

            album = audio['TALB']

            destination_folder_path = f"{folder_path}/{artist}/{album}"
            create_folder(destination_folder_path)
            os.rename(f"{folder_path}\{file}", f"{destination_folder_path}\{file}")        

def download_file(url, output_path):
    """Takes in a feed url and destination then downloads the content"""
    try:
        flush()
        response = requests.get(url, stream=True)
        block_size = 1024
        # block_size = 8192
        total_file_size = int(response.headers.get('content-length', 0))
        total_kb = int((total_file_size / block_size))
    except:
        print("Error occured in response creation")
    else:
        # Creates a file at a specific path and a progress bar to track download
        with open(output_path, "wb") as file:
            chunks_installed = 0
            for chunk in response.iter_content(chunk_size=block_size):
                file.write(chunk)
                chunks_installed += 1
                sys.stderr.write(f'Download Progress: {round((chunks_installed/total_kb) * 100)}%\n')

def output_files(feed, output_directory):
    """Goes through the feeds and downloads available files"""
    total_files = 0  
    for entry in feed.entries:
        file_name = os.path.basename(entry.title)
        output_path = os.path.join(output_directory, file_name)

        if os.path.isfile(output_path):
            sys.stdout.write(f"{file_name} has already downloaded\n")
            continue
        
        sys.stdout.write(f"=== Downloading: {file_name} ===")
        file_url = entry.link
        download_file(file_url, output_path)
        total_files += 1
    return total_files # Returns the total number of files downloaded

def convert_time_elapsed(elapsed_time):
    """Helps make human readable time for print statements"""
    if elapsed_time > 60:
        total_time = f"Total Time Elapsed: {round(elapsed_time / 60, 2)} minutes"
    else:
        total_time = f"Total Time Elapsed: {round(elapsed_time, 2)} seconds"
    
    return total_time

def main(target_drive, rss_url):

    # Gets the file path for the day's downloads
    today = str(datetime.date.today())
    destination = f"{target_drive}/{today}"

    feed = feedparser.parse(rss_url)
    create_folder(destination)

    feed_start = time.perf_counter() # Starts the timer
    total_files = output_files(feed, destination)
    feed_close = time.perf_counter() # Ends the timer
    elapsed_time = convert_time_elapsed(feed_close - feed_start)

    print(f"\n{'='*20}\n{elapsed_time}\nTotal Files Downloaded: {total_files} files\n{'=' * 20}")
    organize_folders(destination)

    # if audio:
    #     organize_albums(destination)
    # else:
    #     organize_folders(destination)

if __name__ == "__main__":
    # print(sys.argv[2], sys.argv[1])
    main(sys.argv[2], sys.argv[1])
