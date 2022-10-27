# Web Scrapping Booking

Python script to scrap results from Booking.com for city, dates and quantity of adults.
It was develop to forecast demand and price floating in the area of my hostel in Pipa RN Brazil, but also useeful to other hotel businesses in any location.

### Install and Usage
  1. Clone o repositório e entre na pasta do repositório que você acabou de clonar

  2. Crie o ambiente virtual para o projeto
  - `python3 -m venv .venv && source .venv/bin/activate`

  3. Instale as dependências
  - `python3 -m pip install -r requirements.txt`

  4. Defina suas variaveis em:
  ```bash
    - search_location = ''
    - min_pax = 
    - max_pax = 
    - start_date = ''
    - end_date = ''
  ```
    
  5. Rode com python3 -u <path to the code>
   
### Libs
selenium
beautifulsoup4
requests
pandas
    
### Some of the challenges
Get elements using Seleneium and BeatifulSoup

### Implements in the future
Run automactilly every day
Ddumps graficilly in an excel
Connect to my hotel channel manager and auto-price adjusments
