import time
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from bs4 import BeautifulSoup

import pyfiglet

import json



import mysql.connector
retry = 0
max_retry = 3




def scroll_component(driver, element):
    driver.execute_script("arguments[0].scrollIntoView();", element)

def compare_with_today(date_str):
    try:
        date_obj = parse_date(date_str)
        date_only = date_obj.date()
        today_date = datetime.today().date()
        if today_date > date_only:
            return "past"
        else:
            return "future"
    except ValueError as e:
        return str(e)
    
def format_date(date_text):
    """
    Converts a date string to the desired format.
    
    Args:
    date_text (str): The date string to be formatted.

    Returns:
    str: The formatted date string, or the original string if no formatting is needed.
    """
    try:
        # Try to parse the date string assuming it has a time component
        date_obj = datetime.strptime(date_text, '%d %b, %I:%M\u202f%p')
        # Format the datetime object to the desired format
        formatted_date = date_obj.strftime('%d %b, %I:%M %p')
    except ValueError:
        # If parsing fails, return the original date string
        formatted_date = date_text
    
    return formatted_date


def parse_date(date_str):
    formats_without_year = ["%a, %d %b", "%d %b, %I:%M %p"]
    formats_with_year = ["%d %b %y", "%a %d %b %y", "%d %b %y, %I:%M %p", "%a %d %b %y, %I:%M %p"]
    
    # Try formats without year first, assuming current year
    for fmt in formats_without_year:
        try:
            parsed_date = datetime.strptime(date_str, fmt)
            current_year = datetime.today().year
            return parsed_date.replace(year=current_year)
        except ValueError:
            continue
    
    # Try formats with year next
    for fmt in formats_with_year:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    raise ValueError(f"Date string {date_str} does not match any known format.")

def compare_with_today(date_str):
    try:
        date_obj = parse_date(date_str)
        date_only = date_obj.date()
        today_date = datetime.today().date()
        if today_date > date_only:
            return "past"
        else:
            return "future"
    except ValueError as e:
        return str(e)
    
def format_date(date_text):
    """
    Converts a date string to the desired format.
    
    Args:
    date_text (str): The date string to be formatted.

    Returns:
    str: The formatted date string, or the original string if no formatting is needed.
    """
    try:
        # Try to parse the date string assuming it has a time component
        date_obj = datetime.strptime(date_text, '%d %b, %I:%M\u202f%p')
        # Format the datetime object to the desired format
        formatted_date = date_obj.strftime('%d %b, %I:%M %p')
    except ValueError:
        # If parsing fails, return the original date string
        formatted_date = date_text
    
    return formatted_date



