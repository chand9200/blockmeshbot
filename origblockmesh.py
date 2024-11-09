import requests
import time
import os
import webbrowser
from dotenv import load_dotenv

# Display message at the start of automation
print("Starting Automation...")
print("Author : dasarpemulung")
print("Telegram Channel : @dasarpemulung")
print("YouTube : Dasar Pemulung")
print("=======================")
# Open the YouTube URL automatically
youtube_url = "https://www.youtube.com/watch?v=oquyxkqrzB8"
webbrowser.open(youtube_url)

# Load environment variables from .env file
load_dotenv()
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

# API URLs
LOGIN_URL = "https://api.blockmesh.xyz/api/get_token"
REPORT_URL = "https://app.blockmesh.xyz/api/report_uptime?email={email}&api_token={api_token}&ip={ip}"

# Headers for login and report
headers_login = {
    "accept": "*/*",
    "content-type": "application/json",
    "origin": "https://app.blockmesh.xyz",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/130.0.0.0 Safari/537.36"
}
headers_report = {
    "accept": "*/*",
    "content-type": "text/plain;charset=UTF-8",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/130.0.0.0 Safari/537.36"
}

# Check if proxylist.txt exists
if os.path.exists("proxylist.txt"):
    with open("proxylist.txt", "r") as file:
        proxies = file.read().splitlines()
else:
    proxies = None  # No proxies available

# Function to format proxy for requests
def get_proxy_dict(proxy):
    proxy_type, user_pass_host = proxy.split("://")
    user, pass_host = user_pass_host.split(":", 1)
    password, host_port = pass_host.split('@', 1)
    host, port = host_port.split(':')
    return {
        "http": f"{proxy_type}://{user}:{password}@{host}:{port}",
        "https": f"{proxy_type}://{user}:{password}@{host}:{port}"
    }, host  # return proxy dictionary and IP address

# Function to log in and get token
def login(proxy=None):
    proxies_dict = get_proxy_dict(proxy)[0] if proxy else None
    ip_address = get_proxy_dict(proxy)[1] if proxy else requests.get("https://api64.ipify.org").text
    
    payload = {"email": EMAIL, "password": PASSWORD}
    try:
        response = requests.post(LOGIN_URL, json=payload, headers=headers_login, proxies=proxies_dict)
        response.raise_for_status()
        data = response.json()
        print(f"Login successful with IP: {ip_address}")
        return data.get("api_token"), ip_address
    except requests.RequestException as e:
        print(f"Login failed: {e}")
        return None, None

# Function to send uptime report
def report_uptime(api_token, ip_address, proxy=None):
    proxies_dict = get_proxy_dict(proxy)[0] if proxy else None
    report_url = REPORT_URL.format(email=EMAIL, api_token=api_token, ip=ip_address)
    try:
        response = requests.post(report_url, headers=headers_report, proxies=proxies_dict)
        response.raise_for_status()
        print("Uptime report successful.")
    except requests.RequestException as e:
        print(f"Uptime report failed: {e}")

# Main function
def main():
    if proxies:
        while proxies:
            current_proxy = proxies.pop(0)  # Use first proxy
            api_token, ip_address = login(current_proxy)
            
            if api_token:
                proxies.append(current_proxy)  # Move used proxy to end of list
                with open("proxylist.txt", "w") as file:
                    file.write("\n".join(proxies))
                
                print("Waiting 5 minutes before posting...")
                time.sleep(300)  # Wait 5 minutes

                report_uptime(api_token, ip_address, current_proxy)
            else:
                print("Trying next proxy...\n")
    else:
        api_token, ip_address = login()
        
        if api_token:
            print("Waiting 5 minutes before posting...")
            time.sleep(300)
            report_uptime(api_token, ip_address)

if __name__ == "__main__":
    main()
