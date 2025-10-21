import requests
from bs4 import BeautifulSoup
import csv
import os

def scrape_vehicles_html():
    url = "https://www.tct.pro/used-vehicles"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all vehicle cards using the correct CSS selector
        vehicle_cards = soup.find_all('div', class_='group relative overflow-hidden rounded-2xl transition-shadow duration-200')
        
        vehicles = []
        
        for i, card in enumerate(vehicle_cards, start=1):
            vehicle = {'id': i}
            
            # Extract vehicle name from h3
            h3 = card.find('h3')
            vehicle['name'] = h3.get_text(strip=True) if h3 else 'N/A'
            
            # Extract year and price from the bold divs
            bold_divs = card.find_all('div', class_=lambda c: c and 'text-lg md:text-xl font-bold' in c)
            if len(bold_divs) >= 2:
                vehicle['year'] = bold_divs[0].get_text(strip=True)
                vehicle['price'] = bold_divs[1].get_text(strip=True)
            else:
                vehicle['year'] = 'N/A'
                vehicle['price'] = 'N/A'
            
            # Extract mileage, transmission, fuel from the spans
            info_spans = card.find_all('span', class_=lambda c: c and 'text-xs font-medium' in c)
            if len(info_spans) >= 3:
                vehicle['mileage'] = info_spans[0].get_text(strip=True)
                vehicle['transmission'] = info_spans[1].get_text(strip=True)
                vehicle['fuel'] = info_spans[2].get_text(strip=True)
            else:
                vehicle['mileage'] = 'N/A'
                vehicle['transmission'] = 'N/A'
                vehicle['fuel'] = 'N/A'
            
            # Extract availability badge
            badge_div = card.find('div', class_=lambda c: c and 'absolute top-4 right-4' in c)
            if badge_div:
                badge_text = badge_div.get_text(strip=True)
                vehicle['badge'] = badge_text
                vehicle['isAvailable'] = badge_text == 'Disponible'
            else:
                vehicle['badge'] = 'N/A'
                vehicle['isAvailable'] = False
            
            vehicles.append(vehicle)
        
        if not vehicles:
            print("No vehicles found with the current selectors.")
            return
        
        # Get field names
        fieldnames = vehicles[0].keys()
        
        # Create the folder if it doesn't exist
        folder_path = os.path.join("data", "method3_python")
        os.makedirs(folder_path, exist_ok=True)
        
        # Save to CSV
        csv_file_path = os.path.join(folder_path, "LibraryMethod.csv")
        with open(csv_file_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(vehicles)
        
        print(f"Successfully scraped {len(vehicles)} vehicles from HTML and saved to {csv_file_path}")
    
    except requests.exceptions.RequestException as e:
        print(f"Error making request to website: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    scrape_vehicles_html()