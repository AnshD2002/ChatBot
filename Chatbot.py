import polars as pl
import os
import random
import requests
import re
from datetime import datetime
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, jsonify

# Define your file paths and check if the file exists
dialog_file = "dialogs.txt"
if not os.path.exists(dialog_file):
    raise FileNotFoundError(f"{dialog_file} not found!")

def read_api_key(file_path):
    with open(file_path, 'r') as f:
        api_key = f.read().strip()
    return api_key

# Read API key from file
api_key_file = 'api_key.txt'
api_key = read_api_key(api_key_file)

# Define the Bot class
class Bot:
    greet_commands = {"hey", "hi", "hello", "hola", "heya", "hey there", "howdy", "hi there"}
    exit_commands = {"bye", "exit", "goodbye", "quit", "stop"}
    time_commands = {"time", "time please", "whats the time", "what's the time", "tell me the time"}
    weather_commands = {"weather", "what's the weather", "weather update"}
    news_commands = {"news", "latest news"}
    joke_commands = {"joke", "tell a joke", "tell me a joke"}
    fun_fact_commands = {"fun fact", "tell me a fun fact"}
    small_talk = [
        "That's interesting!",
        "Tell me more!",
        "I see.",
        "Why do you think that?"
    ]

    def __init__(self, dataframe, weather_api_key):
        self.responses = dataframe
        self.context = {}
        self.weather_api_key = weather_api_key

    def get_response(self, input_command):
        input_command = input_command.lower()
        if input_command in self.greet_commands:
            return f"{random.choice(list(self.greet_commands))}"
        elif input_command in self.exit_commands:
            return "Goodbye!"
        elif any(cmd in input_command for cmd in self.weather_commands):
            city = input_command.replace("weather", "").strip()
            if not city:
                return "Please specify a city to get the weather information."
            weather_data = self.get_weather(city)
            if weather_data:
                return (f"Location: {weather_data['location']}\n"
                        f"Temperature: {weather_data['temperature']}°C\n"
                        f"Weather: {weather_data['description']}\n"
                        f"Humidity: {weather_data['humidity']}%\n"
                        f"Wind Speed: {weather_data['wind_speed']} m/s")
            else:
                return "Sorry, I couldn't fetch the weather information right now."
        elif input_command in self.news_commands:
            return self.get_news()
        elif input_command in self.joke_commands:
            return self.tell_joke()
        elif input_command in self.fun_fact_commands:
            return self.tell_fun_fact()
        elif input_command in self.responses["input"].to_list():
            response = self.responses.filter(pl.col("input") == input_command)["output"][0]
            return response
        elif input_command in self.time_commands:
            now = datetime.now()
            return f"Current Time is {now.strftime('%H:%M:%S')}"
        elif input_command.lower() in ["math", "maths"]:
            return "Enter an equation below."
        elif re.match(r'^[0-9\+\-\*/\(\)\s]+$', input_command):
            return self.calculate_math(input_command)
        else:
            return f"I am sorry, I don't understand that. {random.choice(self.small_talk)}"

    def get_weather(self, city):
        base_url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': city,
            'appid': self.weather_api_key,
            'units': 'metric'  # Use 'imperial' for Fahrenheit
        }
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            return {
                'location': data['name'],
                'temperature': data['main']['temp'],
                'description': data['weather'][0]['description'],
                'humidity': data['main']['humidity'],
                'wind_speed': data['wind']['speed']
            }
        else:
            return None

    def get_news(self):
        url = 'https://news.google.com/news/rss'
        res = requests.get(url)
        soup = BeautifulSoup(res.content, 'xml')
        headlines = soup.find_all('title')[1:6]  # Get the first 5 headlines
        news = "\n".join([headline.getText() for headline in headlines])
        return news

    def tell_joke(self):
        jokes = [
            "Why don’t scientists trust atoms? Because they make up everything!",
            "Why did the scarecrow win an award? Because he was outstanding in his field!",
            "Why don't skeletons fight each other? They don't have the guts.",
            "Why did the math book look sad? Because it had too many problems.",
            "What do you call fake spaghetti? An impasta!",
            "Why was the math teacher late to work? Because she took the rhombus.",
            "Why did the bicycle fall over? Because it was two-tired!",
            "Why don't programmers like nature? It has too many bugs.",
            "Why was the stadium so cool? It was filled with fans.",
            "How does a penguin build its house? Igloos it together!"
        ]

        return random.choice(jokes)

    def tell_fun_fact(self):
        fun_facts = [
            "Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still edible.",
            "A day on Venus is longer than a year on Venus. It takes Venus 243 Earth days to rotate once but only 225 Earth days to orbit the Sun.",
            "Bananas are berries, but strawberries aren't.",
            "Octopuses have three hearts. Two pump blood to the gills, while the third pumps it to the rest of the body.",
            "A single strand of spaghetti is called a 'spaghetto'.",
            "There are more stars in the universe than grains of sand on all the world's beaches.",
            "A group of flamingos is called a 'flamboyance'.",
            "Wombat poop is cube-shaped to prevent it from rolling away.",
            "The shortest war in history lasted 38 to 45 minutes, between Britain and Zanzibar on August 27, 1896.",
            "Scotland's national animal is the unicorn."
        ]
        return random.choice(fun_facts)

    def calculate_math(self, equation):
        try:
            result = eval(equation)
            return f"The result of {equation} is {result}"
        except Exception as e:
            return f"Sorry, I couldn't calculate that. Error: {str(e)}"

# Read the TSV file without headers
df = pl.read_csv(dialog_file, separator="\t", has_header=False, new_columns=["input", "output"])

# Initialize Flask application
app = Flask(__name__, static_url_path='/static', static_folder='static')

# Initialize Bot instance
bot = Bot(df, api_key)

# Define route for home page

@app.route("/", methods=["GET", "POST"])
def chat():
    if request.method == "POST":
        user_input = request.json.get("user_input")
        bot_response = bot.get_response(user_input)
        return jsonify({"bot_response": bot_response})
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
