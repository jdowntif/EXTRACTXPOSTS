from package import install_package,google_chrome,init_chrome
from Xaccount import account,click_button
install_package("selenium")
install_package("bs4")
file_path_log = None

def time_now():
    from datetime import datetime
    global file_path_log
    # Obtenir la date et l'heure actuelles
    now = datetime.now()
    return now.strftime("%H:%M:%S:%f")[:-3]
    

    
def save_links(url,link_list,file_path):
    with open(file_path, 'a') as file:
        for link, datetime_str in link_list:
            full_url = f"https://x.com{link}"
            print(f"Link: {full_url}")
            print(f"Datetime: {datetime_str}")
            print()
            file.write(full_url + '\n')
        file.write(datetime_str + '\n')
        file.write(f"X: {url}\n")

def find_tag(driver,tag,attribu,attr_value):
    from bs4 import BeautifulSoup
    import time
    print(f"{time_now()} : find_tag(driver,{tag},{attribu},{attr_value})")
    # Nombre maximum de tentatives
    max_attempts = 10
    delay = 1
    # Boucle pour rechercher l'élément
    attempts = 0
    button = None
    while button is None and attempts < max_attempts:
            
        # Récupérer le contenu HTML de la page
        html_content = driver.page_source
        # Créer un objet BeautifulSoup à partir du contenu HTML
        soup = BeautifulSoup(html_content, "html.parser")

        # Rechercher l'élément <button> avec l'attribut attribu=attr_value
        button = soup.find(tag, {attribu: attr_value})
        
        # Incrémenter le nombre de tentatives
        attempts += 1

        # Attendre 1 seconde avant la prochaine tentative
        if attempts < max_attempts and button is None:
            print(f"{time_now()} : Élément non trouvé, nouvelle tentative dans", delay, "seconde(s)...")
            time.sleep(delay)
    # Vérifier si l'élément a été trouvé
    if button:
         print(f"{time_now()} : Élément <{tag}> avec l'attribut {attribu}='{attr_value}' a été trouvé.")       
         return True        
    else:
        print(f"{time_now()} : L'élément <{tag}> avec l'attribut {attribu}='{attr_value}' n'a pas été trouvé après", max_attempts, "tentatives.")
        return False
            
def fetch_content(driver):
    from bs4 import BeautifulSoup
    if find_tag(driver,"div","aria-label","Home timeline"):  
        try:
            # Récupérer le contenu HTML de la page
            html_content = driver.page_source
            # Utiliser BeautifulSoup pour analyser le contenu HTML
            soup = BeautifulSoup(html_content, 'html.parser')

            # Rechercher tous les éléments <span>
            span_elements = soup.find_all('span')

            # Vérifier si des éléments <span> ont été trouvés
            if not span_elements:
                print(f"{time_now()} : Aucun élément <span> n'a été trouvé.")
                return False
            else:
                # Afficher le texte de chaque élément <span>
                for index, span in enumerate(span_elements):
                    inner_html = ''.join(str(child) for child in span.children)
                    if "Account suspended" in inner_html:
                        print(f"{time_now()} : {inner_html}")
                        return True
        except Exception as e:
            print(f"{time_now()} : Erreur lors de la recherche des éléments <span>: {str(e)}")
            return False

def get_post(driver):
    from bs4 import BeautifulSoup
    try:      
        if find_tag(driver,"div","data-testid","cellInnerDiv"):
            print(f"{time_now()} : Posts Trouve")
            # Récupérer le contenu HTML de la page
            html_content = driver.page_source
            # Utiliser BeautifulSoup pour analyser le contenu HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            # Rechercher l'élément <span> contenant le texte spécifié
            posts = soup.find_all("div", {"data-testid": "cellInnerDiv"})
            if posts:
                print(f"{time_now()} : Posts Recupere")
                return posts
            else:
                print(f"{time_now()} : Posts Pas Recupere")
                return False
        else :
            print(f"{time_now()} : Posts Pas Trouve")
            return False 
    except AttributeError:
        print(f"{time_now()} : Erreur : Impossible de trouver les Posts.")
        return False
    except Exception as e:
        print(f"{time_now()} : Une erreur inattendue s'est produite :", e)
        return False
    
def Attribu_time(post):
    from bs4 import BeautifulSoup
    try:
        time_element = post.find("time")
        if time_element:
            timeattribut = time_element.get("datetime")
            
            # Récupérer l'élément parent de time_element
            parent_element = time_element.find_parent()

            # Récupérer la valeur de l'attribut 'href' si le parent est un lien <a>
            href_value = None
            if parent_element.name == 'a' and 'href' in parent_element.attrs:
                href_value = parent_element['href']
            return time_element, timeattribut, href_value
        else:
            print(f"{time_now()} : last élément <time> avec l'attribut datetime n'a été trouvé.")
            return None, None, None
    except Exception:
        print(f"{time_now()} : Erreur lors de l'analyse de last élément")
        return None, None, None
    
