import requests
import json

# Constants
API_URL = "https://api.example.com/data"

# Function to fetch data
def fetch_data():
    response = requests.get(API_URL)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return None

# Main execution
if __name__ == "__main__":
    data = fetch_data()
    if data:
        print(data)
    else:
        print("Failed to fetch data.")
