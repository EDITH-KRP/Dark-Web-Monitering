import requests
from bs4 import BeautifulSoup


def track_seller_profile(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

       
        profile_name = soup.find('h1', class_='profile-name').text.strip()
        activity_data = soup.find_all('div', class_='activity')

        activities = []
        for activity in activity_data:
            activities.append(activity.text.strip())

        return {"profile_name": profile_name, "activities": activities}

    except requests.exceptions.RequestException as e:
        return {"error": f"Error accessing seller profile: {e}"}

if __name__ == "__main__":
   
    seller_url = "http://example.onion/seller_profile" 
    result = track_seller_profile(seller_url)
    print(result)
