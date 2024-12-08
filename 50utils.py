import os
import re
import time
import json
import base64
import threading
import subprocess as sp
import xml.etree.ElementTree as ET
import urllib.parse
import requests
import psutil
import pwinput
import lxml
import webbrowser
from bs4 import BeautifulSoup
from tabulate import tabulate
from colorama import Fore
from datetime import datetime

strRealmIP = Fore.GREEN + "  Current Realm IP: "
strHelp = f"""{Fore.MAGENTA}
 ██╗  ██╗███████╗██╗     ██████╗       
 ██║  ██║██╔════╝██║     ██╔══██╗      
 ███████║█████╗  ██║     ██████╔╝      
 ██╔══██║██╔══╝  ██║     ██╔═══╝       
 ██║  ██║███████╗███████╗██║           
 ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝           
    {Fore.WHITE}
    1. REALM IP FAQ
    2. EXALT DATA FAQ
    3. IGN CHECKER FAQ
    4. DAILY COLLECTOR FAQ

    0. BACK

"""
strNoFAQ = f"{Fore.YELLOW}Nothing to see here{Fore.WHITE}"

strInvalid = f'\n  Invalid option \n' + Fore.WHITE
strInfo = f"""{Fore.MAGENTA}
 ██╗███╗   ██╗███████╗ ██████╗         
 ██║████╗  ██║██╔════╝██╔═══██╗        
 ██║██╔██╗ ██║█████╗  ██║   ██║        
 ██║██║╚██╗██║██╔══╝  ██║   ██║        
 ██║██║ ╚████║██║     ╚██████╔╝        
 ╚═╝╚═╝  ╚═══╝╚═╝      ╚═════╝ 
{Fore.WHITE}
    Version: 
    └─ publicBeta-1.0
    
    Creator:
    └─ buddingromance
       └─ Discord: buddingromance                           (1)
       └─ Discord Server: discord.gg/creatures              (2)
       └─ YouTube: buddingromance                           (3)
       └─ GitHub: budding-romance                           (4)
       └─ Website: fifty.website                            (5)
       └─ DogeBawt: discord.gg/autododge                    (6)

    Contributors:
    └─ Contribute to the software on GitHub and you'll be listed here :)

    BACK                                                    (0)
"""

strMenu = f"""{Fore.MAGENTA}
 ███╗   ███╗███████╗███╗   ██╗██╗   ██╗
 ████╗ ████║██╔════╝████╗  ██║██║   ██║
 ██╔████╔██║█████╗  ██╔██╗ ██║██║   ██║
 ██║╚██╔╝██║██╔══╝  ██║╚██╗██║██║   ██║
 ██║ ╚═╝ ██║███████╗██║ ╚████║╚██████╔╝
 ╚═╝     ╚═╝╚══════╝╚═╝  ╚═══╝ ╚═════╝ 
{Fore.WHITE}
    1. CURRENT REALM IP
    2. DISPLAY CURRENT EXALT DATA
    3. CHECK IGN AVAILABILITY
    4. IMITATE IN-GAME LOGIN (DAILY COLLECTOR)
    5. REALMEYE TOOLS
    6. CHECK IN-GAME GUILD INFO

    8. ADD ACCOUNTS TO THE CONFIG
    9. REMOVE OR EDIT ACCOUNTS
    
    H. HELP
    I. INFO

    0. EXIT
"""
DEFAULT_CONFIG = {
    "token": "",
    "ignCheckerAccounts": [],
    "daily": [],
    "other": [],
    "realmeye": []
}

TITLES = [
    "🗡 50utils by buddingromance - Check out the INFO tab to support me!",
    "🗡 50utils by buddingromance - Open the HELP menu if you're stuck.",
    "🗡 50utils by buddingromance - You can report bugs on my Discord server.",
    "🗡 50utils by buddingromance - Feel free to DM me suggestions!",
    "🗡 50utils by buddingromance - Online IGN checker ^& daily collector: fifty.website"
]

errNotOpen =  f"{Fore.RED}Game not open.{Fore.WHITE}"

CFG_PATH = "config.json"

p = "none"
cmdRealmIP = "netstat -an | findstr :2050"

# functions

def _clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def prompt_input(prompt, allowed_values=None):
    while True:
        user_input = input(prompt).strip().upper()
        if allowed_values is None or user_input in allowed_values:
            return user_input
        print(f"{Fore.RED}  Invalid input, try again.{Fore.WHITE}")

