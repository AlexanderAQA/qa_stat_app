import requests
import csv
from datetime import datetime
import os
import matplotlib.pyplot as plt
from flask import Flask, render_template
from io import StringIO
from io import BytesIO  # Import BytesIO from io
import base64

app = Flask(__name__)
# Function to get the number of QA vacancies and links
def get_qa_vacancy_count_and_links():
    search_params = {
        "text": "QA удаленная работа",
        "period": 14,
        "only_with_salary": False,
    }

    api_url = "https://api.hh.ru/vacancies"
    response = requests.get(api_url, params=search_params)

    if response.status_code == 200:
        data = response.json()
        vacancies_count = data.get("found", 0)

        # Get links to QA vacancies
        vacancy_links = [f"https://hh.ru/vacancy/{vacancy['id']}" for vacancy in data.get("items", [])]

        return vacancies_count, vacancy_links
    else:
        return None, None

# Get the current date
current_date = datetime.now().strftime('%Y-%m-%d')

# Get the number of QA vacancies and links
qa_count, qa_links = get_qa_vacancy_count_and_links()

# Check if the CSV file exists and is not empty
csv_exists = os.path.isfile(r'.\qa1.csv') and os.path.getsize(r'.\qa1.csv') > 0

# Update the CSV file
with open(r'.\qa1.csv', 'a', newline='') as csvfile:
    fieldnames = ['Date1', 'Number_of_Vacancies1', 'Links1']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    # If the file is empty, write the header
    if not csv_exists:
        writer.writeheader()
    
    # Write the data to the CSV file
    writer.writerow({'Date1': current_date, 'Number_of_Vacancies1': qa_count, 'Links1': qa_links if qa_links else 'N/A'})

with open(r'.\qa2.csv', 'a', newline='') as csvfile:
    fieldnames = ['Date', 'Number_of_Vacancies']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    # Check if the file is empty and write the header if needed
    if not os.path.getsize(r'.\qa2.csv'):
        writer.writeheader()
    
    # Write the data to the CSV file
    writer.writerow({'Date': current_date, 'Number_of_Vacancies': qa_count})

app = Flask(__name__)

def read_statistics(file_path):
    statistics = []
    with open(file_path, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        next(reader)  # Skip the header row
        for row in reader:
            date = row['Date']
            vacancies = int(row['Number_of_Vacancies'])  # Convert to an integer
            statistics.append((date, vacancies))  # Store data as a tuple
    return statistics

# Generate a graph from the statistics
def generate_graph(statistics):
    dates, vacancies = zip(*statistics)
    plt.figure(figsize=(10, 6))
    plt.plot(dates, vacancies, marker='o', linestyle='-', color='b')
    plt.title("Количество QA-вакансий во времени (только удаленка)")
    plt.xlabel("Дата")
    plt.ylabel("Количество QA-вакансий")
    plt.xticks(rotation=0)
    graph_stream = BytesIO()
    plt.savefig(graph_stream, format="png")
    plt.close()
    graph_stream.seek(0)
    return graph_stream

# Define the route to display the graph
@app.route('/')
def display_graph():
    statistics = read_statistics(r'.\qa2.csv')  # Specify the correct file path
    graph_stream = generate_graph(statistics)

    # Convert the image data to base64
    graph_base64 = base64.b64encode(graph_stream.getvalue()).decode('utf-8')

    return f"<img src='data:image/png;base64,{graph_base64}' alt='QA Vacancies Graph'>"

if __name__ == '__main__':
    app.run(debug=True)

# Print the current date and number of QA vacancies
print(f"Дата: {current_date}")
print(f"Количество вакансий QA (удаленка): {qa_count}")
