from flask import Flask, render_template, request, redirect, url_for
import requests
from urllib.parse import quote
import os
import json
from datetime import datetime
import base64
import io
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

app = Flask(__name__)

def get_weather_data(city, start_date=None, end_date=None, temp_unit="C", windspeed_unit="kmh"):
    api_key = os.getenv("API_KEY")
    encoded_city = quote(city)
    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{encoded_city}?unitGroup=metric&key={api_key}&contentType=json"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        if 'days' in data:
            days = data['days']
            if start_date and end_date:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
                days = [day for day in days if start_date <= datetime.strptime(day['datetime'], '%Y-%m-%d') <= end_date]
            
            dates = [day['datetime'] for day in days]
            temps = [convert_temperature(day['temp'], temp_unit) for day in days]
            humidities = [day['humidity'] for day in days]
            windspeeds = [convert_windspeed(day.get('windspeed', 0), windspeed_unit) for day in days]

            img_base64 = generate_plot(dates, temps, humidities, city)
            alerts = check_weather_alerts(days, temp_unit, windspeed_unit)
            weather_info = [
                {
                    "date": date,
                    "temp": temp,
                    "humidity": humidity,
                    "windspeed": windspeed
                }
                for date, temp, humidity, windspeed in zip(dates, temps, humidities, windspeeds)
            ]

            return weather_info, img_base64, alerts

        return None, None, None

    except requests.exceptions.RequestException as e:
        print(f"API Request Error: {e}")
        return None, None, None
    except json.JSONDecodeError as e:
         print(f"JSON Decode Error: {e}")
         return None, None, None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None, None, None
        

def convert_temperature(temp, unit):
    if unit == "F":
        return (temp * 9/5) + 32
    return temp

def convert_windspeed(windspeed, unit):
    if unit == "mph":
        return windspeed * 0.621371
    return windspeed

def check_weather_alerts(days, temp_unit, windspeed_unit):
    alerts = []
    for day in days:
        date = day['datetime']
        temp = day['temp']
        humidity = day['humidity']
        precip = day.get('precip', 0)
        windspeed = day.get('windspeed', 0)
        
        if temp_unit == "F":
            temp = (temp * 9/5) + 32
            if temp > 95:
                alerts.append(f"High temperature alert on {date} - {temp}°F")
            if temp < 50:
                alerts.append(f"Low temperature alert on {date} - {temp}°F")
        elif temp > 35:
           alerts.append(f"High temperature alert on {date} - {temp}°C")
        elif temp < 10:
             alerts.append(f"Low temperature alert on {date} - {temp}°C")
        
        if humidity > 80:
            alerts.append(f"High humidity alert on {date} - {humidity}%")
        if precip > 10:
            alerts.append(f"High precipitation alert on {date} - {precip} mm")
        if windspeed_unit == 'mph':
             windspeed = windspeed * 0.621371
             if windspeed > 12.4:
                alerts.append(f"High wind speed alert on {date} - {windspeed} mph")
        elif windspeed > 20:
            alerts.append(f"High wind speed alert on {date} - {windspeed} m/s")
            
    return alerts

def generate_plot(dates, temps, humidities, city):
    try:
        plt.figure(figsize=(10, 6))
        plt.plot(dates, temps, marker='o', color='b', label="Temperature")
        plt.plot(dates, humidities, marker='x', color='g', label="Humidity (%)")
        plt.title(f"Daily Weather in {city}", fontsize=16)
        plt.xlabel("Date", fontsize=12)
        plt.ylabel("Value", fontsize=12)
        plt.xticks(rotation=45)
        plt.grid(alpha=0.3)
        plt.legend()
        plt.tight_layout()

        # Save the plot to a buffer
        img_buf = io.BytesIO()
        plt.savefig(img_buf, format='png')
        img_buf.seek(0)

        # Encode the image as base64
        img_base64 = base64.b64encode(img_buf.read()).decode('utf8')
        plt.close()
        return img_base64
    except Exception as e:
        print(f"Plotting error: {e}")
        return None

@app.route("/", methods=["GET", "POST"])
def index():
    weather_data = None
    img_base64 = None
    alerts = None
    if request.method == "POST":
        city = request.form.get("city")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        temp_unit = request.form.get("temp_unit", "C")
        windspeed_unit = request.form.get("windspeed_unit", "kmh")
        
        if not city:
            return render_template("index.html", error="City is required")
        
        try:
           weather_data, img_base64, alerts = get_weather_data(city, start_date, end_date, temp_unit, windspeed_unit)
        except Exception as e:
           return render_template("index.html", error=str(e))

    return render_template("index.html", weather_data=weather_data, img_base64=img_base64, alerts=alerts)

if __name__ == "__main__":
    app.run(debug=True)