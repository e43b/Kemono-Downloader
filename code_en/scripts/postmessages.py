import requests
from bs4 import BeautifulSoup

# URL of the page
url = input("Enter the Post Link: ")

# Make the HTTP request
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Get the HTML content
    html_content = response.text

    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract the title from the <title> tag
    title_tag = soup.find('title').text.strip()

    # Remove invalid characters for file name
    invalid_chars = '\\/:*?"<>|'
    for char in invalid_chars:
        title_tag = title_tag.replace(char, '')

    # Extract the post title
    title = title_tag.split(' | ')[0]

    # Extract the publication date
    published = soup.find('div', class_='post__published').text.strip().split(': ')[1]

    # Extract the content while maintaining formatting
    content = soup.find('div', class_='post__content').get_text(separator='\n')

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
                comments += f"Comment by {commenter} ({comment_time}):\n{comment_message}\n\n"

    # Name the file with the post title
    file_name = "{}.txt".format(title)

    # Save the content in a text file while maintaining formatting
    with open(file_name, 'w', encoding='utf-8') as file:
        file.write("Title: {}\n".format(title))
        file.write("\nPublication Date: {}\n".format(published))
        file.write("\nContent:\n{}\n".format(content))
        if downloads:
            file.write("\nDownloads:\n{}".format(downloads))
        if comments:
            file.write("\nComments:\n{}".format(comments))

    print("Post content successfully saved to '{}'.\n".format(file_name))
else:
    print("Error accessing the page:", response.status_code)
