# WebScraping with Python - SouJunor Page

Este projeto consiste em um estudo de caso da Web Scraping utilizando Python. O objetivo do projeto é explorar e entender conceitos de webscraping e a manipulação de dados para a criação de um dataframe.



### Uso

Instalando as dependencias:

    pip install -r requirements.txt


Ajuste as varaveis de ambiente criando um arquivo .env com o seguinte conteudo:

    LOGIN_LINKEDIN=your_linkedin_login
    PASSWORD_LINKEDIN=your_linkedin_password


### Iniciando o script

    python main.py

O script inicializa o webscraping, loga no LinkedIn, navega para os posts, coleta os dados e atualiza o dataframe principal.

### Estrutura do projeto

- **webscraping**/
    - **get_data.py**: Contains the LinkedInScraper class for scraping LinkedIn posts.
    - **process_data.py**: Contains the DataHandler class for processing and saving data.
- **main.py**: The main script to run the LinkedIn web scraping process.
- **.env**: Environment variable file for storing LinkedIn login credentials.

