import os
import requests
import io

def get_input_data():
    header_columns = []
    with open('./input/input_data.dsv', mode='r') as file:
        first_line = True
        for line in file:
            columns = line.strip().split("|")
            if first_line:
                first_line = False
                header_columns = columns
                continue
            yield columns

def download_mp3_to_memory(tag: str, url: str) -> tuple[str, bytes]:
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to download file. Status code: {response.status_code}")
    return tag, response.content

def main():
    for data in get_input_data():
        print(data)
