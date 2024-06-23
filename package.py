def kill_chrome_process():
    import psutil
    for proc in psutil.process_iter(['name']):
        try:
            if 'chrome' in proc.info['name'].lower():
                print(f"Processus Chrome {proc.pid} fermé.")
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
        
def init_chrome():
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import WebDriverException
    from selenium import webdriver
    import os
    import time
    kill_chrome_process()
    local_app_data = os.environ['LOCALAPPDATA']
    user_data_directory = os.path.join(local_app_data, 'Google', 'Chrome', 'User Data')

    # Create ChromeOptions object
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    # Add the user data directory option
    chrome_options.add_argument(f"user-data-dir={user_data_directory}")
    attempt = 1
    delay_between_attempts = 1
    max_attempts = 100
    while attempt <= max_attempts:
        try:
            # Initialize the Chrome browser with options
            driver = webdriver.Chrome(options=chrome_options)           
            return driver
        except WebDriverException as e:
            print(f"Attempt {attempt}/{max_attempts}: Error opening Chrome - {str(e)}")

            # Close the browser window if it was opened
            if 'driver' in locals() and driver:
                driver.quit()

        # Increment the attempt count
        attempt += 1

        # Wait before trying again
        if attempt <= max_attempts:
            print(f"Waiting {delay_between_attempts} seconds before retrying...")
            time.sleep(delay_between_attempts)
        else:
            print("Maximum number of attempts reached. Unable to open the URL.")
            raise
        
def google_chrome(website_url):
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import WebDriverException
    from selenium import webdriver
    import os
    import time
    kill_chrome_process()
    local_app_data = os.environ['LOCALAPPDATA']
    user_data_directory = os.path.join(local_app_data, 'Google', 'Chrome', 'User Data')

    # Create ChromeOptions object
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    # Add the user data directory option
    chrome_options.add_argument(f"user-data-dir={user_data_directory}")
    attempt = 1
    delay_between_attempts = 1
    max_attempts = 100
    while attempt <= max_attempts:
        try:
            # Initialize the Chrome browser with options
            driver = webdriver.Chrome(options=chrome_options)

            # Navigate to the specified URL
            driver.get(website_url)

            # Wait for the page to load (you might need to adjust the waiting time)
            driver.implicitly_wait(30)
            
            return driver
        except WebDriverException as e:
            print(f"Attempt {attempt}/{max_attempts}: Error opening URL - {str(e)}")

            # Close the browser window if it was opened
            if 'driver' in locals() and driver:
                driver.quit()

        # Increment the attempt count
        attempt += 1

        # Wait before trying again
        if attempt <= max_attempts:
            print(f"Waiting {delay_between_attempts} seconds before retrying...")
            time.sleep(delay_between_attempts)
        else:
            print("Maximum number of attempts reached. Unable to open the URL.")
            raise
        
def install_package(nom_package):
    import subprocess
    import sys
    """
    Installe un package Python sur votre système.
    """
    # Vérifier si le package est déjà installé
    try:
        __import__(nom_package)
        print(f"{nom_package} est déjà installé.")
        return
    except ImportError:
        pass

    # Installer le package
    print(f"Installation de {nom_package}...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", nom_package])

    print(f"{nom_package} a été installé avec succès.")

install_package("selenium")    
install_package("psutil")