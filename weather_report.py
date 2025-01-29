import os
import requests
from urllib.parse import quote
import matplotlib.pyplot as plt
from datetime import datetime

def convert_temperature(temp, unit):
    if unit == "F":
        return (temp * 9/5) + 32
    return temp

def convert_windspeed(windspeed, unit):
    if unit == "mph":
        return windspeed * 0.621371
    return windspeed

def check_weather_alerts(days):
    alerts = []
    for day in days:
        date = day['datetime']
        temp = day['temp']
        humidity = day['humidity']
        precip = day.get('precip', 0)
        windspeed = day.get('windspeed', 0)
        
        if temp > 35:
            alerts.append(f"High temperature alert on {date} - {temp}°C")
        if temp < 10:
            alerts.append(f"Low temperature alert on {date} - {temp}°C")
        if humidity > 80:
            alerts.append(f"High humidity alert on {date} - {humidity}%")
        if precip > 10:
            alerts.append(f"High precipitation alert on {date} - {precip} mm")
        if windspeed > 20:
            alerts.append(f"High wind speed alert on {date} - {windspeed} m/s")
            
    if alerts:
        print("\n⚠️ Weather Alert:")
        for alert in alerts:
            print(alert)
    else:
        print("\nNo weather alerts found for the specified period.")
        
def get_weather_data(data, start_date, end_date):
    try:
        if 'days' in data:
            days = data['days']
            if start_date and end_date:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
                days = [day for day in days if start_date <= datetime.strptime(day['datetime'], '%Y-%m-%d') <= end_date]
            
            temp_unit = input("Select temperature unit(C/F):").upper()
            windspeed_unit = input("Select the unit of measurement for wind speed (kmh/mph): ").lower()
            
            dates = [day['datetime'] for day in days]
            temps = [day['temp'] for day in days]
            humidities = [day['humidity'] for day in days]
            windspeeds = [convert_windspeed(day.get('windspeed', 0), windspeed_unit)for day in days]
            
            print("\nWeather information:")
            for date, temp, humidity, windspeed in zip(dates, humidities, windspeeds):
                print(f"date{date}: temp = {temp}°{temp_unit}, humidity = {humidity}%, windspeed = {windspeed} {windspeed_unit}")
                
            check_weather_alerts(days)
        return plot(days, dates, temps, humidities)
    except KeyError:
        print("City not found")
        
def plot(days, dates, temps, humidities):
    try:
        plt.figure(figsize=(10, 6))
        plt.plot(dates, temps, marker='o', color='b', label="Temperature (°C)")
        plt.plot(dates, humidities, marker='x', color='g', label="Humidity (%)")
        plt.title(f"Daily Temperature in {encoded_city}", fontsize=16)
        plt.xlabel("Date", fontsize=12)
        plt.ylabel("Temperature (°C)", fontsize=12)
        plt.xticks(rotation=45)
        plt.grid(alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.show()
    except Exception as e:
        print(e)
if __name__ == "__main__":
    api_key = os.getenv("API_KEY")
    city = input("Enter the city name: ")
    start_date = input("Enter start date (YYYY-MM-DD): ")
    end_date = input("Enter end date (YYYY-MM-DD): ")
    encoded_city = quote(city)
    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{encoded_city}?unitGroup=metric&key={api_key}&contentType=json"
    response = requests.get(url)
    data = response.json()
    
    get_weather_data(data, start_date, end_date)