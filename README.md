Weather App by Sanskriti Malakar

This is a full-stack weather app built for the AI/ML/Gen AI Engineer Intern Technical Assessment for Product Manager Accelerator (PM Accelerator).

The app lets users search for weather by entering a location (like a city, zip code, or coordinates), view real-time weather and a 5-day forecast, save and manage past searches, and even watch related YouTube videos. It also supports exporting saved data in different formats.

Demo Video: ([link](https://youtu.be/f-WPwlL3Nk0))

Core Functionality
* Search by: City, Zip Code, GPS Coordinates, Landmarks, etc.
* Current Weather: Real-time temperature, weather conditions, and weather icons.
* 5-Day Forecast: Cleanly formatted upcoming weather data.
* Current Location Support: Automatically fetch weather using browser location.
* Error Handling: User-friendly messages for invalid input or API failures.

CRUD Operations
* Create: Save weather info based on user-defined location and date range.
* Read: View all previously saved weather records.
* Update: Edit saved forecast details (e.g., description or temperature).
* Delete: Remove stored weather records.


File Structure & Descriptions
* app.py – Main Flask app. Routes user requests and connects all modules (weather, YouTube, database, export).
* db.py – Handles database operations: create, read, update, delete weather entries.
* weather.py – Communicates with the OpenWeatherMap API to retrieve current and forecast data.
* youtube.py – Integrates the YouTube Data API to fetch location-based travel/weather videos.
* export.py – Supports export of weather data in JSON, CSV, XML, PDF, and Markdown formats.
* templates/ – HTML templates for rendering views (home, results, errors).
* static/ – Contains static frontend assets: CSS, JavaScript, and icons.
* requirements.txt – Lists all required Python libraries and dependencies.

How to run:
    1. Clone the github repo
    2. install the required python packages from the requirements.txt file. like 
    3. Open browser window and use address http://localhost:5000/
