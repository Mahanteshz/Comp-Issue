# app.py
from flask import Flask, request, render_template, send_file
import os
from datetime import datetime

app = Flask(__name__)

# Function to generate current timestamp
def get_timestamp():
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H-%M-%S")  # Format as year-month-day_hour-minute-second
    return timestamp

# Specify the output directory and file path with timestamp
def get_output_file_path(prefix='output'):
    timestamp = get_timestamp()
    output_dir = 'output_files/'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_file = os.path.join(output_dir, f'{prefix}-{timestamp}.txt')  # Replace with your desired output file path and format
    return output_file

# Function to process input file by retaining specified columns
def process_file(input_file, output_file, columns_to_keep):
    with open(input_file, 'r', encoding='utf-8') as f_in, open(output_file, 'w', encoding='utf-8') as f_out:
        for line in f_in:
            parts = line.strip().split('\t')
            if len(parts) >= max(columns_to_keep):  # Ensure there are enough columns
                selected_parts = [parts[i] for i in columns_to_keep if i <= len(parts)]
                output_line = '\t'.join(selected_parts)
                f_out.write(output_line + '\n')
            else:
                break

# Function to remove duplicate lines from a file
def remove_duplicates(input_file, output_file):
    unique_lines = set()
    with open(input_file, 'r', encoding='utf-8') as f_in:
        for line in f_in:
            unique_lines.add(line.strip())

    with open(output_file, 'w', encoding='utf-8') as f_out:
        for line in unique_lines:
            f_out.write(line + '\n')

# Function to delete lines from input file based on data file
def delete_lines_from_file(data_file, input_file, output_file):
    with open(data_file, 'r', encoding='utf-8') as data:
        strings_to_retain = {line.strip() for line in data.readlines()}

    with open(input_file, 'r', encoding='utf-8') as input_f:
        lines = input_f.readlines()

    with open(output_file, 'w', encoding='utf-8') as output_f:
        for line in lines:
            words = line.split()
            if any(word in strings_to_retain for word in words):
                output_f.write(line)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            file_path = os.path.join('uploads', file.filename)
            file.save(file_path)

            output_file_1 = get_output_file_path('processed_columns')
            columns_to_keep = [1, 2, 3]  # Specify columns to retain (0-based index)
            process_file(file_path, output_file_1, columns_to_keep)

            output_file_2 = get_output_file_path('unique_lines')
            remove_duplicates(output_file_1, output_file_2)

            data_file = 'data_file.txt'  # Specify the path to your data file
            output_file_4 = get_output_file_path('filtered_lines')
            delete_lines_from_file(data_file, output_file_2, output_file_4)

            return send_file(output_file_4, as_attachment=True)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
