import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

# Função para verificar e corrigir o link
def corrigir_link(link):
    if not link.endswith("dms"):
        link += "/dms"
    return link

# Função para extrair o conteúdo dos artigos e criar arquivos de texto
def extrair_conteudo(link):
    response = requests.get(link)
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all("article", class_="dm-card")

    # Extrair o título para a pasta
    title = soup.find("meta", property="og:title")["content"]
    title = title.replace("|", "-").strip()  # Remover caracteres inválidos para nome de pasta
    os.makedirs(title, exist_ok=True)  # Criar pasta se não existir

    for i, article in enumerate(articles, start=1):
        content = article.find("div", class_="dm-card__content").text.strip()
        published_date = article.find("div", class_="dm-card__added").text.strip()
        file_title = f"{i}_{published_date.replace(':', '-')}"

        file_path = os.path.join(title, f"{file_title}.txt")
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
            file.write(f"\n\nPublished: {published_date}")

# Link do perfil
link = input('Digite o Link do Perfil que deseja baixar as DMs: ')
link = corrigir_link(link)

# Extrair conteúdo e criar arquivos de texto
extrair_conteudo(link)
