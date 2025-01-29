import os
import requests
from urllib.parse import quote
import matplotlib.pyplot as plt
from datetime import datetime

def get_weather_data(data, start_date, end_date):
    try:
        if 'days' in data:
            days = data['days']
            if start_date and end_date:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
                days = [day for day in days if start_date <= datetime.strptime(day['datetime'], '%Y-%m-%d') <= end_date]
            dates = [day['datetime'] for day in days]
            temps = [day['temp'] for day in days]
            humidities = [day['humidity'] for day in days]
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