import requests
import json
import os
import time
import re
import uuid
from fake_useragent import UserAgent
from colorama import init, Fore, Style
import fade
from itertools import cycle

init()

def clean_filename(hostname):
    cleaned_hostname = re.sub(r'^([0-9])', '', re.sub(r'[/:"*?<>|]', '', hostname))
    return cleaned_hostname.replace('^0','').replace('^1','').replace('^2','').replace('^3','').replace('^4','').replace('^5','').replace('^6','').replace('^7','').replace('^8','').replace('^9','')

def check_if_player_exists(filename, player_data, added_players):
    if not os.path.exists(filename):
        return False

    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    for line in lines:
        try:
            existing_player = json.loads(line)
        except json.JSONDecodeError:
            continue

        if existing_player.get('fivem') == player_data.get('fivem'):
            fields_to_check = ['steam', 'name', 'live', 'xbl', 'license', 'license2','name','ip']
            fields_match = True

            for field in fields_to_check:
                existing_field_value = existing_player.get(field)
                new_field_value = player_data.get(field)

                if (existing_field_value is not None or new_field_value is not None) and existing_field_value != new_field_value:
                    fields_match = False
                    break

            if fields_match:
                return True

    if player_data['identifiers'] in added_players:
        return True

    return False

def get_server_info(server_id, proxy, added_players):
    url = f'https://servers-frontend.fivem.net/api/servers/single/{server_id}'
    user_agent = UserAgent()
    headers = {'User-Agent': user_agent.random, 'method': 'GET'}

    try:
        response = requests.get(url, headers=headers, proxies=proxy)

        if response.status_code == 200:
            server_data = response.json()
            hostname = clean_filename(str(uuid.uuid4()))

            try:
                hostname = clean_filename(server_data['Data']['hostname'])[:100]
            except Exception as err:
                print(err)

            try:
                if len(server_data['Data']['vars']['sv_projectName']) >= 10:
                    hostname = clean_filename(server_data['Data']['vars']['sv_projectName'])[:100]
            except:
                pass

            if not os.path.exists('scrape-joueur'):
                os.makedirs('scrape-joueur')

            if not os.path.exists('server_info'):
                os.makedirs('server_info')

            player_filename = f'scrape-joueur/{hostname}.txt'
            server_filename = f'server_info/{hostname}_server.txt'

            for player in server_data['Data']['players']:
                player_data = json.dumps(player, ensure_ascii=False)
                player_identifiers = player['identifiers']

                if not check_if_player_exists(player_filename, player, added_players):
                    with open(player_filename, 'a', encoding='utf-8') as file:
                        file.write(player_data)
                        file.write('\n')

                    print(Fore.BLUE + f'[Nouveau]' + Style.RESET_ALL + f' {player["name"]} a été ajouté !')
                    added_players.append(player_identifiers)
            server_info = {
                "server_id": server_id,
                "hostname": server_data['Data'].get('hostname', 'N/A'),
                "max_clients": server_data['Data'].get('vars', {}).get('sv_maxClients', 'N/A'),
                "gametype": server_data['Data'].get('vars', {}).get('gametype', 'N/A'),
                "mapname": server_data['Data'].get('vars', {}).get('mapname', 'N/A'),
                "resources": server_data['Data'].get('resources', []),
                "players_online": len(server_data['Data'].get('players', []))
            }

            with open(server_filename, 'w', encoding='utf-8') as file:
                file.write(json.dumps(server_info, ensure_ascii=False))
                file.write('\n')
                for resource in server_info["resources"]:
                    file.write(resource + '\n')

            print(Fore.BLUE + f'[INFO]' + Style.RESET_ALL + f' Informations du serveur {server_id} enregistrées dans {server_filename}')

        else:
            print(Fore.RED + f'\n[ERROR]' + Style.RESET_ALL + f" Message d'erreur ({server_id}: {response.status_code})\n")

    except Exception as e:
        print(f'Erreur: {str(e)}')

def process_servers(server_ids, proxies, added_players):
    proxy_cycle = cycle(proxies)  
    for server_id in server_ids:
        proxy = next(proxy_cycle)
        get_server_info(server_id, proxy, added_players)
        time.sleep(0.5)

def main():
    with open('serveur.txt', 'r') as server_file:
        french_server_ids = [line.strip() for line in server_file.readlines()]

    with open('proxy.txt', 'r') as proxy_file:
        proxy_list = [{'http': f'socks5://{proxy.strip()}'} for proxy in proxy_file]

    added_players = []

    while True:
        half_length = len(french_server_ids) // 2
        first_half = french_server_ids[:half_length]
        second_half = french_server_ids[half_length:]

        process_servers(first_half, proxy_list, added_players)
        process_servers(second_half, proxy_list, added_players)

def startup():
    os.system("cls")
    banner = '''
   ____ ____________     _____ 
   /_   /_   \_____  \   /  |  |
   |   ||   | _(__  <  /   |  |_
   |   ||   |/       \/    ^   /
   |___||___/______  /\____   | 
                   \/      |__|                       
'''
    faded_text = fade.water(banner) 
    print(faded_text)

    time.sleep(2)
    main()

if __name__ == "__main__":
    startup()
