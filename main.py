import os, time, datetime, os
import feedparser, requests

from alive_progress import alive_bar
from dotenv import load_dotenv

def create_folder(folder_path):
    """Creates a folder at a specified location"""
    os.makedirs(folder_path, exist_ok=True)

def download_file(url, output_path):
    """Takes in a feed url and destination then downloads the content"""
    try:
        response = requests.get(url, stream=True)
        total_file_size = int(response.headers.get('content-length', 0))
    except:
        print("Error occured in response creation")
    else:
        # Creates a file at a specific path and a progress bar to track download
        with open(output_path, "wb") as file:
            with alive_bar(total_file_size) as bar:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
                    bar(8192)

def output_files(feed, output_directory):
    """Goes through the feeds and downloads available files"""
    total_files = 0
    for entry in feed.entries:
        file_name = os.path.basename(entry.title)
        output_path = os.path.join(output_directory, file_name)

        if os.path.isfile(output_path):
            print(f"{file_name} has already downloaded")
            continue

        print(f"=== Downloading: {file_name} ===")
        tic = time.perf_counter()

        file_url = entry.link
        download_file(file_url, output_path)

        toc = time.perf_counter()
        print(f"Downloaded to: {output_path}\n{convert_time_elapsed(toc-tic)}\n{'='*20}")
        total_files += 1
    return total_files # Returns the total number of files downloaded

def convert_time_elapsed(elapsed_time, total=False):
    """Helps make human readable time for print statements"""
    if elapsed_time > 60:
        total_time = f"Time Elapsed: {round(elapsed_time / 60, 2)} minutes"
    else:
        total_time = f"Time Elapsed: {round(elapsed_time, 2)} seconds"
    
    if total:
        total_time = 'Total ' + total_time
    return total_time
    

def main(target_drive, rss_url):
    load_dotenv()
    feed = feedparser.parse(rss_url)

    # Creatse the day's unprocessed folder
    today = str(datetime.date.today())
    destination = f"{target_drive}/{today}"
    create_folder(destination)

    feed_start = time.perf_counter() # Starts the timer
    total_files = output_files(feed, destination)
    feed_close = time.perf_counter() # Ends the timer
    elapsed_time = convert_time_elapsed(feed_close - feed_start, True)

    print(f"\n{'='*20}\n{elapsed_time}\nTotal Files Downloaded: {total_files} files\n{'=' * 20}")

if __name__ == "__main__":
    main(os.getenv('TARGET_DRIVE'), os.getenv('RSS_URL'))