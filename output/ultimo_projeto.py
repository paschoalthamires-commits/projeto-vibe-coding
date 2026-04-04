# Nome do Projeto
nome = "Meu Portfólio"

# Arquivos e Ressources

arquivos = {
    "Resume.pdf": "Documentação.pdf",
}

rressources = {
    "Bibliotecas": ["pip", "numpy", "pandas"],
}

# Título e Subtítulo do Projeto
título = "Meu Portfólio"
subtítulo = "Desenvolvimento de Aplicativos Web com Python"

# Imagens do Projeto

imagem_título = "https://example.com/título.jpg"
imagem_arquivos = {
    "Resume.pdf": "https://example.com/documentação.pdf",
}

imagem_rressources = {
    "Bibliotecas": [
        {"nome": "pip", "link": "https://pip.pypa.io/"},
        {"nome": "numpy", "link": "https://numpy.org/"},
        {"nome": "pandas", "link": "https://pandas.pydata.org/"},
    ],
}

# Conteúdo do Projeto

conteudo_título = "Sobre mim:"
conteudo_arquivos = {
    "Resume.pdf": conteudo_título + " Este é o meu currículo.",
}

conteudo_rressources = {
    "Bibliotecas": conteudo_título + " Essas são as bibliotecas que uso no desenvolvimento do meu projeto.",
}

conteudo_imagem = conteudo_título + ". Imagem do Projeto."
conteudo_arquivos = conteudo_título + ". Arquivo de impressão do Projeto."

# Exibição do Portfólio

exibicao_portfólio = """
<b>{}</b><br>
<b>Desenvolvedor</b>: <i>meunome@example.com</i>
<br>
<b>Tecnologias</b>: <i>pypa.io</i>, <i>numpy.org</i>, <i>pandas.pydata.org</i>

<b>{}</b><br>
<b>Criei um projeto que:</b>
<br>
<ul>
    <li>Exibe informações sobre mim e meu currículo</li>
    <li>Utiliza bibliotecas para desenvolvimento de aplicativos web</li>
    <li>Exibe imagens do meu projeto</li>
</ul>

<b>{}</b><br>
<b>Conteúdo:</b>
<br>
<ul>
    <li>Resumo: Sobre mim e o meu currículo</li>
    <li>Descrição de bibliotecas utilizadas</li>
    <li>Imagem do meu projeto</li>
</ul>

<b>{}</b><br>
<b>Link para mais informações:</b>
<br>
<ul>
    <li><a href="https://example.com/curso" target="_blank">Cursos</a></li>
    <li><a href="https://example.com/projeto2" target="_blank">Projeto 2</a></li>
</ul>
""".format(titulo, subtítulo)

# Exibição do Portfólio no Site

exibicao_portfólio_no_site = """
<b>{}</b>
<br>
<b>Este é meu portfólio padrão em Python. Acesse agora e veja o que eu estou fazendo.</b>
""".format(exibicao_portfólio)