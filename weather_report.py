import os
import requests
import matplotlib.pyplot as plt

def get_weather_data(data):
    try:
        if 'days' in data:
            days = data['days']
            dates = [day['datetime'] for day in days]
            temps = [day['temp'] for day in days]

        return plot(days, dates, temps)
    except KeyError:
        print("City not found")
        
def plot(days, dates, temps):
    try:
        plt.figure(figsize=(10, 6))
        plt.plot(dates, temps, marker='o', color='b', label="Temperature (°C)")
        plt.title(f"Daily Temperature in {city}", fontsize=16)
        plt.xlabel("Date", fontsize=12)
        plt.ylabel("Temperature (°C)", fontsize=12)
        plt.xticks(rotation=45)
        plt.grid(alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.show()
    except Exception as e:
        print(e)
__name__ == "__main__" 
api_key = os.getenv("API_KEY")
city = input("Enter the city name: ")

url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}?unitGroup=metric&key={api_key}&contentType=json"

response = requests.get(url)
data = response.json()

get_weather_data(data)