def load_config():
    if not os.path.isfile(CFG_PATH):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    try:
        with open(CFG_PATH, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"{Fore.RED}  Error loading configuration from {CFG_PATH}.{Fore.WHITE}")
        return DEFAULT_CONFIG

def save_config(config_data):
    with open(CFG_PATH, 'w') as file:
        json.dump(config_data, file, indent=4)

def load_accounts(acctype):
    try:
        with open(CFG_PATH, 'r') as file:
            data = json.load(file)
            if acctype == "daily":
                accounts = data.get('daily', [])
            elif acctype == "ign":
                accounts = data.get('ignCheckerAccounts', [])
            elif acctype == "other":
                accounts = data.get('other', [])
            elif acctype == "realmeye":
                accounts = data.get('realmeye', [])
            else:
                menu(f"\n{Fore.RED}  Something went wrong. Check your config file.\n{Fore.WHITE}")
        return accounts
    except FileNotFoundError:
        save_config(DEFAULT_CONFIG)
        menu(f"\n{Fore.RED}  File '{CFG_PATH}' not found.\n{Fore.YELLOW}  New config file created.{Fore.WHITE}\n")
    except json.JSONDecodeError:
        save_config(DEFAULT_CONFIG)
        menu(f"\n{Fore.RED}  Error decoding JSON from file.\n{Fore.YELLOW}  New config file created.{Fore.WHITE}\n")
    
def format_time_difference(delta):
    seconds = int(delta.total_seconds())
    if seconds < 60:
        return f"{seconds} seconds ago"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minutes ago"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours} hours ago"
    else:
        days = seconds // 86400
        return f"{days} days ago"

def display_accounts(accounts):
    for idx, account in enumerate(accounts, start=1):
        label = account.get('label', 'No Label')
        if label != 'No Label':
            print(f"{idx}. {label} (Account Type: {account.get('accountType', 'Unknown')})")
        else:
            print(f"{idx}. {account.get('username')} (Account Type: RealmEye)")

def select_account(accounts):
    while True:
        try:
            choice = int(input("\nSelect: ")) - 1
            if 0 <= choice < len(accounts):
                selected_account = accounts[choice]
                guid = selected_account.get('guid', 'No GUID')
                username = selected_account.get("username", 'No Username')
                password = selected_account.get('password', 'No Password')
                label = selected_account.get('label', 'No Label')
                if label != 'No Label':
                    return guid, password, label
                else:
                    return username, password
            else:
                if choice + 1 == 0:
                    menu()
                else:
                    print(f"\n{Fore.RED}  Invalid number. Try again.{Fore.WHITE}")
        except ValueError:
            print(f"\n{Fore.YELLOW}  Please enter a valid number.{Fore.WHITE}")

def get_access_token(guid, password, token_hex, headers):
    verify_url = f'https://www.realmofthemadgod.com/account/verify?guid={urllib.parse.quote(guid)}&password={password}&clientToken={token_hex}'
    try:
        verify_response = requests.get(verify_url, headers=headers)
        verify_response.raise_for_status()
        if "<Error>WebChangePasswordDialog.passwordError</Error>" in verify_response.text:
            return None, f"Invalid Account Credentials for {guid}."
        soup = BeautifulSoup(verify_response.text, 'html.parser')
        access_token_tag = soup.find('accesstoken')
        if not access_token_tag:
            return None, f"Failed to retrieve access token. HTML source:\n{verify_response.text}"
        return access_token_tag.text, None
    except requests.RequestException as e:
        return None, f"Error in HTTP request: {e}"

def verify_access_token(access_token, token_hex, headers):
    access_token_encoded = requests.utils.quote(access_token)
    verify_url = f'https://www.realmofthemadgod.com/account/verifyAccessTokenClient?game_net=Unity&play_platform=Unity&game_net_user_id=&clientToken={token_hex}&accessToken={access_token_encoded}'
    try:
        verify_response = requests.get(verify_url, headers=headers)
        verify_response.raise_for_status()
        return None
    except requests.RequestException as e:
        return f"Error during access token verification: {e}"

def char_list(access_token, headers):
    char_url = 'https://www.realmofthemadgod.com/char/list'
    data = {
        'do_login': "true",
        'accessToken': access_token,
        'game_net': "Unity",
        "play_platform": "Unity",
        "game_net_user_id": ""
    }
    try:
        response = requests.post(char_url, headers=headers, data=data)
        response.raise_for_status()
        return response.text
    except Exception as e:
        return None
    
