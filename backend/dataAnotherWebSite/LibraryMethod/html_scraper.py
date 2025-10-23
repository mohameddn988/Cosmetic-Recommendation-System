import requests
from bs4 import BeautifulSoup
import csv
import os
import time

def scrape_games_html():
    base_url = "https://www.wifi4games.com/pc_games/{}/index.html"
    
    all_games = []
    all_detailed_games = []
    game_id = 1
    
    for page in range(1, 50):  # Pages from 1 to 49
        url = base_url.format(page)
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all game links containing "بحجم"
            game_links = soup.find_all('a', href=True)
            
            page_games = []
            
            for a in game_links:
                text = a.get_text(strip=True)
                if "بحجم" in text:
                    parts = text.split("بحجم")
                    name = parts[0].strip()
                    size_part = parts[1].strip()
                    # Extract size (e.g., "10.9 GB")
                    size_words = size_part.split()
                    if len(size_words) >= 2:
                        size = size_words[0] + " " + size_words[1]
                    else:
                        size = size_part
                    
                    game_url = 'https://www.wifi4games.com' + a['href']
                    
                    game = {
                        'id': game_id,
                        'name': name,
                        'size': size,
                        'url': game_url
                    }
                    
                    page_games.append(game)
                    game_id += 1
            
            if not page_games:
                print(f"No more games found on page {page}. Stopping.")
                break
            
            all_games.extend(page_games)
            print(f"Scraped {len(page_games)} games from page {page}")
            
            # Now scrape details for this page's games
            for game in page_games:
                print(f"Scraping details for {game['name']}")
                details = scrape_game_details(game['url'])
                if details:
                    detailed_game = {**game, **details}
                    all_detailed_games.append(detailed_game)
                time.sleep(1)  # Be respectful
        
        except requests.exceptions.RequestException as e:
            print(f"Error making request to page {page}: {e}")
            continue
        except Exception as e:
            print(f"An unexpected error occurred on page {page}: {e}")
            continue
    
    if not all_games:
        print("No games found.")
        return
    
    # Save list CSV
    fieldnames_list = all_games[0].keys()
    folder_path = os.path.join("dataAnotherWebSite", "ExtensionMethod")
    os.makedirs(folder_path, exist_ok=True)
    csv_file_path = os.path.join(folder_path, "wifi4games-com-2025-10-22.csv")
    with open(csv_file_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames_list)
        writer.writeheader()
        writer.writerows(all_games)
    
    print(f"Successfully scraped {len(all_games)} games list and saved to {csv_file_path}")
    
    # Save detailed CSV
    if all_detailed_games:
        fieldnames_detailed = all_detailed_games[0].keys()
        detailed_csv_path = os.path.join(folder_path, "detailed_games.csv")
        with open(detailed_csv_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames_detailed)
            writer.writeheader()
            writer.writerows(all_detailed_games)
        
        print(f"Successfully scraped detailed data for {len(all_detailed_games)} games and saved to {detailed_csv_path}")

def scrape_game_details(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title
        title_tag = soup.find('h1')
        title = title_tag.get_text(strip=True) if title_tag else 'N/A'
        
        # Extract description/story
        story_h3 = soup.find('h3', string='حكاية اللعبة')
        description = ''
        if story_h3:
            story_div = story_h3.find_next('p')
            if story_div:
                description = story_div.get_text(strip=True)
        
        # Extract size from download section
        size = 'N/A'
        download_section = soup.find('h3', string='تنزيل لعبة')
        if download_section:
            size_icon = download_section.find_next('p').find('span', class_=lambda c: c and '' in c)
            if size_icon:
                size_text = size_icon.get_text(strip=True)
                if 'بحجم' in size_text:
                    size = size_text.replace('', '').strip()
        
        # Extract system requirements
        min_cpu = min_gpu = min_ram = rec_cpu = rec_gpu = rec_ram = 'N/A'
        
        min_req_h3 = soup.find('h3', string='الحد الأدنى لمتطلبات النظام:')
        if min_req_h3:
            req_text = min_req_h3.find_next('p').get_text(strip=True)
            lines = req_text.split('\n')
            for line in lines:
                if 'المعالج:' in line:
                    min_cpu = line.replace('المعالج:', '').strip()
                elif 'كرت الفيديو:' in line:
                    min_gpu = line.replace('كرت الفيديو:', '').strip()
                elif 'الرام:' in line:
                    min_ram = line.replace('الرام:', '').strip()
        
        rec_req_h3 = soup.find('h3', string='متطلبات النظام الموصى بها:')
        if rec_req_h3:
            req_text = rec_req_h3.find_next('p').get_text(strip=True)
            lines = req_text.split('\n')
            for line in lines:
                if 'المعالج:' in line:
                    rec_cpu = line.replace('المعالج:', '').strip()
                elif 'كرت الفيديو:' in line:
                    rec_gpu = line.replace('كرت الفيديو:', '').strip()
                elif 'الرام:' in line:
                    rec_ram = line.replace('الرام:', '').strip()
        
        # Extract rating and stats
        rating = reviews_count = downloads = views = 'N/A'
        stats_div = soup.find('div', class_=lambda c: c and '' in c)
        if stats_div:
            stats_text = stats_div.get_text(strip=True)
            # Parse stars and numbers
            # This might need adjustment based on exact format
        
        # For simplicity, look for the stats line
        stats_p = soup.find('p', string=lambda s: s and 'تقيماً' in s)
        if stats_p:
            stats_text = stats_p.get_text(strip=True)
            parts = stats_text.split()
            if len(parts) >= 6:
                rating = parts[0]  # stars
                reviews_count = parts[1]
                downloads = parts[3]
                views = parts[5]
        
        # Extract categories
        categories = []
        category_links = soup.find_all('a', href=lambda h: h and '/cat/' in h)
        for link in category_links:
            categories.append(link.get_text(strip=True))
        categories_str = ', '.join(categories)
        
        return {
            'title': title,
            'description': description,
            'size': size,
            'min_cpu': min_cpu,
            'min_gpu': min_gpu,
            'min_ram': min_ram,
            'rec_cpu': rec_cpu,
            'rec_gpu': rec_gpu,
            'rec_ram': rec_ram,
            'rating': rating,
            'reviews_count': reviews_count,
            'downloads': downloads,
            'views': views,
            'categories': categories_str
        }
    
    except Exception as e:
        print(f"Error scraping details from {url}: {e}")
        return None

def scrape_all_game_details():
    # Read the existing CSV
    csv_file_path = os.path.join("dataAnotherWebSite", "ExtensionMethod", "wifi4games-com-2025-10-22.csv")
    if not os.path.exists(csv_file_path):
        print("Games list CSV not found. Run scrape_games_html first.")
        return
    
    games = []
    with open(csv_file_path, "r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            games.append(row)
    
    detailed_games = []
    
    for game in games:
        print(f"Scraping details for {game['name']}")
        details = scrape_game_details(game['url'])
        if details:
            detailed_game = {**game, **details}
            detailed_games.append(detailed_game)
        time.sleep(1)  # Be respectful to the server
    
    if not detailed_games:
        print("No detailed data scraped.")
        return
    
    # Save detailed data
    fieldnames = detailed_games[0].keys()
    detailed_csv_path = os.path.join("detailed_games.csv")
    with open(detailed_csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(detailed_games)
    
    print(f"Successfully scraped detailed data for {len(detailed_games)} games and saved to {detailed_csv_path}")

if __name__ == "__main__":
    scrape_games_html()