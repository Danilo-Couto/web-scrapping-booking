# Web Scrapping Booking

Python script to scrap results from Booking.com for city, dates and quantity of adults.
It was develop to forecast demand and price floating in the area of my hostel in Pipa RN Brazil, but also useeful to other hotel businesses in any location.

### Install and Usage
  1. Clone the repo and enter to the folder you have just cloned
  2. Create the virtual environment for the project
  - `python3 -m venv .venv && source .venv/bin/activate`

  3. Install the dependencies
  - `python3 -m pip install -r requirements.txt`

  4. Set your variables to:
  ```bash
    - search_location = ''
    - min_pax = 
    - max_pax = 
    - start_date = ''
    - end_date = ''
  ```
    
  5. Run python3 -u <path to the code>
   
### Libs
  - selenium
  - beautifulsoup4
  - requests
  - pandas
    
### Some of the challenges
Get elements using Seleneium and BeatifulSoup

### Implements in the future
  1. Run automatically every day
  2. Graphically dump in an excel
  3. Connect to my hotel channel manager and make auto price adjustmenta