def collect_free_box(box_id, access_token, headers):
    url = 'https://www.realmofthemadgod.com/account/purchasePackage'
    data = {
        'boxId': box_id,
        'quantity': '1',
        'price': '0',
        'currency': '0',
        'location': 'Deals',
        'accessToken': access_token,
        'game_net': "Unity",
        "play_platform": "Unity",
        "game_net_user_id": ""
    }
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response.text
    except Exception as e:
        return None

def getProc():
    p = errNotOpen
    PROCNAME = "RotMG Exalt.exe"
    for proc in psutil.process_iter():
        if proc.name() == PROCNAME:
            p = proc
    return p

def getData():
    d = getProc()
    if d == errNotOpen:
        str = '\n  error: '+d+'\n'
        return str
    else:
        pData = d.cmdline()[1]
        r = re.compile(r'\w{1,}\:\w{1,}\={1,2}')
        arr = r.findall(pData)
        str = ""
        for data in arr:
            rW = re.compile(r'\w+\={1,2}')
            description = re.match(r'\w+\:', data)
            baseEncoded = rW.findall(data)
            if description != "token:":
                strvar = " "+base64.b64decode(baseEncoded[0]).decode("utf-8")+'\n'
            else:
                strvar = " "+baseEncoded[0]+'\n'
            str = str+'\n  '+description.group(0)+strvar
        return str
        
    
def getRealmIP():
    output = sp.getoutput(cmdRealmIP)
    frip = output.splitlines()[-1][32:]
    ip = re.match(r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}', frip)
    if ip and ip.group(0) == "0.0.0.0":
        strIP = f'\n  RotMG is not open.\n  If this shows up with the game open,\n  please DM buddingromance on discord\n{Fore.WHITE}'
    else:
        strIP = f"\n{strRealmIP}{ip.group(0)}\n{Fore.WHITE}"

    return strIP

def check_and_update_token():
    try:
        with open(CFG_PATH, 'r') as file:
            data = json.load(file)

        token = data.get('token', '')
        if not token:
            token = os.urandom(40).hex()
            data['token'] = token
            
            with open(CFG_PATH, 'w') as file:
                json.dump(data, file, indent=4)
            
            print(f"{Fore.YELLOW}\n  New token generated: {token}\n{Fore.WHITE}")
            return token
        else:
            return token

    except FileNotFoundError:
        save_config(DEFAULT_CONFIG)
        return menu(f"\n{Fore.RED}  File '{CFG_PATH}' not found.\n{Fore.YELLOW}  New config file created.{Fore.WHITE}\n")
    except json.JSONDecodeError:
        save_config(DEFAULT_CONFIG)
        return menu(f"\n{Fore.RED}  Error decoding JSON from file.\n{Fore.YELLOW}  New config file created.{Fore.WHITE}\n")

