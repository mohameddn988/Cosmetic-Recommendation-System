import requests
import csv
import os

def scrape_vehicles_api():
    url = "https://www.tct.pro/api/public/vehicles"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        data = response.json()
        
        if not data or 'data' not in data:
            print("No data received from the API.")
            return
        
        vehicles = data['data']
        
        if not isinstance(vehicles, list) or not vehicles:
            print("Unexpected data format. Expected a list of vehicles.")
            return
        
        # Get field names from the first item
        fieldnames = vehicles[0].keys()
        
        # Create the folder if it doesn't exist
        folder_path = os.path.join("data", "ApiMethod")
        os.makedirs(folder_path, exist_ok=True)
        
        # Save to CSV
        csv_file_path = os.path.join(folder_path, "ApiVehicles.csv")
        with open(csv_file_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(vehicles)
        
        print(f"Successfully scraped {len(vehicles)} vehicles and saved to {csv_file_path}")
    
    except requests.exceptions.RequestException as e:
        print(f"Error making request to API: {e}")
    except ValueError as e:
        print(f"Error parsing JSON response: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    scrape_vehicles_api()