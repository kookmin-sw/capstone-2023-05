import csv
import random

def real_nick_to_dummy():
    with open('real-opinion.csv', 'r') as input_file, open('dummy-opinion.csv', 'w', newline='') as output_file:
        reader = csv.DictReader(input_file)
        writer = csv.DictWriter(output_file, fieldnames=reader.fieldnames)
        writer.writeheader()
        for row in reader:
            row['nickname'] = f"\"Nick{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}\""
            row['comment'] = f"\"{row['comment']}\""
            writer.writerow(row)