def parseGuild(g, p, label):
    token_hex = check_and_update_token()
    guid = g
    password = p

    headers = {
        "Host": "www.realmofthemadgod.com",
        "User-Agent": "UnityPlayer/2019.3.14f1 (UnityWebRequest/1.0, libcurl/7.52.0-DEV)",
        "Accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Unity-Version": "2019.3.14f1"
    }

    access_token, error = get_access_token(guid, password, token_hex, headers)
    if error:
        return error

    error = verify_access_token(access_token, token_hex, headers)
    if error:
        return error

    try:
        guild_list_url = 'https://www.realmofthemadgod.com/guild/listMembers'
        guild_list_data = {
            'targetName': '',
            'accessToken': access_token,
            'game_net': "Unity",
            "play_platform": "Unity",
            "game_net_user_id": ""
        }
        guild_list_response = requests.post(guild_list_url, headers=headers, data=guild_list_data)
        guild_list_response.raise_for_status()
        guild_xml = guild_list_response.text

        guild_board_url = 'https://www.realmofthemadgod.com/guild/getBoard'
        guild_board_data = {
            'accessToken': access_token,
            'game_net': "Unity",
            "play_platform": "Unity",
            "game_net_user_id": ""
        }
        guild_board_response = requests.post(guild_board_url, headers=headers, data=guild_board_data)
        guild_board_response.raise_for_status()
        guild_board_text = guild_board_response.text

        try:
            guild_calendar_root = ET.fromstring(guild_xml)
            guild_members_list = []
            increment = 1
            for member in guild_calendar_root.findall('.//Member'):
                name_tag = member.find('Name')
                rank_tag = member.find('Rank')
                fame_tag = member.find('Fame')
                last_login_tag = member.find('LastLogin')
                online_tag = member.find('Online')

                member_name = name_tag.text.strip() if name_tag is not None else "N/A"
                member_rank = rank_tag.text.strip() if rank_tag is not None else "N/A"
                member_fame = fame_tag.text.strip() if fame_tag is not None else "N/A"
                
                if member_rank.isdigit():
                    rank_value = int(member_rank)
                    if rank_value == 40:
                        member_rank = "Founder"
                    elif rank_value == 30:
                        member_rank = "Leader"
                    elif rank_value == 20:
                        member_rank = "Officer"
                    elif rank_value == 10:
                        member_rank = "Member"
                    elif rank_value == 0:
                        member_rank = "Initiate"

                # set Last Login to Online if online_tag exists
                if last_login_tag is not None:
                    last_login_str = last_login_tag.text.strip()
                    last_login_dt = datetime.fromisoformat(last_login_str)  # parse the timestamp
                    time_difference = datetime.now() - last_login_dt  # calculate the difference
                    member_last_login = format_time_difference(time_difference)
                elif online_tag is not None:
                    member_last_login = "Online"
                else:
                    member_last_login = "N/A"

                guild_members_list.append([increment, member_name, member_rank, member_fame, member_last_login])
                increment += 1

            # formatted table
            guild_list_text = tabulate(guild_members_list, headers=["#", "Name", "Rank", "Account Fame", "Last Login"], tablefmt="grid")

        except ET.ParseError:
            return "Failed to parse guild calendar XML."

        while True:
            choice = input("\nChoose an option:\n 1. Display Guild Board\n 2. Display Guild Members\n 0. Back\n\nSelect: ")
            if choice == "0":
                menu()
                break
            elif choice == "1":
                print("\nGuild Board:\n", guild_board_text)
            elif choice == "2":
                print("\nGuild Members:\n", guild_list_text)
            else:
                print("Invalid choice. Please try again.")

    except requests.RequestException as e:
        return f"Error in HTTP request: {e}"

def nameCheck(g, p, name):
    token_hex = check_and_update_token()
    guid = g
    password = p

    # get access token
    url = f'https://www.realmofthemadgod.com/account/verify?guid={guid}&password={password}&clientToken={token_hex}'
    
    headers = {
        "Host": "www.realmofthemadgod.com",
        "User-Agent": "UnityPlayer/2019.3.14f1 (UnityWebRequest/1.0, libcurl/7.52.0-DEV)",
        "Accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Unity-Version": "2019.3.14f1"
    }

    access_token, error = get_access_token(guid, password, token_hex, headers)
    if error:
        print(f"{Fore.RED}\n{error}{Fore.WHITE}")
        return

    error = verify_access_token(access_token, token_hex, headers)
    if error:
        print(f"{Fore.RED}\n{error}{Fore.WHITE}")
        return

    # sends the invite request only if the name is taken
    url_char = 'https://www.realmofthemadgod.com/friends/requestFriend'
    data = {
        'targetName': name,
        'accessToken': access_token,
        'game_net': "Unity",
        'play_platform': "Unity",
        'game_net_user_id': ""
    }

    try:
        friend_request_response = requests.post(url_char, headers=headers, data=data)
        friend_request_response.raise_for_status()
    except requests.RequestException as e:
        return f"{Fore.RED}  Error during friend request: {e}{Fore.WHITE}"

    friend_request_html = friend_request_response.text

    if friend_request_html == "<Error>Only named players can be added as friends.</Error>":
        print(f" {Fore.GREEN}conga rats! IGN {Fore.WHITE}{name}{Fore.GREEN} is NOT taken{Fore.WHITE}")
        return
    elif friend_request_html == "<Success/>":
        print(f"{Fore.RED}  IGN {Fore.WHITE}{name}{Fore.RED} is taken{Fore.WHITE}")
        return
    else:
        print(f"{Fore.RED}  Error: {Fore.YELLOW}{friend_request_html}{Fore.WHITE}")
        return

def realmeye_login(username, password):
    url = 'https://www.realmeye.com/login'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://www.realmeye.com",
        "Accept": "*/*",
    }
    
    data = {
        "username": username,
        "bindToIp": "f",
        "password": password
    }
    session = requests.Session()
    try:
        response = session.post(url, headers=headers, data=data)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"Error during login: {e}"

    if response.text:
        if "session" in session.cookies:
            session_cookie = session.cookies.get("session")
            return session_cookie
        else:
            return "Session cookie not found in response."
    else:
        return "Login successful but no content returned."

