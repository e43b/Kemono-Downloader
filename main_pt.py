import os
import requests
import logging
import re
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

    # Encontrando o título da página
    title_tag = soup.find("title")
    title = title_tag.text.strip()

    # Removendo tudo após "by" e substituindo espaços por underscore
    title = title.split("by")[0].strip().replace(" ", "_")
    title = sanitize_filename(title)

    # Limitando o número de caracteres do nome da pasta
    title = title[:45]

    # Criando a pasta com o título como nome
    os.makedirs(title, exist_ok=True)

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
            image_path = os.path.join(title, f"{idx + 1}{ext}")
            with open(image_path, "wb") as f:
                f.write(image_response.content)
            print(f"Imagem {idx + 1} baixada.")
    print("Todos os downloads foram concluídos.")
else:
    logging.error("Falha ao acessar a página.")
