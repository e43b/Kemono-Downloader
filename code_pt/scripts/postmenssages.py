import requests
from bs4 import BeautifulSoup

# URL da página
url = input("Digite o Link do Post: ")

# Faça a solicitação HTTP
response = requests.get(url)

# Verifique se a solicitação foi bem-sucedida
if response.status_code == 200:
    # Obtenha o conteúdo HTML
    html_content = response.text

    # Parseie o conteúdo HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extraia o título da tag <title>
    title_tag = soup.find('title').text.strip()

    # Remova caracteres inválidos para nome de arquivo
    invalid_chars = '\\/:*?"<>|'
    for char in invalid_chars:
        title_tag = title_tag.replace(char, '')

    # Extraia o título da postagem
    title = title_tag.split(' | ')[0]

    # Extraia a data de publicação
    published = soup.find('div', class_='post__published').text.strip().split(': ')[1]

    # Extraia o conteúdo mantendo a formatação
    content = soup.find('div', class_='post__content').get_text(separator='\n')

    # Extraia links de download, se existirem
    downloads = ""
    downloads_section = soup.find('h2', string='Downloads')
    if downloads_section:
        download_links = downloads_section.find_next('ul', class_='post__attachments').find_all('a', class_='post__attachment-link')
        for link in download_links:
            downloads += f"Link de Download: {link['href']}\n"

    # Extraia os comentários
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
                comments += f"Comentário de {commenter} ({comment_time}):\n{comment_message}\n\n"

    # Nomeie o arquivo com o título da postagem
    file_name = "{}.txt".format(title)

    # Salve o conteúdo em um arquivo de texto mantendo a formatação
    with open(file_name, 'w', encoding='utf-8') as file:
        file.write("Título: {}\n".format(title))
        file.write("\nData de Publicação: {}\n".format(published))
        file.write("\nConteúdo:{}\n".format(content))
        if downloads:
            file.write("\nDownloads:\n{}".format(downloads))
        if comments:
            file.write("\nComentários:\n{}".format(comments))

    print("Conteúdo da postagem salvo com sucesso em '{}'.\n".format(file_name))
else:
    print("Erro ao acessar a página:", response.status_code)