def dailyLogin(g, p, label, box_ids):
    token_hex = check_and_update_token()
    guid = g
    password = p

    # get access token
    url = f'https://www.realmofthemadgod.com/account/verify?guid={guid}&password={password}&clientToken={token_hex}'
    
    headers = {
        "Host": "www.realmofthemadgod.com",
        "User-Agent": "UnityPlayer/2019.3.14f1 (UnityWebRequest/1.0, libcurl/7.52.0-DEV)",
        "Accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Unity-Version": "2019.3.14f1"
    }

    access_token, error = get_access_token(guid, password, token_hex, headers)
    if error:
        print(f"{Fore.RED}\n{error}{Fore.WHITE}")
        return

    error = verify_access_token(access_token, token_hex, headers)
    if error:
        print(f"{Fore.RED}\n{error}{Fore.WHITE}")
        return

    char_data = char_list(access_token, headers)
    if not char_data or "<Error>" in char_data:
        print(f"{Fore.RED}\nFailed to fetch character data for {label}.{Fore.WHITE}")
        return

    if box_ids.upper() != "N":
        box_ids_list = box_ids.split(',')
        for box_id in box_ids_list:
            box_id = box_id.strip()
            box_result = collect_free_box(box_id, access_token, headers)
            if box_result and "<Error>" not in box_result:
                print(f"{Fore.GREEN}\nDaily reward (Free Box ID: {box_id}) successfully claimed.{Fore.WHITE}")
            else:
                print(f"{Fore.YELLOW}\nFailed to claim reward or no reward available for Box ID: {box_id}.{Fore.WHITE}")

    menu(f"{Fore.GREEN}\nDaily login completed for {label}.{Fore.WHITE}")

def freeBoxes(g, p):
    token_hex = check_and_update_token()
    guid = g
    password = p

    # get access token
    url = f'https://www.realmofthemadgod.com/account/verify?guid={guid}&password={password}&clientToken={token_hex}'
    
    headers = {
        "Host": "www.realmofthemadgod.com",
        "User-Agent": "UnityPlayer/2019.3.14f1 (UnityWebRequest/1.0, libcurl/7.52.0-DEV)",
        "Accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Unity-Version": "2019.3.14f1"
    }

    access_token, error = get_access_token(guid, password, token_hex, headers)
    if error:
        print(f"{Fore.RED}\n{error}{Fore.WHITE}")
        return

    error = verify_access_token(access_token, token_hex, headers)
    if error:
        print(f"{Fore.RED}\n{error}{Fore.WHITE}")
        return

    url = 'https://www.realmofthemadgod.com/shop/deals'
    
    dataBox = {
        'accessToken': access_token,
        'game_net': "Unity",
        "play_platform": "Unity",
        "game_net_user_id": "",
        "version": 1.0
    }

    headers = {
        "Host": "www.realmofthemadgod.com",
        "User-Agent": "UnityPlayer/2019.3.14f1 (UnityWebRequest/1.0, libcurl/7.52.0-DEV)",
        "Accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Unity-Version": "2019.3.14f1"
    }

    try:
        response = requests.post(url, data=dataBox, headers=headers)
        response.raise_for_status()
        root = ET.fromstring(response.text)
        packages = root.findall(".//Package")
        
        free_packages_found = False
        for package in packages:
            price_element = package.find(".//Price")
            if price_element is not None and 'amount' in price_element.attrib:
                amount = price_element.attrib['amount']
                if amount == "0":
                    free_packages_found = True
                    package_title = package.attrib.get('title', 'No title')
                    package_id = package.attrib.get('id', 'Unknown ID')
                    start_time = package.find(".//StartTime").text if package.find(".//StartTime") else 'N/A'
                    end_time = package.find(".//EndTime").text if package.find(".//EndTime") else 'N/A'
                    print(f"{Fore.GREEN}Free Package: {package_title} (ID: {package_id}){Fore.WHITE}")
                    print(f"Start Time: {start_time} | End Time: {end_time}")
        
        if not free_packages_found:
            print(f"{Fore.YELLOW}No free packages found.{Fore.WHITE}")
        
    except requests.RequestException as e:
        print(f"{Fore.RED}Error in HTTP request: {e}{Fore.WHITE}")

