import requests
import time

# --- CONFIGURATION ---
# Replace with your actual GitHub Personal Access Token
TOKEN = 'ghp_your_actual_token_here_xxxxxxx'

HEADERS = {
    'Authorization': f'token {TOKEN}',
    'Accept': 'application/vnd.github.v3+json',
    'X-GitHub-Api-Version': '2022-11-28'
}

def get_users(endpoint):
    """Fetches all users from a specific endpoint (followers or following), handling pagination."""
    users = set()
    url = f"https://api.github.com/user/{endpoint}?per_page=100"
    
    while url:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        
        for user in response.json():
            users.add(user['login'])
            
        # Handle GitHub's pagination to ensure we get *all* users
        url = None
        if 'Link' in response.headers:
            links = response.headers['Link'].split(', ')
            for link in links:
                if 'rel="next"' in link:
                    url = link[link.find('<')+1:link.find('>')]
                    break
    return users

def main():
    print("Fetching followers and following lists...")
    try:
        followers = get_users('followers')
        following = get_users('following')
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to GitHub API. Check your token. Details: {e}")
        return

    # Find people who follow you, but you don't follow back yet
    to_follow = followers - following

    if not to_follow:
        print("You are already following back all your followers!")
        return

    print(f"Found {len(to_follow)} users to follow back. Starting...")

    for user in to_follow:
        print(f"Following {user}...")
        follow_url = f"https://api.github.com/user/following/{user}"
        res = requests.put(follow_url, headers=HEADERS)
        
        if res.status_code == 204:
            print(f"Successfully followed {user}.")
        else:
            print(f"Failed to follow {user}. Status Code: {res.status_code}")
            
        # Pause for 2 seconds between requests to respect GitHub's rate limits
        time.sleep(2)
        
    print("Finished auto-following!")

if __name__ == "__main__":
    main()