def get_link(posts,link_list):
    from bs4 import BeautifulSoup
    link_count = 0
    last_element = None
    last_datetime = None
    for post in posts:
        # Appeler la fonction pour obtenir l'élément <time> et sa valeur datetime
        time_element, datetime_value, link = Attribu_time(post)
        if time_element:
            last_element = time_element
            if [link, datetime_value] not in link_list:
                link_list.append([link, datetime_value])
                #print([link, datetime_value])
                last_datetime = datetime_value
                link_count += 1
    print(f"{time_now()} : {last_datetime}")
    return link_count, link_list,last_element    

def calculate_duration(link_list,days_threshold):
    from datetime import datetime, timezone
    # Récupérer la valeur de l'attribut "datetime"
    last_datetime_str = link_list[-1][1]
    # Convertir la valeur en objet datetime
    date_time = datetime.fromisoformat(last_datetime_str.replace("Z", "+00:00")).replace(tzinfo=timezone.utc)
    #print(date_time)
    # Obtenir la date actuelle
    now = datetime.now(timezone.utc)
    # Calculer la durée
    duration = now - date_time
    if duration.days < days_threshold:
        return True
    else:
        return False

def scroll_end(driver):
    import time
    from selenium.common.exceptions import NoSuchWindowException, NoSuchElementException
    try:
        from selenium.common.exceptions import NoSuchWindowException
        # Faire défiler l'élément dans la vue
        driver.execute_script("window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'});")
        # Attendre 5 secondes
        time.sleep(5)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Attendre 5 secondes
        time.sleep(5)
        return False
    except (NoSuchWindowException, NoSuchElementException) as e:
        print(f"{time_now()} : Error scroll_end : {str(e)}")
        return True

def socialContext(post):
    from bs4 import BeautifulSoup
    try:
        # Récupérer le parent 
        parent_element = post.parent
        # Remonter dans les parents jusqu'à trouver un élément "article" avec un attribut "aria-labelledby"
        while parent_element:
            tag_name = parent_element.name
            if tag_name == 'article' and parent_element.get_attribute('aria-labelledby'):
                print(f"{time_now()} : Parent article avec aria-labelledby trouvé.")
                return parent_element.find('span', {'data-testid': 'socialContext'}) is not None
            parent_element = parent_element.parent
        # Si aucun élément correspondant n'est trouvé, renvoyer None
        print(f"{time_now()} : Aucun élément parent article avec aria-labelledby n'a été trouvé.")
        return False
    except (AttributeError, TypeError) as e:
        print(f"{time_now()} : Une erreur est survenue : {e}")
        return False
    
def find_wrong(html_content):
    from bs4 import BeautifulSoup
    try:
        print(f"{time_now()} : find_wrong.")
        # Utiliser BeautifulSoup pour analyser le contenu HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        # Le texte à rechercher
        message = "Something went wrong. Try reloading."
        # Rechercher l'élément <span> contenant le texte spécifié
        span_element = soup.find('span', string=message)

        if span_element:
            print(f"{time_now()} : Something went wrong.")
            return True  # Retourner True pour indiquer que l'erreur a été trouvée
        else:
            return False  # Retourner False pour indiquer que l'erreur n'a pas été trouvée

    except Exception as e:
        print(f"{time_now()} : An error Something went wrong : {e}")
        return False  # Retourner False pour indiquer que l'erreur n'a pas été trouvée

def save_links(url,link_list,file_path):
    with open(file_path, 'a') as file:
        for link, datetime_str in link_list:
            full_url = f"https://x.com{link}"
            print(f"Link: {full_url}")
            print(f"Datetime: {datetime_str}")
            print()
            file.write(full_url + '\n')
        file.write(datetime_str + '\n')
        file.write(f"X: {url}\n")

def extraire_username(html):
    from bs4 import BeautifulSoup
    # Parse le HTML
    soup = BeautifulSoup(html, 'html.parser')

    # Trouve le div avec l'attribut data-testid="UserName"
    div = soup.find('div', {'data-testid': 'UserName'})
    if not div:
        return None

    # Cherche un span dans les enfants du div dont le texte commence par '@'
    span = div.find('span', string=lambda text: text and text.startswith('@'))
    if span:
        return span.text
    else:
        return None

def Follow(driver):
    profile = extraire_username(driver.page_source)
    if profile:
        print(f"{time_now()} : Page profile : {profile}")
        attr_value = f"Follow {profile}"
    else:
        return False
    
    if find_tag(driver,"button","aria-label",attr_value):
        print(f"{time_now()} : button Follow Found")
    else:
        return False
    
    if click_button(driver,"button","aria-label",attr_value):
        print(f"{time_now()} : button Follow click")
    else:
        return False
    