def realmeye_guild(username, password):
    guild_name = input("Guild Name: ")
    session_cookie = realmeye_login(username, password)
    if not session_cookie:
        return "Failed to retrieve session cookie."

    url = f'https://www.realmeye.com/guild/{guild_name}'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Accept": "text/html",
        "Referer": f'https://www.realmeye.com/player/{username}',
        "Accept-Language": "en",
        "Cookie": f"session={session_cookie}; gdprCookiePolicyAccepted=true"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        if 'text/html' not in response.headers.get('Content-Type', ''):
            print(f"Unexpected Content-Type: {response.headers.get('Content-Type')}")
            return None

        soup = BeautifulSoup(response.text, 'lxml')

        members_list = []
        member_rows = soup.select("table#f tbody tr")
        
        for row in member_rows:
            name_cell = row.find("td")
            if name_cell:
                member_name = name_cell.get_text(strip=True)
                member_rank = row.find_all("td")[1].get_text(strip=True)

                fame_cell = row.find_all("td")[2]
                if fame_cell and fame_cell.find('a'):
                    fame_value = fame_cell.get_text(strip=True)
                    member_fame = f"{int(fame_value):,}"
                else:
                    member_fame = "Private Fame"

                members_list.append((member_name, member_rank, member_fame))

        print(tabulate(members_list, headers=["Name", "Guild Rank", "Fame"], tablefmt="pretty")+"\n")
    except requests.RequestException as e:
        print(f"Error during GET request: {e}")
        return None
    return []

def realmeye():
    accounts = load_accounts("realmeye")
    
    if not accounts:
        return menu(f"{Fore.RED}\n  No accounts to display.{Fore.WHITE}")
    
    display_accounts(accounts)
    
    username, password = select_account(accounts)
    print("\n 1. Show Guild Members\n 2. Compare an In-Game Guild List with RealmEye (not finished yet)\n\n 0. BACK\n")
    while True:
        choice = prompt_input("Select: ", allowed_values={"1", "2", "0"})
        if choice == "0":
            menu()
            break
        elif choice == "1":
            realmeye_guild(username, password)
        elif choice == "2":
            print("\nThis function is not finished yet. I'll push it once it looks good enough.")
        else:
            return []

def gParse():
    accounts = load_accounts("other")
    
    if not accounts:
        return menu(f"{Fore.RED}\n  No accounts to display.{Fore.WHITE}")
    
    display_accounts(accounts)
    guid, password, label = select_account(accounts)
    return parseGuild(guid, password, label)

def ign():
    accounts = load_accounts("ign")
    
    if not accounts:
        return menu(f"{Fore.RED}\n  No accounts to display.{Fore.WHITE}")
    
    display_accounts(accounts)
    
    guid, password, label = select_account(accounts)
    print("\n 0. BACK\n")
    while True:
        name = input("IGN: ")
        if name == "0":
            menu()
            break
        else:
            nameCheck(guid, password, name)

def daily():
    accounts = load_accounts("daily")
    
    if not accounts:
        return menu(f"{Fore.RED}\n  No accounts to display.{Fore.WHITE}")
    
    display_accounts(accounts)
    
    guid, password, label = select_account(accounts)
    while True:
        print("\n 1. View Available Free Boxes\n 2. Collect Free Boxes & Log In \n 3. Skip Claiming And Log In\n\n 0. BACK\n")
        choice = input("Select: ")
        if choice == "1":
            freeBoxes(guid, password)
        elif choice == "2":
            box_ids = input("\nFree Box IDs (Separate with commas if multiple): ").strip()
            if box_ids == "0":
                menu()
                break
            else:
                dailyLogin(guid, password, label, box_ids)
                break
        elif choice == "3":
            dailyLogin(guid, password, label, "N")
            break
        elif choice == "0":
            menu()
            break

def appendCfg(newData, parent, label):
    with open(CFG_PATH,'r+') as file:
        fileData = json.load(file)
        fileData[parent].append(newData)
        file.seek(0)
        print(json.dump(fileData, file, indent = 4))
        file.close()
        menu(f"{Fore.GREEN}\n  {label} {Fore.YELLOW}({parent}){Fore.GREEN} successfully added.{Fore.WHITE}\n")

