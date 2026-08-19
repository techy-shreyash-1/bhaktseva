import requests as re
import geocoder
response = re.get('https://api.ipify.org').text
ip = response
location = geocoder.ip(ip)
print(ip)
print(location.state)