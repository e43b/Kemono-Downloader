import os
import re
import requests
import logging
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# Configuring logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def sanitize_filename(filename):
    """Remove special characters from a filename."""
    return re.sub(r'[<>:"/\\|?*]', '', filename)

# URL of the page
url = input("Enter Post Link: ")

# Making HTTP request
response = requests.get(url)

# Checking if the request was successful
if response.status_code == 200:
    # Parsing HTML content
    soup = BeautifulSoup(response.content, "html.parser")

    # Extracting folder name from meta tag
    meta_tag = soup.find('meta', property='og:title')
    if meta_tag:
        folder_name = meta_tag['content']
    else:
        folder_name = "Untitled_Folder"  # Default name if tag is not found

    # Removing invalid characters for folder name
    folder_name = sanitize_filename(folder_name)

    # Limiting the number of characters in the folder name
    folder_name = folder_name[:45]

    # Creating folder with the extracted name
    folder_path = os.path.abspath(folder_name)
    os.makedirs(folder_path, exist_ok=True)

    # Finding all 'a' tags with class 'fileThumb'
    file_thumb_links = soup.find_all("a", class_="fileThumb")

    # Extracting links from found tags and saving images in the created folder
    for idx, link in enumerate(file_thumb_links):
        image_url = link["href"]
        image_response = requests.get(image_url)
        if image_response.status_code == 200:
            # Extracting file extension from URL
            _, ext = os.path.splitext(os.path.basename(urlparse(image_url).path))
            # Saving the numbered image with original extension
            image_path = os.path.join(folder_path, f"{idx + 1}{ext}")
            with open(image_path, "wb") as f:
                f.write(image_response.content)
            print(f"Image {idx + 1} downloaded.")
    print("All downloads have been completed.")

    # Extracting information from the second code block
    # Get HTML content
    html_content = response.text

    # Parse HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract title from <title> tag
    title_tag = soup.find('title').text.strip()

    # Remove invalid characters for filename
    invalid_chars = '\\/:*?"<>|'
    for char in invalid_chars:
        title_tag = title_tag.replace(char, '')

    # Extract post title
    title = title_tag.split(' | ')[0]

    # Extract publication date
    published = soup.find('div', class_='post__published').text.strip().split(': ')[1]

    # Extract content while maintaining formatting
    content_tag = soup.find('div', class_='post__content')
    if content_tag:
        content = content_tag.get_text(separator='\n')
    else:
        content = "Content not found."

    # Extract download links, if any
    downloads = ""
    downloads_section = soup.find('h2', string='Downloads')
    if downloads_section:
        download_links = downloads_section.find_next('ul', class_='post__attachments').find_all('a', class_='post__attachment-link')
        for link in download_links:
            downloads += f"Download Link: {link['href']}\n"

    # Extract comments
    comments = ""
    comments_section = soup.find('footer', class_='post__footer')
    if comments_section:
        comments_header = comments_section.find('h2', class_='site-section__subheading')
        if comments_header and comments_header.text.strip() == 'Comments':
            comment_articles = comments_section.find_all('article', class_='comment')
            for article in comment_articles:
                commenter = article.find('a', class_='fancy-link fancy-link--local comment__name').text.strip()
                comment_message = article.find('p', class_='comment__message').text.strip()
                comment_time = article.find('time', class_='timestamp').text.strip()
                comments += f"Comment from {commenter} ({comment_time}):\n{comment_message}\n\n"

    # Name the file with the post title
    file_name = "{}.txt".format(title)

    # Full path to the text file within the folder
    file_path = os.path.join(folder_path, file_name)

    # Save content to a text file while maintaining formatting
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write("Title: {}\n".format(title))
        file.write("\nPublication Date: {}\n".format(published))
        file.write("\nContent:{}\n".format(content))
        if downloads:
            file.write("\nDownloads:\n{}".format(downloads))
        if comments:
            file.write("\nComments:\n{}".format(comments))

    print("Post content successfully saved in '{}'.\n".format(file_path))
else:
    logging.error("Failed to access the page.")
