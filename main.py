import openai
import asyncio
from collections import Counter
import csv
import seaborn as sns 
import matplotlib.pyplot as plt_figure

openai.api_key = "**insert your key here**"

# Asynchronous function to query ChatGPT
async def query_chatgpt(prompt, n):
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, lambda: openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=10,
        n=n,
        stop=None,
        temperature=0.5
    ))
    response_dict = response.to_dict()
    return [choice['message']['content'].strip() for choice in response_dict['choices']]

# Asynchronous function to process prompts
async def process_prompts(prompt, n, word_counts):
    responses = await query_chatgpt(prompt, n)
    for response in responses:
        words = response.split()
        word_counts.update(words)

#Function to plot word_frequencies for each prompt
def plot_word_frequencies(word_counts, prompt, top_n=50):
    top_words = word_counts.most_common(top_n)
    words, counts = zip(*top_words)

    plt_figure.figure(figsize=(12, 6))
    sns.set_style("whitegrid")
    sns.barplot(x=list(words), y=list(counts), palette="viridis")
    plt_figure.title(f"Top Word Frequencies for Prompt: '{prompt}'", fontsize=16)
    plt_figure.xlabel("Words", fontsize=14)
    plt_figure.ylabel("Frequency", fontsize=14)
    plt_figure.show()

# Function to export word frequencies to a CSV file
def export_to_csv(word_counts, file_name="chatgpt_word_frequencies.csv"):
    with open(file_name, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["word", "count"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for word, count in word_counts.items():
            writer.writerow({"word": word, "count": count})

async def main():
    total_n = int(input("Enter the number of times to process the prompt: "))
    prompt = input("Enter the prompt: ")

    word_counts = Counter()
    responses_per_call = 10  # Adjust this value based on your API limits and desired speed

    num_full_calls = total_n // responses_per_call
    remainder = total_n % responses_per_call

    tasks = [process_prompts(prompt, responses_per_call, word_counts) for _ in range(num_full_calls)]

    if remainder > 0:
        tasks.append(process_prompts(prompt, remainder, word_counts))

    await asyncio.gather(*tasks)

    print("\nWord frequencies:")
    for word, count in word_counts.items():
        print(f"{word}: {count}")

    # Export the word frequencies to a CSV file
    export_to_csv(word_counts)
    plot_word_frequencies(word_counts, prompt)

if __name__ == "__main__":
    asyncio.run(main())