def manageAccounts():
    try:
        with open(CFG_PATH, 'r') as file:
            file_data = json.load(file)
    except FileNotFoundError:
        print(f"{Fore.RED}Error: Configuration file not found.{Fore.WHITE}")
        return
    except json.JSONDecodeError:
        print(f"{Fore.RED}Error: Invalid configuration file format.{Fore.WHITE}")
        return

    # Display all accounts (including account type and label)
    print("\nAvailable Accounts:")
    account_types = ["ignCheckerAccounts", "daily", "realmeye", "other"]
    for account_type in account_types:
        if account_type in file_data:
            print(f"\n{Fore.YELLOW}{account_type} Accounts:{Fore.WHITE}")
            for i, account in enumerate(file_data[account_type]):
                # Safely access 'label' (use 'username' if 'label' is missing)
                label = account.get('label', account.get('username', 'No label'))
                account_type_name = account.get('accountType', 'No account type')
                print(f" {i+1}. {label} ({account_type_name})")

    print("\nOptions:")
    print(" 1. Edit Account")
    print(" 2. Remove Account")
    print(" 0. BACK\n")

    while True:
        option = input(f"Select an option: ")

        if option == "1":
            print(f"\nSelect the account type to edit:")
            print(" 1. ignCheckerAccounts")
            print(" 2. daily")
            print(" 3. realmeye")
            print(" 4. other\n")

            account_type_choice = input("Enter the number of the account type: ")
            account_type_mapping = {"1": "ignCheckerAccounts", "2": "daily", "3": "realmeye", "4": "other"}

            if account_type_choice in account_type_mapping:
                account_type = account_type_mapping[account_type_choice]
            else:
                print(f"{Fore.RED}Invalid account type selection.{Fore.WHITE}")
                continue

            if account_type not in file_data:
                print(f"{Fore.RED}No accounts available in this type.{Fore.WHITE}")
                continue

            print(f"\n{Fore.YELLOW}Select an account to edit:{Fore.WHITE}")
            for i, account in enumerate(file_data[account_type]):
                label = account.get('label', account.get('username', 'No label'))
                print(f"{i+1}. {label}")

            account_index = int(input(f"Select an account (1-{len(file_data[account_type])}): ")) - 1
            if 0 <= account_index < len(file_data[account_type]):
                account = file_data[account_type][account_index]

                print(f"\nEditing {account.get('label', 'No label')} ({account.get('accountType', 'No account type')})")

                account['label'] = input(f"Enter new label (current: {account.get('label', 'No label')}): ") or account.get('label', '')
                account['guid'] = input(f"Enter new GUID (current: {account.get('guid', 'No GUID')}): ") or account.get('guid', '')
                account['password'] = pwinput.pwinput(prompt=f"Enter new password (current: {account.get('password', 'No password')}): ") or account.get('password', '')

                with open(CFG_PATH, 'w') as file:
                    json.dump(file_data, file, indent=4)

                print(f"{Fore.GREEN}Account updated successfully.{Fore.WHITE}")
            else:
                print(f"{Fore.RED}Invalid account selection.{Fore.WHITE}")

        elif option == "2":
            print(f"\nSelect the account type to remove:")
            print(" 1. ignCheckerAccounts")
            print(" 2. daily")
            print(" 3. realmeye")
            print(" 4. other\n")

            account_type_choice = input("Enter the number of the account type: ")
            account_type_mapping = {"1": "ignCheckerAccounts", "2": "daily", "3": "realmeye", "4": "other"}

            if account_type_choice in account_type_mapping:
                account_type = account_type_mapping[account_type_choice]
            else:
                print(f"{Fore.RED}Invalid account type selection.{Fore.WHITE}")
                continue

            if account_type not in file_data:
                print(f"{Fore.RED}No accounts available in this type.{Fore.WHITE}")
                continue

            print(f"\n{Fore.YELLOW}Select an account to remove:{Fore.WHITE}")
            for i, account in enumerate(file_data[account_type]):
                label = account.get('label', account.get('username', 'No label'))
                print(f" {i+1}. {label}")
            print("\n")
            account_index = int(input(f"Select an account (1-{len(file_data[account_type])}): ")) - 1
            if 0 <= account_index < len(file_data[account_type]):
                account = file_data[account_type][account_index]
                confirm = input(f"Are you sure you want to remove the account '{account.get('label', 'No label')}'? (y/n): ")
                if confirm.lower() == "y":
                    file_data[account_type].pop(account_index)

                    with open(CFG_PATH, 'w') as file:
                        json.dump(file_data, file, indent=4)

                    print(f"{Fore.GREEN}Account removed successfully.{Fore.WHITE}")
                else:
                    print(f"{Fore.YELLOW}Account removal canceled.{Fore.WHITE}")
            else:
                print(f"{Fore.RED}Invalid account selection.{Fore.WHITE}")

        elif option == "0":
            return menu()

        else:
            print(f"{Fore.RED}Invalid option, please try again.{Fore.WHITE}")


