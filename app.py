from flask import Flask, request, jsonify
import requests
import time

app = Flask(__name__)

# Cache location results
location_cache = {}

# Cache duration: 1 hour
CACHE_TIME = 3600


def get_user_ip():
    """
    Get the visitor's IP address.
    """

    # Check forwarded IP headers
    x_forwarded_for = request.headers.get("X-Forwarded-For")

    if x_forwarded_for:
        # First IP is usually the visitor's IP
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.remote_addr

    return ip


def get_location(ip):
    """
    Get approximate location using IP address.
    Includes caching and fallback API.
    """

    # Check cache first
    if ip in location_cache:
        cached_data = location_cache[ip]

        # Use cached data if it is not expired
        if time.time() - cached_data["timestamp"] < CACHE_TIME:
            print("Using cached location data")
            return cached_data["data"]

    # Default result
    result = {
        # "ip": ip,
        # "city": None,
        "state": None,
        # "country": None,
        # "postal_code": None,
        # "latitude": None,
        # "longitude": None,
        # "timezone": None,
        # "organization": None,
        # "source": None
    }

    # ==========================================
    # API 1: ipwho.is
    # ==========================================
    try:
        print(f"Getting location for IP: {ip}")

        response = requests.get(
            f"https://ipwho.is/{ip}",
            timeout=10
        )

        data = response.json()

        if data.get("success", True):

            result.update({
                "ip": data.get("ip", ip),
                # "city": data.get("city"),
                "state": data.get("region")
                # if isinstance(data.get("timezone"), dict)
                # else data.get("timezone"),
                # "organization": data.get("connection", {}).get("org")
                # if isinstance(data.get("connection"), dict)
                # else None,
                # "source": "ipwho.is"
            })

            # Save to cache
            # location_cache[ip] = {
            #     "timestamp": time.time(),
            #     "data": result
            # }

            return result

    except Exception as e:
        print("ipwho.is Error:", e)

    # ==========================================
    # API 2: ipapi.co fallback
    # ==========================================
    try:
        response = requests.get(
            f"https://ipapi.co/{ip}/json/",
            timeout=10
        )

        # Check for rate limit
        if response.status_code == 429:
            raise Exception("ipapi.co rate limit reached")

        response.raise_for_status()

        data = response.json()

        result.update({
            # "ip": ip,
            # "city": data.get("city"),
            "state": data.get("region"),
            # "country": data.get("country_name"),
            # "postal_code": data.get("postal"),
            # "latitude": data.get("latitude"),
            # "longitude": data.get("longitude"),
            # "timezone": data.get("timezone"),
            # "organization": data.get("org"),
            "source": "ipapi.co"
        })

        # Save successful result to cache
        location_cache[ip] = {
            "timestamp": time.time(),
            "data": result
        }

        return result

    except Exception as e:
        print("ipapi.co Error:", e)

    # Return if both APIs fail
    result["error"] = "Unable to get location at this time"

    return result


@app.route("/")
def home():
    """
    Runs when the user opens the website.
    """

    # Get visitor IP
    ip = get_user_ip()

    # Get approximate location
    user_location = get_location(ip)

    # Print details in backend terminal
    print("\n" + "=" * 50)
    print("          NEW USER VISITED WEBSITE")
    print("=" * 50)
    print("IP Address   :", user_location.get("ip"))
    # print("City         :", user_location.get("city"))
    print("State        :", user_location.get("state"))
    # print("Country      :", user_location.get("country"))
    # print("Postal Code  :", user_location.get("postal_code"))
    # print("Latitude     :", user_location.get("latitude"))
    # print("Longitude    :", user_location.get("longitude"))
    # print("Timezone     :", user_location.get("timezone"))
    # print("Organization :", user_location.get("organization"))
    # print("API Source   :", user_location.get("source"))
    print("=" * 50 + "\n")

    return jsonify({
        "message": "Welcome! Approximate location detected.",
        "user_details": user_location
    })


@app.route("/location")
def location():
    """
    API endpoint:
    /location
    """

    ip = get_user_ip()
    user_location = get_location(ip)

    return jsonify(user_location)


@app.route("/clear-cache")
def clear_cache():
    """
    Clear cached location data.
    """

    location_cache.clear()

    return jsonify({
        "message": "Location cache cleared successfully"
    })


if __name__ == "__main__":

    print("=" * 50)
    print("Starting Flask Server")
    print("Local URL: http://127.0.0.1:5000")
    print("Location API: http://127.0.0.1:5000/location")
    print("=" * 50)

    # Required for GitHub Codespaces / Port Forwarding
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )