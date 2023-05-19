import time
import os
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import openai
import logging

import requests

# Log setup
logging.basicConfig(level=logging.INFO)

# Load OpenAI API key
openai.api_key = ("sk-efqaf43t34wt34t45tg3qt2qt")


# Load prompt content
def read_prompt_file(filename):
    with open(filename, "r") as file:
        return file.read()


prompt_content = read_prompt_file("prompt.txt")


def load_parquet(file_path):
    logging.info("Loading Parquet file...")
    df = pd.read_parquet(file_path, engine='pyarrow')
    # make sure the phrases column is a string
    df['phrases'] = df['phrases'].astype(str)
    return df


def save_to_parquet(df, output_file):
    logging.info("Saving DataFrame to Parquet file...")
    print(df.describe())
    print(df['phrases'].apply(type).value_counts())
    df.to_parquet(output_file)


def call_openai_api(chunk):
    logging.info("Calling OpenAI API...")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt_content},
                {"role": "user", "content": f"{chunk}."},
            ],
            max_tokens=1595,
            n=1,
            stop=None,
            temperature=0,
        )
        return response.choices[0]['message']['content'].strip()
    except Exception as e:
        logging.error(f"Error processing chunk: {e}")
        return ""


def split_into_chunks(text, tokens=750):
    chunks = [text[i:i + tokens] for i in range(0, len(text), tokens)]
    return chunks


def process_chunk(chunk):
    return call_openai_api(chunk)


def process_parquet(input_file, output_file):
    df = load_parquet(input_file)
    for idx, row in df.iterrows():
        logging.info(f"Processing row {idx}...")
        phrases = row[2]
        if not isinstance(phrases, str):
            phrases = str(phrases)
        if len(phrases) > 2500:
            phrases = split_into_chunks(phrases, tokens=2500)
            response = ""
            with ThreadPoolExecutor(max_workers=12) as executor:
                results = executor.map(process_chunk, phrases)
                response = "".join(results)
            print("\n\nRESPONSE: \n" + response + "\n\n")
        else:
            response = call_openai_api(phrases)

        df.loc[idx, 'phrases'] = response
        print("\n\nRESPONSE: \n" + response + "\n\n")
        filename = output_file + str(time.strftime("%Y%m%d%H%M", time.localtime())) + "-row-" + str(idx) + ".parquet"
        save_to_parquet(df, filename)
        print(df['phrases'])
        logging.info("Waiting for 30 seconds because of OpenAI API limit")
        time.sleep(30)


if __name__ == "__main__":
    input_file = "data/pdf-phrases18-mai-11-04.parquet"
    output_file = "data/run2/phrases-output-"
    process_parquet(input_file, output_file)
