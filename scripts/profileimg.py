from bs4 import BeautifulSoup
import requests
import time
import os
import logging
import re
from urllib.parse import urlparse

# Configurando o logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Função para extrair links de uma página específica
def extrair_links_pagina(url):
    # Realiza o request e obtém o conteúdo da página
    print("Fazendo o request para", url)
    response = requests.get(url, headers=headers)
    html_content = response.content

    # Analisa o conteúdo HTML
    soup = BeautifulSoup(html_content, "html.parser")

    # Encontra todos os elementos 'article' com a classe 'post-card' e 'post-card--preview'
    articles = soup.find_all("article", class_="post-card post-card--preview")

    # Lista para armazenar os links completos
    links_completos_pagina = []

    # Itera sobre os elementos 'article' encontrados
    for article in articles:
        # Verifica se o elemento 'article' contém uma imagem
        if article.find("img", class_="post-card__image"):
            # Encontra o elemento 'a' dentro do 'article'
            link = article.find("a")
            # Obtém o atributo href do link
            href = link.get("href")
            # Adiciona o domínio ao link e o armazena na lista
            link_completo = "https://kemono.su" + href
            links_completos_pagina.append(link_completo)

    return links_completos_pagina

def sanitize_filename(filename):
    """Remove caracteres especiais de um nome de arquivo."""
    return re.sub(r'[<>:"/\\|?*]', '', filename)

# URL base do perfil
url_base = input('Digite o Link do perfil que deseja baixar os posts: ')

# Cabeçalho do navegador
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.4535.0 Safari/537.36"
}

# Realiza o request e obtém o conteúdo da primeira página
url_primeira_pagina = url_base
response = requests.get(url_primeira_pagina, headers=headers)
html_content = response.content

# Analisa o conteúdo HTML
soup = BeautifulSoup(html_content, "html.parser")

# Encontra a tag <title> para obter o título da página principal
title_tag = soup.find("title")
if title_tag:
    # Extrai o texto dentro da tag
    title = title_tag.text.strip()
    # Sanitize o título para remover caracteres especiais
    title = sanitize_filename(title)
else:
    # Se não for possível encontrar a tag <title>, define um título padrão
    title = "Posts"

# Cria uma pasta principal com o título da página principal
main_folder = os.path.join(os.getcwd(), title)
os.makedirs(main_folder, exist_ok=True)

# Encontra a tag <small> com o número total de páginas
tag_small = soup.find("small")
if tag_small:
    # Extrai o texto dentro da tag
    texto = tag_small.get_text(strip=True)
    # Extrai o número total de páginas
    total_paginas = int(texto.split()[-1])
    # Calcula o número máximo de páginas a serem analisadas
    numero_maximo_paginas = (total_paginas - 1) // 50 + 1

    print(f"\nNúmero total de páginas: {total_paginas}")
    print(f"Número máximo de páginas a serem analisadas: {numero_maximo_paginas}\n")

    # Lista para armazenar todos os links completos
    todos_links_completos = []

    # Extrai os links da primeira página
    links_primeira_pagina = extrair_links_pagina(url_primeira_pagina)
    todos_links_completos.extend(links_primeira_pagina)

    # Salva os links da primeira página em um arquivo de texto
    with open(os.path.join(main_folder, "links_extraidos.txt"), "w") as f:
        for link in todos_links_completos:
            f.write(link + "\n")

    # Contadores de links extraídos e ignorados
    total_links_extraidos = len(links_primeira_pagina)
    total_links_ignorados = 50 - len(links_primeira_pagina)

    # Loop para navegar pelas páginas restantes e extrair os links
    for pagina_numero in range(1, numero_maximo_paginas):
        # Calcula o deslocamento 'o' para a página atual
        deslocamento = pagina_numero * 50
        # Constrói a URL da página atual
        url_pagina = f"{url_base}?o={deslocamento}"

        # Extrai os links da página atual
        links_pagina = extrair_links_pagina(url_pagina)
        todos_links_completos.extend(links_pagina)

        # Atualiza os links no arquivo de texto
        with open(os.path.join(main_folder, "links_extraidos.txt"), "a") as f:
            for link in links_pagina:
                f.write(link + "\n")

        # Atualiza os contadores
        total_links_extraidos += len(links_pagina)
        total_links_ignorados += 50 - len(links_pagina)

    # Imprime estatísticas
    print(f"Total de links extraídos: {total_links_extraidos}")
    print(f"Total de links ignorados por falta de imagem: {total_links_ignorados}\n")
else:
    print("Não foi possível encontrar informações sobre o número total de páginas.")

# Loop para baixar os posts de cada link extraído
for link in todos_links_completos:
    response = requests.get(link)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        title_tag = soup.find("title")
        title = title_tag.text.strip()
        title = title.split("by")[0].strip().replace(" ", "_")
        title = sanitize_filename(title)
        title = title[:45]
        # Cria uma pasta para o post dentro da pasta principal
        post_folder = os.path.join(main_folder, title)
        os.makedirs(post_folder, exist_ok=True)
        file_thumb_links = soup.find_all("a", class_="fileThumb")
        for idx, link in enumerate(file_thumb_links):
            image_url = link["href"]
            image_response = requests.get(image_url)
            if image_response.status_code == 200:
                _, ext = os.path.splitext(os.path.basename(urlparse(image_url).path))
                image_path = os.path.join(post_folder, f"{idx + 1}{ext}")
                with open(image_path, "wb") as f:
                    f.write(image_response.content)
                print(f"Imagem {idx + 1} de {title} baixada.")
        print(f"Todos os downloads de {title} foram concluídos.\n")
    else:
        logging.error(f"Falha ao acessar a página: {link}\n")