def setup():
    print("\n 1. IGN Checker Account\n 2. Daily Collector Account\n 3. RealmEye\n 4. Other\n\n 0. BACK\n")
    while True:
        option = prompt_input("Select: ", allowed_values={"1", "2", "3", "4", "0"})
        if option in {"1", "2", "4"}:
            print(f"\n 1. Exalt\n 2. Steam {Fore.RED}(CURRENTLY NOT SUPPORTED FOR MENU OPTIONS BUT YOU CAN ADD ONE){Fore.WHITE}\n\n 0. BACK\n")
            _accountType = prompt_input("Choose your account type: ", allowed_values={"1", "2", "0"})

            if _accountType == "1":
                accountType = "Web"
                label = input("\nLabel: ")
                guid = input("E-Mail: ")
                password = pwinput.pwinput()
            elif _accountType == "2":
                accountType = "Steam"
                label = input("\nLabel: ")
                guid = input("GUID: ")
                password = pwinput.pwinput(prompt="Secret: ")
            elif _accountType == "0":
                menu()
            else:
                print(f"\n{Fore.RED}  Invalid account type{Fore.WHITE}")
                continue

            if option == "1":
                _type = "ignCheckerAccounts"
            elif option == "2":
                _type = "daily"
            elif option == "4":
                _type = "other"
            else:
                return []  
            if option in {"1", "2", "4"}:
                newAcc = {
                "active": False,
                "label": label,
                "accountType": accountType,
                "guid": guid,
                "password": password
                }
            appendCfg(newAcc, _type, label)
        elif option == "3":
                username = input("Username: ")
                password = pwinput.pwinput()
                _type = "realmeye"
                newAcc = {
                "username": username,
                "password": password
                }
                appendCfg(newAcc, _type, username)
        elif option == "0":
            return menu()
        else:
            print(f"\n{Fore.RED}  Invalid option, please try again{Fore.WHITE}")


def _help():
    _clear_screen()
    print(strHelp)
    while True:
        option = prompt_input("Select: ", allowed_values={"1", "2", "3", "4", "0"})
        if option in {"1", "2", "3", "4"}:
            print(strNoFAQ)
        elif option == "0":
            return(menu())
            break

def info():
    _clear_screen()
    print(strInfo)
    option = prompt_input("Select: ", allowed_values={"1", "2", "3", "4", "5", "6", "0"})
    if option == "1":
        webbrowser.open('https://discord.com/users/845594331322515487')
        info()
    elif option == "2":
        webbrowser.open('https://discord.gg/creatures')
        info()
    elif option == "3":
        webbrowser.open('https://youtube.com/buddingromance')
        info()
    elif option == "4":
        webbrowser.open('https://github.com/budding-romance')
        info()
    elif option == "5":
        webbrowser.open('https://fifty.website')
        info()
    elif option == "6":
        webbrowser.open('https://discord.gg/autododge')
        info()
    elif option == "0":
        return(menu())

def menu(meow=""):
    _clear_screen()
    if meow:
        print(meow)
    print(strMenu)
    option = prompt_input("Select: ", allowed_values={"1", "2", "3", "4", "5", "6", "8", "9", "H", "I", "0"})
    if option == "1":
        menu(getRealmIP())
    elif option == "2":
        menu(getData())
    elif option == "3":
        ign()
    elif option == "4":
        daily()
    elif option == "5":
        realmeye()
    elif option == "6":
        gParse()
    elif option == "8":
        setup()
    elif option == "9":
        manageAccounts()
    elif option == "H":
        _help()
    elif option == "I":
        info()
    elif option == "0":
        print("Exiting...")
        _clear_screen()
        exit()

def update_elapsed_time(start_time):
    while True:
        elapsed_time = time.time() - start_time

        elapsed_hours = int(elapsed_time // 3600)
        elapsed_minutes = int((elapsed_time % 3600) // 60)
        elapsed_seconds = int(elapsed_time % 60)

        elapsed_time_formatted = f"{elapsed_hours:02}:{elapsed_minutes:02}:{elapsed_seconds:02}"

        current_title = TITLES[title_index]
        realtitle = f"title Elapsed Time: {elapsed_time_formatted} ^| {current_title}"
        os.system(realtitle)
        time.sleep(1)

def update_title_text():
    global title_index
    while True:
        time.sleep(10)
        title_index = (title_index + 1) % len(TITLES)

if __name__ == "__main__":
    config = load_config()
    start_time = time.time()
    title_index = 0
    elapsed_time_thread = threading.Thread(target=update_elapsed_time, args=(start_time,), daemon=True)
    title_text_thread = threading.Thread(target=update_title_text, daemon=True)
    elapsed_time_thread.start()
    title_text_thread.start()
    menu()
