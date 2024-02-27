import os
import requests
from bs4 import BeautifulSoup
import re

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
        # Verifica se o elemento 'article' não contém uma imagem
        if not article.find("img", class_="post-card__image"):
            # Encontra o elemento 'a' dentro do 'article'
            link = article.find("a")
            # Obtém o atributo href do link
            href = link.get("href")
            # Adiciona o domínio ao link e o armazena na lista
            link_completo = "https://kemono.su" + href
            links_completos_pagina.append(link_completo)

    return links_completos_pagina

# Cria a pasta principal
def criar_pasta_principal(titulo_pagina):
    pasta_principal = re.sub(r'[^\w\s]', '', titulo_pagina).replace(' ', '_').lower()
    if not os.path.exists(pasta_principal):
        os.makedirs(pasta_principal)
    return pasta_principal

# URL base do site
url_base = "https://kemono.su/patreon/user/17913091"

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

# Encontra o título da página a partir da tag meta
titulo_pagina = soup.find("meta", property="og:title")['content']

# Cria a pasta principal com base no título da página
pasta_principal = criar_pasta_principal(titulo_pagina)

# Imprime o título da pasta principal
print("Pasta principal criada:", pasta_principal)

# Encontra a tag <small> com o número total de páginas
tag_small = soup.find("small")
if tag_small:
    # Extrai o texto dentro da tag
    texto = tag_small.get_text(strip=True)
    # Extrai o número total de páginas
    total_paginas = int(texto.split()[-1])
    # Calcula o número máximo de páginas a serem analisadas
    numero_maximo_paginas = (total_paginas - 1) // 50 + 1

    print(f"Número total de páginas: {total_paginas}")
    print(f"Número máximo de páginas a serem analisadas: {numero_maximo_paginas}")

    # Lista para armazenar todos os links completos
    todos_links_completos = []

    # Extrai os links da primeira página
    links_primeira_pagina = extrair_links_pagina(url_primeira_pagina)
    todos_links_completos.extend(links_primeira_pagina)

    # Salva os links da primeira página em um arquivo de texto
    with open(os.path.join(pasta_principal, "links_extraidos.txt"), "w") as f:
        for link in links_primeira_pagina:
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
        with open(os.path.join(pasta_principal, "links_extraidos.txt"), "a") as f:
            for link in links_pagina:
                f.write(link + "\n")

        # Atualiza os contadores
        total_links_extraidos += len(links_pagina)
        total_links_ignorados += 50 - len(links_pagina)

    # Imprime estatísticas
    print(f"Total de links extraídos: {total_links_extraidos}")
    print(f"Total de links ignorados por terem imagem: {total_links_ignorados}")

    # Loop para acessar cada link extraído e extrair o conteúdo
    for link in todos_links_completos:
        # Faça a solicitação HTTP
        response = requests.get(link)

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
            file_name = os.path.join(pasta_principal, "{}.txt".format(title))

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
        # Aguarda um breve intervalo para evitar sobrecarregar o servidor
        time.sleep(1)
else:
    print("Não foi possível encontrar informações sobre o número total de páginas.")