def save_data_to_database(data):
    # Connexion à la base de données MySQL
    conn = mysql.connector.connect(
        host='localhost', 
        user='root',  
        password='',  
        database='dataset'  # Remplacez par le nom de votre base de données
    )
    cursor = conn.cursor()
    match_ids = []

    for match in data:
        cursor.execute('''
        INSERT INTO matches (date_text, unix_timestamp, team_a_logo_url, team_a_name, team_a_goal, team_b_logo_url, team_b_name, team_b_goal, day)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', match)
        conn.commit()
        match_id = cursor.lastrowid
        match_ids.append(match_id)

    conn.close()
    print("Data saved to database.")
    return match_ids

def extract_info_from_html(soup, day,unix_timestamp):
    # soup = BeautifulSoup(html_content, 'html.parser')

    match_data = []
    stats_data = []
    date_text = ''
    team_a_logo_url = ''
    team_a_name = ''
    team_a_goal = ''
    team_b_logo_url = ''
    team_b_name = ''
    team_b_goal = ''

    try:
        # Extract date information
        imso_hide_overflow_div = soup.find('div', class_='imso-hide-overflow')
        spans = imso_hide_overflow_div.find_all('span')  # Only direct child span elements
        if len(spans) > 1:
            date = spans[4].text.strip()
            date_text = format_date(date)

    except Exception as e:
        print(f"An error occurred while extracting date: {e}")

    try:
        # Extract team A information
        team_a_logo_element = soup.select_one('.imso_mh__first-tn-ed .imso_btl__mh-logo')
        if team_a_logo_element:
            team_a_logo_url = team_a_logo_element['src']

        team_a_name_element = soup.select_one('.imso_mh__first-tn-ed .imso_mh__tm-nm .liveresults-sports-immersive__hide-element')
        if team_a_name_element:
            team_a_name = team_a_name_element.text
        team_a_goal_element = soup.select_one('.imso_mh__l-tm-sc')
        if team_a_goal_element:
            team_a_goal = team_a_goal_element.text
    except Exception as e:
        print(f"An error occurred while extracting team A information: {e}")

    try:
        # Extract team B information
        team_b_logo_element = soup.select_one('.imso_mh__second-tn-ed .imso_btl__mh-logo')
        if team_b_logo_element:
            team_b_logo_url = team_b_logo_element['src']
        team_b_name_element = soup.select_one('.imso_mh__second-tn-ed .imso_mh__tm-nm .liveresults-sports-immersive__hide-element')
        if team_b_name_element:
            team_b_name = team_b_name_element.text
        team_b_goal_element = soup.select_one('.imso_mh__r-tm-sc')
        if team_b_goal_element:
            team_b_goal = team_b_goal_element.text
    except Exception as e:
        print(f"An error occurred while extracting team B information: {e}")

    time.sleep(2)

    match_data.append([date_text, unix_timestamp, team_a_logo_url, team_a_name, team_a_goal, team_b_logo_url, team_b_name, team_b_goal, day])

    match_id =save_data_to_database(match_data)
    date_res = compare_with_today(date_text)
    if date_res == 'past':
        shots_rows = soup.find_all('tr', class_='MzWkAb')
        if shots_rows:
            shots_data = []
            for row in shots_rows:
                tds = row.find_all('td')
                for td in tds:
                    shots_data.append(td.text.strip())
            team_a_short = shots_data[0]
            team_b_short = shots_data[1]
            team_a_shots_on_target = shots_data[2]
            team_b_shots_on_target = shots_data[3]
            team_a_possession = shots_data[4].strip("%")
            team_b_possession = shots_data[5].strip("%")
            team_a_passes = shots_data[6]
            team_b_passes = shots_data[7]
            team_a_pass_accuracy = shots_data[8].strip("%")
            team_b_pass_accuracy = shots_data[9].strip("%")
            team_a_fouls = shots_data[10]
            team_b_fouls = shots_data[11]
            team_a_yellow_cards = shots_data[12]
            team_b_yellow_cards = shots_data[13]
            team_a_red_cards = shots_data[14]
            team_b_red_cards = shots_data[15]
            team_a_offsides = shots_data[16]
            team_b_offsides = shots_data[17]
            team_a_corners = shots_data[18]
            team_b_corners = shots_data[19]

            # Extract goal times
            team_a_goal_times = [span.text for span in soup.select('.imso_gs__left-team .liveresults-sports-immersive__game-minute span') if span.text.isdigit()]
            team_b_goal_times = [span.text for span in soup.select('.imso_gs__right-team .liveresults-sports-immersive__game-minute span') if span.text.isdigit()]
            
        
        team_a_goal_times_str = json.dumps(team_a_goal_times)
        team_b_goal_times_str = json.dumps(team_b_goal_times)

        stats_data.append([match_id[0], team_a_short, team_b_short, team_a_shots_on_target, team_b_shots_on_target, 
                    team_a_possession, team_b_possession, team_a_passes, team_b_passes, team_a_pass_accuracy, 
                    team_b_pass_accuracy, team_a_fouls, team_b_fouls, team_a_yellow_cards, team_b_yellow_cards, 
                    team_a_red_cards, team_b_red_cards, team_a_offsides, team_b_offsides, team_a_corners, 
                    team_b_corners, team_a_goal_times_str, team_b_goal_times_str])
        # Save statistics data to the database with the foreign key reference
       # save_statistics_to_database(stats_data)

def main():
    ascii_banner = pyfiglet.figlet_format("SCRAPING-FOOT")


    print(ascii_banner)
    global retry, max_retry
    retry += 1
    print(f"Attempt {retry} of {max_retry}")

    if retry > max_retry:
        print("Max retries exceeded.")
        return

    # Set up the database
    

    driver = None
    try:
        options = webdriver.ChromeOptions()
        options.headless = False
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(60)
        
        # ty peux changer le pays ici 
        url = "https://www.google.com/search?q=resultat equipe france football"
        driver.get(url)

        try:
            more_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[jsname="bHOicb"]'))
            )
            more_btn.click()
            print("Clicked 'More' button.")
        except TimeoutException:
            print("More button not found. Retrying...")
            driver.quit()
            return main()

        main_div = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "liveresults-sports-immersive__updatable-team-matches"))
        )

        scroll_component(driver, main_div)

        match_tiles = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "liveresults-sports-immersive__match-tile"))
        )
        print("Les éléments avec la classe 'liveresults-sports-immersive__match-tile' ont été trouvés.")

       


        """
        main_div = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "OcbAbf"))
        )
        """
        nombre_elements = len(match_tiles)

       # print(f"Nombre d'éléments trouvés : {nombre_elements}")

        driver.execute_script("window.scrollBy(0, -500);")


        match_of_day = []
        nombre=0
        file_counter = 1
       # for match_tile in match_tiles:
        for index, match_tile in enumerate(match_tiles, start=1):
            try:
                    tables = match_tile.find_elements(By.CLASS_NAME, 'KAIX8d')
                    nombre=nombre+1
                    table_contents = []
                    print("nombre  est ",nombre)

                    start_times = []
               
                    nested_divs = match_tile.find_elements(By.CSS_SELECTOR, 'div.imso-loa.imso-ani')
                    for nested_div in nested_divs:
                   
                        start_time = nested_div.get_attribute('data-start-time')
                   

                        if start_time:
                            start_times.append(start_time)


                    for i,table in enumerate(tables):
                            table_html = table.get_attribute('outerHTML')
                            table_contents.append(table_html)
                            time.sleep(5)
                            driver.execute_script("arguments[0].scrollIntoView();", table)


                            
                            time.sleep(2)
                            driver.execute_script("arguments[0].scrollIntoView();", table)

                            driver.execute_script("arguments[0].click();", table)

                            time.sleep(3)
                            nGzje_elements = WebDriverWait(driver, 20).until(
                                EC.presence_of_all_elements_located((By.CLASS_NAME, "nGzje"))
                            )

                            nGzje_elements = WebDriverWait(driver, 20).until(
                                EC.presence_of_all_elements_located((By.CLASS_NAME, "nGzje"))
                            )

                            try:
                                driver.execute_script("window.history.go(-1)")
                                time.sleep(1)
                            except TimeoutException:
                                print("Back button was not found or clickable in the given time.")

                            # Store nGzje_elements HTML content in a file
                            nGzje_html = [element.get_attribute('outerHTML') for element in nGzje_elements]
                            
                            soup = BeautifulSoup(nGzje_html[0], 'html.parser')

                            # save_html('\n'.join(nGzje_html), 'nGzje_elements.html')

                            day=55
                            unix_timestamp = start_times[i]
                            extract_info_from_html(soup, day,unix_timestamp)
                        #ici ici elnles commentaire en haut 

                            time.sleep(1)


                    
            except Exception as e:
                print("An error occurred:", str(e))
            

        

    except TimeoutException:
        print("Les éléments avec la classe 'liveresults-sports-immersive__match-tile' n'ont pas été trouvés.")
        driver.quit()
        return main()

    except Exception as e:
        print("An error occurred:", str(e))
        
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()
