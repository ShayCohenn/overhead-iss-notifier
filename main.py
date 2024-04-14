import os
import time
import smtplib
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv("FROM_EMAIL")
PASSWORD = os.getenv("PASSWORD")
TO_EMAIL = os.getenv("TO_EMAIL")

MY_LAT = 39.046834437571704 # Your latitude
MY_LONG = 125.72042751696706 # Your longitude

def is_iss_overhead() -> bool:
    response = requests.get(url="http://api.open-notify.org/iss-now.json")
    response.raise_for_status()
    data = response.json()

    iss_latitude = float(data["iss_position"]["latitude"])
    iss_longitude = float(data["iss_position"]["longitude"])

    return MY_LAT - 5 <= iss_latitude <= MY_LAT + 5 and MY_LONG - 5 <= iss_longitude <= MY_LONG + 5

def is_night() -> bool:
    parameters = {
    "lat": MY_LAT,
    "lng": MY_LONG,
    "formatted": 0,
}

    response = requests.get("https://api.sunrise-sunset.org/json", params=parameters)
    response.raise_for_status()
    data = response.json()
    sunrise: int = int(data["results"]["sunrise"].split("T")[1].split(":")[0])
    sunset: int = int(data["results"]["sunset"].split("T")[1].split(":")[0])

    time_now: int = datetime.now().hour

    return time_now >= sunset or time_now <= sunrise

while True:
    if is_iss_overhead() and is_night():
        connection = smtplib.SMTP("smtp.gmail.com")
        connection.starttls()
        connection.login(EMAIL, PASSWORD)
        connection.sendmail(
            from_addr=EMAIL,
            to_addrs=TO_EMAIL,
            msg="Subject:Look Up\n\nThe ISS is above you"
        )
    time.sleep(60)
