import os
from pdf2image import convert_from_path
import pytesseract
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import json

docs_path = "input/docs"
text_path = "output/dev/text"
image_path = "output/dev/images"
unkown_path = "input/unknown"

folders = [f for f in os.listdir(docs_path) if os.path.isdir(os.path.join(docs_path, f))]

def extract_text(pdf_path):
    """Extracts text from a PDF file using OCR."""
    text = ''

    try:
        # Convert PDF pages to images
        images = convert_from_path(pdf_path)
        for i, image in enumerate(images):
            if not os.path.exists("output/dev"):
                os.makedirs("output/dev")
            if not os.path.exists(image_path):
                os.makedirs(image_path)
            internal_path = pdf_path.split("/")[2]
            if unkown_path in pdf_path:
                internal_path = "unknown"
                if not os.path.exists(os.path.join(image_path, "unknown")):
                    os.makedirs(os.path.join(image_path, "unknown"))
                image.save(os.path.join(image_path, internal_path, f"unknown_{i}.png"), "PNG")
            else:
                internal_path = pdf_path.split("/")[2]
                if not os.path.exists(os.path.join(image_path, pdf_path.split("/")[2])):
                    os.makedirs(os.path.join(image_path, pdf_path.split("/")[2]))
                image.save(os.path.join(image_path, internal_path, f"{os.path.splitext(os.path.basename(pdf_path))[0]}_{i}.png"), "PNG")
            # Perform OCR on each image
            page_text = pytesseract.image_to_string(image)
            if page_text:
                text += page_text
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
    return text.lower()

def extract_all_text():
    """Extracts text from all PDF files in the docs folder."""
    for folder_title in folders:
        folder_path = os.path.join(docs_path, folder_title)
        text_folder_path = os.path.join(text_path, folder_title)
        
        if not os.path.exists(text_folder_path):
            os.makedirs(text_folder_path)
        
        files = [f for f in os.listdir(folder_path) if f.endswith(".pdf")]
        for file in files:
            if os.path.exists(os.path.join(text_folder_path, f"{os.path.splitext(file)[0]}.txt")):
                continue
            file_path = os.path.join(folder_path, file)
            text = extract_text(file_path)
            
            text_file_path = os.path.join(text_folder_path, f"{os.path.splitext(file)[0]}.txt")
            with open(text_file_path, "w") as text_file:
                text_file.write(text)
            
            print(f"Extracted text from {file_path} to {text_file_path}")

def extract_keywords(text):
    """Extracts keywords from text and keeps track of their counts and order of appearance."""
    # Remove non-alphabetic characters except spaces
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    # Find sequences of alphabetic characters and spaces
    sequences = re.findall(r'[a-zA-Z\s]+', text)
    # Join sequences to form the cleaned text
    cleaned_text = ' '.join(sequences)
    # Tokenize text
    tokens = word_tokenize(cleaned_text)
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    keywords = {}
    order = 0
    
    for sequence in sequences:
        # Add individual words as keywords
        words = sequence.split()
        for i in range(len(words)):
            word = words[i]
            if word and word.lower() not in stop_words and len(word) > 2:
                if word not in keywords:
                    keywords[word] = {'count': 0, 'order': order}
                keywords[word]['count'] += 1
                order += 1
            # Add sequences of at most two words as keywords
            if i < len(words) - 1:
                two_word_sequence = f"{words[i]} {words[i + 1]}"
                if two_word_sequence and two_word_sequence.lower() not in stop_words:
                    if two_word_sequence not in keywords:
                        keywords[two_word_sequence] = {'count': 0, 'order': order}
                    keywords[two_word_sequence]['count'] += 1
                    order += 1
    limited_keywords = {k: keywords[k] for k in list(keywords.keys())[:750]}

    return limited_keywords

def extract_all_keywords(ignore=None):
    """Extracts keywords from all text files in the text folder and saves them to a JSON file."""
    for folder_title in folders:
        folder_path = os.path.join(text_path, folder_title)
        files = [f for f in os.listdir(folder_path) if (f.endswith(".txt") and f != ignore)]
        
        keywords_dict = {}
        for file in files:
            file_path = os.path.join(folder_path, file)
            text = get_text(file_path)
            keywords = extract_keywords(text)
            keywords_dict[get_doc_id(file)] = keywords
        
        # Save the keywords dictionary to a JSON file
        json_file_path = os.path.join(folder_path, f"{folder_title}_keywords.json")
        with open(json_file_path, "w") as json_file:
            json.dump(keywords_dict, json_file, indent=4)
        output_averages(folder_title)

def get_text(file_path):
    """Reads text from a file."""
    with open(file_path, "r") as text_file:
        return text_file.read()
    json_file_path = os.path.join(text_path, folder, f"{os.path.basename(folder)}_keywords.json")
    with open(json_file_path, "r") as json_file:
        return json.load(json_file)

def get_doc_id(doc_title):
    return doc_title.lower().replace(".txt", "").replace(" ", "_")

def get_keywords(folder):
    json_file_path = os.path.join(text_path, folder, f"{os.path.basename(folder)}_keywords.json")
    with open(json_file_path, "r") as json_file:
        return json.load(json_file)

def get_mappings():
    with open(os.path.join("input", "manual_mappings.json"), "r") as json_file:
        return json.load(json_file)

def get_averages(folder_title):
    json_file_path = os.path.join(text_path, folder_title, f"{folder_title}_averages.json")
    with open(json_file_path, "r") as json_file:
        return json.load(json_file)
    
def output_averages(folder_title):
    folder_keywords = get_keywords(folder_title)
    avg_keywords = calculate_average_keywords(folder_keywords)
    
    json_file_path = os.path.join(text_path, folder_title, f"{folder_title}_averages.json")
    with open(json_file_path, "w") as json_file:
        json.dump(avg_keywords, json_file, indent=4)

def get_common_ignore():
    with open(os.path.join("input", "common_keywords.json"), "r") as json_file:
        return json.load(json_file)
    
def calculate_average_keywords(data):
    keyword_stats = {}

    # Aggregate counts and orders for each keyword
    for file_keywords in data.values():
        for keyword, stats in file_keywords.items():
            if keyword not in keyword_stats:
                keyword_stats[keyword] = {'total_count': 0, 'total_order': 0, 'occurrences': 0}
            keyword_stats[keyword]['total_count'] += stats['count']
            keyword_stats[keyword]['total_order'] += stats['order']
            keyword_stats[keyword]['occurrences'] += 1

    # Calculate average count and order for each keyword
    average_keywords = {}
    for keyword, stats in keyword_stats.items():
        average_keywords[keyword] = {
            'avg_count': stats['total_count'] / stats['occurrences'],
            'avg_order': stats['total_order'] / stats['occurrences'],
            'hit_rate': stats['occurrences'] / len(data)
        }
    
    sorted_keywords = dict(sorted(average_keywords.items(), key=lambda item: item[1]['hit_rate'], reverse=True))

    return sorted_keywords

if __name__ == "__main__":
    extract_all_text()