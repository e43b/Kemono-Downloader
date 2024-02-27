import os
import requests
import logging
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# Configuring logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def sanitize_filename(filename):
    """Remove special characters from a filename."""
    return re.sub(r'[<>:"/\\|?*]', '', filename)

# URL of the page
url = input("Enter the Post Link: ")

# Making the HTTP request
response = requests.get(url)

# Checking if the request was successful
if response.status_code == 200:
    # Parsing HTML content
    soup = BeautifulSoup(response.content, "html.parser")

    # Finding the page title
    title_tag = soup.find("title")
    title = title_tag.text.strip()

    # Removing everything after "by" and replacing spaces with underscores
    title = title.split("by")[0].strip().replace(" ", "_")
    title = sanitize_filename(title)

    # Limiting the number of characters in the folder name
    title = title[:45]

    # Creating the folder with the title as the name
    os.makedirs(title, exist_ok=True)

    # Finding all 'a' tags with class 'fileThumb'
    file_thumb_links = soup.find_all("a", class_="fileThumb")

    # Extracting links from the found tags and saving the images in the created folder
    for idx, link in enumerate(file_thumb_links):
        image_url = link["href"]
        image_response = requests.get(image_url)
        if image_response.status_code == 200:
            # Extracting the file extension from the URL
            _, ext = os.path.splitext(os.path.basename(urlparse(image_url).path))
            # Saving the numbered image with the original extension
            image_path = os.path.join(title, f"{idx + 1}{ext}")
            with open(image_path, "wb") as f:
                f.write(image_response.content)
            print(f"Image {idx + 1} downloaded.")
    print("All downloads have been completed.")
else:
    logging.error("Failed to access the page.")
