import os
import re
import requests
import logging
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# Configurando o logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def sanitize_filename(filename):
    """Remove caracteres especiais de um nome de arquivo."""
    return re.sub(r'[<>:"/\\|?*]', '', filename)

# URL da página
url = input("Digite o Link do Post: ")

# Fazendo a requisição HTTP
response = requests.get(url)

# Verificando se a requisição foi bem sucedida
if response.status_code == 200:
    # Parseando o conteúdo HTML
    soup = BeautifulSoup(response.content, "html.parser")

    # Extrair o nome da pasta a partir da tag meta
    meta_tag = soup.find('meta', property='og:title')
    if meta_tag:
        folder_name = meta_tag['content']
    else:
        folder_name = "Pasta_Sem_Nome"  # Nome padrão caso a tag não seja encontrada

    # Removendo caracteres inválidos para nome de pasta
    folder_name = sanitize_filename(folder_name)

    # Limitando o número de caracteres do nome da pasta
    folder_name = folder_name[:45]

    # Criando a pasta com o nome extraído
    folder_path = os.path.abspath(folder_name)
    os.makedirs(folder_path, exist_ok=True)

    # Encontrando todas as tags 'a' com a classe 'fileThumb'
    file_thumb_links = soup.find_all("a", class_="fileThumb")

    # Extraindo os links das tags encontradas e salvando as imagens na pasta criada
    for idx, link in enumerate(file_thumb_links):
        image_url = link["href"]
        image_response = requests.get(image_url)
        if image_response.status_code == 200:
            # Extrai a extensão do arquivo da URL
            _, ext = os.path.splitext(os.path.basename(urlparse(image_url).path))
            # Salva a imagem numerada com a extensão original
            image_path = os.path.join(folder_path, f"{idx + 1}{ext}")
            with open(image_path, "wb") as f:
                f.write(image_response.content)
            print(f"Imagem {idx + 1} baixada.")
    print("Todos os downloads foram concluídos.")

    # Extração de informações do segundo bloco de código
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
    content_tag = soup.find('div', class_='post__content')
    if content_tag:
        content = content_tag.get_text(separator='\n')
    else:
        content = "Conteúdo não encontrado."

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

    # Caminho completo para o arquivo de texto dentro da pasta
    file_path = os.path.join(folder_path, file_name)

    # Salve o conteúdo em um arquivo de texto mantendo a formatação
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write("Título: {}\n".format(title))
        file.write("\nData de Publicação: {}\n".format(published))
        file.write("\nConteúdo:{}\n".format(content))
        if downloads:
            file.write("\nDownloads:\n{}".format(downloads))
        if comments:
            file.write("\nComentários:\n{}".format(comments))

    print("Conteúdo da postagem salvo com sucesso em '{}'.\n".format(file_path))
else:
    logging.error("Falha ao acessar a página.")