#scrapp chrome and extract urls
def scrap_compte(url,driver,file_path_save,days_threshold,index):
    link_list = []
    scroll_echec = False
    
    print(f"{time_now()} : Check Account suspended")
    if fetch_content(driver):
        keep_going = False
        saving = False
    else:
        keep_going = True
        saving = True
    
    print(f"{time_now()} : Check Follow button")
    Follow(driver)
    
    num_days = 10
    count_try = 0
    count_scroll = 0
    while keep_going:
        print(f"{time_now()} : get post")
        posts = get_post(driver)
        if posts:
            print(f"{time_now()} : get links")
            link_count, link_list, post = get_link(posts,link_list)
            print(f"{time_now()} : Nombre de Lien Trouve : {link_count}")
            if not post:
                print(f"{time_now()} : No end post")
                keep_going = False
            if link_count > 0:
                count_try = 0
                print(f"{time_now()} : check calculate_duration")
                if calculate_duration(link_list,days_threshold):
                    print(f"{time_now()} : calculate_duration ok. scroll_end")
                    scroll_echec = scroll_end(driver)
                else:
                    print(f"{time_now()} : calculate_duration no. check socialContext")
                    if socialContext(post):
                        print(f"{time_now()} : socialContext ok. scroll_end")
                        scroll_echec = scroll_end(driver)
                    else:
                        print(f"{time_now()} : socialContext No. old post")
                        keep_going = False
            else :
                count_try += 1
                print(f"{time_now()} : count_try : {count_try}")
                if count_try < 10 :
                    print(f"{time_now()} : count_try ok. scroll_end")
                    scroll_echec = scroll_end(driver)      
                else:
                    print(f"{time_now()} : max try")
                    keep_going = False
        else:
            count_scroll += 1
            print(f"{time_now()} : count_scroll : {count_scroll}")
            if count_scroll < 10:
                print(f"{time_now()} : count_scroll ok. scroll_end")
                scroll_echec = scroll_end(driver)
            else:
                print(f"{time_now()} : End. Aucun posts")
                keep_going = False
        print(f"{time_now()} : Check wrong")
        wrong = find_wrong(driver.page_source)
        if wrong or scroll_echec:
            while wrong:
                print(f"{time_now()} : find wrong status : {wrong}")
                driver = account(url,driver)
                wrong = find_wrong(driver.page_source)
            print(f"{time_now()} : scroll_echec : {scroll_echec}")
            index -= 1
            saving = False
            keep_going = False
    ordre = index + 1
    if saving:
        save_links(url,link_list,file_path_save)
    return ordre,driver    
        
#extract url from filname 
def open_url(file_name,days_threshold):
    from selenium import webdriver
    from selenium.common.exceptions import WebDriverException
    import os
    import subprocess
    from datetime import datetime
    global file_path_log
    # Obtenir la date et l'heure actuelles
    now = datetime.now()
    file_name_save = f"links_{now.strftime('%Y%m%d_%H%M%S')}.txt"
    file_name_log = f"logs_{now.strftime('%Y%m%d_%H%M%S')}.txt"
    # Chemin du fichier dans le même répertoire que le script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path_save = os.path.join(script_dir, file_name_save)
    file_path_log = os.path.join(script_dir, file_name_log)
    # Chemin du fichier dans le même répertoire que le script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path_open = os.path.join(script_dir, file_name)
    file_path_wrong = os.path.join(script_dir, "CompteNo.txt")
    # Lecture des URLs à partir du fichier 'comptetwitter.txt'
    with open(file_path_open, 'r') as file:
        urls_to_check = file.readlines()
        urls_to_check = [url.strip() for url in urls_to_check]
    # Parcourir chaque URL et vérifier s'il y a une erreur
    index = 0
    driver = init_chrome()
    wrong_try = 0
    while index < len(urls_to_check):
        url = urls_to_check[index]
        try:    
            driver.get(url)
        except WebDriverException:
            driver = google_chrome(url)
        print(f"{time_now()} : Google Chrome : {url}")
        wrong_stat = index
        index,driver = scrap_compte(url,driver,file_path_save,days_threshold,index)
        if index == wrong_stat:
            wrong_try += 1
            print(f"{time_now()} :  {url} wrong try {wrong_try}")
        else:
            wrong_try = 0
        if wrong_try == 10 :
            index += 1
            wrong_try = 0
            print(f"{time_now()} : Max wrong try")
            with open(file_path_wrong, 'a') as file:
                file.write(url + '\n')
            
    subprocess.run(['explorer.exe', file_path_save])
    return driver

days_threshold = 300           
file_name = 'comptetwitter.txt'            
driver = open_url(file_name,days_threshold)        
print(f"{time_now()} : Goodbye!")


