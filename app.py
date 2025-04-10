from flask import Flask, render_template, request, redirect, url_for, send_file
import requests
import sqlite3
import json
from datetime import datetime
import uuid
import csv
from io import StringIO, BytesIO
from fpdf import FPDF  
import re
import youtube
import db
import fileExport
# API keys
API_KEY = "a35bc7a09d1bb0720255be3bc9d4ac5d"

# flask app
app = Flask(__name__)


# home page and weather entry
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        location_input = request.form["city"].strip()
        is_zip = re.fullmatch(r"\d{5}", location_input)

        try:
            # Step 1: Get coordinates
            lat = lon = city_name = None
            if is_zip:
                geo_url = f"http://api.openweathermap.org/geo/1.0/zip?zip={location_input},US&appid={API_KEY}"
                data = requests.get(geo_url).json()
                lat, lon = data.get("lat"), data.get("lon")
                city_name = data.get("name", location_input)
            else:
                geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={location_input}&limit=1&appid={API_KEY}"
                geo_res = requests.get(geo_url).json()
                if geo_res:
                    lat, lon = geo_res[0]["lat"], geo_res[0]["lon"]
                    city_name = geo_res[0].get("name", location_input)

            # if not avail thru openweather then: 
            if not lat or not lon:
                nom_url = f"https://nominatim.openstreetmap.org/search?q={location_input}&format=json&limit=1"
                nom_res = requests.get(nom_url, headers={"User-Agent": "weather-app"}).json()
                if not nom_res:
                    return render_template("index.html", error="Location not found. Try being more specific.")
                lat, lon = nom_res[0]["lat"], nom_res[0]["lon"]
                city_name = nom_res[0]["display_name"].split(",")[0]

            # get data
            weather_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=imperial"
            res = requests.get(weather_url).json()
            if res.get("cod") != "200":
                return render_template("index.html", error="Could not fetch weather data.")

            # format
            weather_data = []
            for i in range(0, len(res["list"]), 8):  
                day = res["list"][i]
                formatted_date = datetime.strptime(day["dt_txt"].split(" ")[0], "%Y-%m-%d").strftime("%B %d, %Y")
                weather_data.append({
                    "date": formatted_date,
                    "temp": day["main"]["temp"],
                    "desc": day["weather"][0]["description"],
                    "icon": day["weather"][0]["icon"],
                    "city": city_name
                })

            videos = youtube.get_youtube_videos(city_name)
            return render_template("forecast.html", weather=weather_data, videos=videos)

        except Exception as e:
            print(f"Error: {e}")
            return render_template("index.html", error="An error occurred. Please try again.")

    return render_template("index.html")

# weather based on current location
@app.route("/current_weather")
def current_weather():
    lat = request.args.get("lat")
    lon = request.args.get("lon")

    if not lat or not lon:
        return render_template("index.html", error="Missing location data. Please try again.")

    reverse_geo_url = f"http://api.openweathermap.org/geo/1.0/reverse?lat={lat}&lon={lon}&limit=1&appid={API_KEY}"
    reverse_res = requests.get(reverse_geo_url).json()

    if not reverse_res:
        return render_template("index.html", error="Unable to identify location from coordinates.")

    city_name = reverse_res[0]["name"]

    forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=imperial"
    res = requests.get(forecast_url).json()

    if res.get("cod") != "200":
        return render_template("index.html", error="Could not fetch weather for your location.")

    weather_data = []
    for i in range(0, len(res["list"]), 8):  
        day = res["list"][i]
        raw_date = datetime.strptime(day["dt_txt"].split(" ")[0], "%Y-%m-%d")
        formatted_date = raw_date.strftime("%B %d, %Y")
        weather_data.append({
            "date": formatted_date,
            "temp": day["main"]["temp"],
            "desc": day["weather"][0]["description"],
            "icon": day["weather"][0]["icon"],
            "city": city_name
        })

    videos = youtube.get_youtube_videos(city_name)
    return render_template("forecast.html", weather=weather_data, videos=videos)

# redirects to home
@app.route("/forecast")
def forecast():
    return redirect("/")

#saves forcast to database
@app.route("/save_all", methods=["POST"])
def save_all():
    forecasts = json.loads(request.form["forecast"])
    forecast_id = str(uuid.uuid4())
    city = forecasts[0]["city"]  
    videos = youtube.get_youtube_videos(city)  

    # Save forecasts to database
    conn = sqlite3.connect("weather.db")
    c = conn.cursor()
    for item in forecasts:
        c.execute("""
            INSERT INTO weather (forecast_id, city, date, temperature, description)
            VALUES (?, ?, ?, ?, ?)
        """, (forecast_id, item["city"], item["date"], item["temp"], item["desc"]))
    conn.commit()
    conn.close()
    return render_template("forecast.html", weather=forecasts, videos=videos, city=city)

#delete forecast
@app.route("/delete/<forecast_id>", methods=["POST"])
def delete_forecast(forecast_id):
    conn = sqlite3.connect("weather.db")
    c = conn.cursor()
    c.execute("DELETE FROM weather WHERE forecast_id = ?", (forecast_id,))
    conn.commit()
    conn.close()
    return redirect("/saved")

#edit saved forecast
@app.route("/edit/<forecast_id>", methods=["GET", "POST"])
def edit_forecast(forecast_id):
    conn = sqlite3.connect("weather.db")
    c = conn.cursor()

    if request.method == "POST":
        updates = request.form.getlist("forecast")
        c.execute("DELETE FROM weather WHERE forecast_id = ?", (forecast_id,))
        for item in updates:
            city, date, temp, desc = item.split("||")
            c.execute("""
                INSERT INTO weather (forecast_id, city, date, temperature, description)
                VALUES (?, ?, ?, ?, ?)
            """, (forecast_id, city, date, float(temp), desc))
        conn.commit()
        conn.close()
        return redirect("/saved")

    c.execute("SELECT city, date, temperature, description FROM weather WHERE forecast_id = ?", (forecast_id,))
    rows = c.fetchall()
    conn.close()
    forecasts = [{"city": city, "date": date, "temp": temp, "desc": desc} for city, date, temp, desc in rows]
    return render_template("edit.html", forecast_id=forecast_id, forecasts=forecasts)

#view all saved forecasts
@app.route("/saved")
def saved():
    conn = sqlite3.connect("weather.db")
    c = conn.cursor()
    c.execute("SELECT forecast_id, city, date, temperature, description FROM weather ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()

    grouped = {}
    for f_id, city, date, temp, desc in rows:
        if f_id not in grouped:
            grouped[f_id] = {"city": city, "forecasts": []}
        grouped[f_id]["forecasts"].append((date, temp, desc))

    for f_id, data in grouped.items():
        data["forecasts"] = sorted(data["forecasts"], key=lambda x: datetime.strptime(x[0], "%B %d, %Y"))

    entries = [{"forecast_id": f_id, "city": data["city"], "forecasts": data["forecasts"]} for fid, data in grouped.items()]

    return render_template("saved.html", entries=entries)

#export data as json, csv, or pdf
@app.route("/export/<filetype>")
def export(filetype):
   return fileExport.export(filetype, app)

#run app
if __name__ == "__main__":
    db.init_db()
    app.run(debug=True)
