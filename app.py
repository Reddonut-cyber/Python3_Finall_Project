from flask import Flask, render_template, request
import requests
from urllib.parse import quote
import os

app = Flask(__name__)

def get_weather_data(city, start_date=None, end_date=None):
    api_key = os.getenv("API_KEY")
    encoded_city = quote(city)
    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{encoded_city}?unitGroup=metric&key={api_key}&contentType=json"
    response = requests.get(url)
    data = response.json()
    if 'days' in data:
        days = data['days']
        if start_date and end_date:
            days = [day for day in days if start_date <= day['datetime'] <= end_date]
        return days
    return None

@app.route("/", methods=["GET", "POST"])
def index():
    weather_data = None
    if request.method == "POST":
        city = request.form["city"]
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        weather_data = get_weather_data(city, start_date, end_date)
    return render_template("index.html", weather_data=weather_data)

if __name__ == "__main__":
    app.run(debug=True)