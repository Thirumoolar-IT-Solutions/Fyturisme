import mysql.connector
from abc import ABC, abstractmethod
import requests
import os
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
API_KEY = "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"
print(API_KEY)

# Database connection
class Database:
    def __init__(self):
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="123@456",
            database="fitness_db",
            autocommit=True,
            port=3306
        )
        self.cursor = self.db.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_data (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255),
                age INT,
                weight FLOAT,
                segment VARCHAR(255),
                goal VARCHAR(255),
                calories INT,
                meal TEXT,
                workout TEXT
            )
        ''')
        self.db.commit()

    def save_user_data(self, user):
        query = '''INSERT INTO user_data (name, age, weight, segment, goal, calories, meal, workout)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'''
        values = (user.name, user.age, user.weight, user.segment, user.goal, user.calories, user.meal, user.workout)
        self.cursor.execute(query, values)
        self.db.commit()

# LLM-based prompt generation using Llama API
class LlamaGenerator:
    def __init__(self):
        self.api_key = API_KEY
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

    def generate_response(self, prompt):
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        data = {"model": "llama3-8b-8192", "messages": [{"role": "system", "content": prompt}]}
        try:
            response = requests.post(self.api_url, json=data, headers=headers)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"].strip()
        except requests.exceptions.RequestException as e:
            return f"Error fetching LLM response: {str(e)}"

# Abstract base class for suggestions
class SuggestionStrategy(ABC):
    def __init__(self, llm):
        self.llm = llm

    @abstractmethod
    def get_nutrition(self, weight):
        pass

    @abstractmethod
    def get_workout(self):
        pass

# Concrete suggestion classes for each segment
class StayHomeStrategy(SuggestionStrategy):
    def get_nutrition(self, weight):
        prompt = f"Generate a meal plan for a person staying at home weighing {weight} kg."
        meal = self.llm.generate_response(prompt)
        return weight * 22, meal

    def get_workout(self):
        prompt = "Suggest a home-friendly workout routine."
        return self.llm.generate_response(prompt)

class AwayFromFamilyStrategy(SuggestionStrategy):
    def get_nutrition(self, weight):
        prompt = f"Generate a meal plan for a person who travels frequently and weighs {weight} kg."
        meal = self.llm.generate_response(prompt)
        return weight * 25, meal

    def get_workout(self):
        prompt = "Suggest a workout routine for someone who travels often."
        return self.llm.generate_response(prompt)

class PostPartumStrategy(SuggestionStrategy):
    def get_nutrition(self, weight):
        prompt = f"Generate a meal plan for a postpartum woman weighing {weight} kg."
        meal = self.llm.generate_response(prompt)
        return weight * 28, meal

    def get_workout(self):
        prompt = "Suggest a workout routine for a postpartum woman."
        return self.llm.generate_response(prompt)

class RecoveringStrategy(SuggestionStrategy):
    def get_nutrition(self, weight):
        prompt = f"Generate a meal plan for a person in recovery weighing {weight} kg."
        meal = self.llm.generate_response(prompt)
        return weight * 24, meal

    def get_workout(self):
        prompt = "Suggest a light workout routine for a person recovering from an illness or injury."
        return self.llm.generate_response(prompt)

# Person class to manage user data and suggestions
class Person:
    def __init__(self, name, age, weight, segment, goal, llm):
        self.name = name
        self.age = age
        self.weight = weight
        self.segment = segment
        self.goal = goal
        self.llm = llm
        self.strategy = self._set_strategy()
        self.calories, self.meal = self.strategy.get_nutrition(self.weight)
        self.workout = self.strategy.get_workout()
        self.adjust_calories()

    def _set_strategy(self):
        strategies = {
            "Person stay in the house": StayHomeStrategy(self.llm),
            "Person stay away from family": AwayFromFamilyStrategy(self.llm),
            "Post-partum women": PostPartumStrategy(self.llm),
            "Recovering persons": RecoveringStrategy(self.llm)
        }
        return strategies.get(self.segment, StayHomeStrategy(self.llm))

    def adjust_calories(self):
        if self.goal == "Weight Loss":
            self.calories = int(self.calories * 0.9)
        elif self.goal == "Muscle Gain":
            self.calories = int(self.calories * 1.1)

    def save_to_db(self, db):
        db.save_user_data(self)

# process_input function to handle Streamlit inputs
def process_input(name, age, weight, segment, goal):
    print("Starting process_input...")  # Debug
    try:
        llm = LlamaGenerator()
        print("LLM initialized")  # Debug
        user = Person(name, age, weight, segment, goal, llm)
        print("Person object created")  # Debug
        response = f"Hello {name}! Here’s your plan:\n- Age: {age}\n- Weight: {weight} kg\n- Situation: {segment}\n- Goal: {goal}\n- Calories: {user.calories} kcal\n- Meal: {user.meal}\n- Workout: {user.workout}"
        print("Response generated:", response)  # Debug
        return response
    except Exception as e:
        error_msg = f"Error in process_input: {str(e)}"
        print(error_msg)  # Debug
        return error_msg