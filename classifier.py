
document_to_classify = "Sleep Study Report 1.pdf"

from keys import extract_all_text, unkown_path, extract_text
from llm import classify_llm
import os, json, shutil

def classify(doc_name, auto_move=False, debug=False):
    if debug:
        print("-"*50)
        print("Classifying", doc_name)
        print("Extracting text")

    text = extract_text(os.path.join(unkown_path, doc_name))

    ignore = doc_name.replace(".pdf", ".txt")
    if debug:
        print("Checking for new information")
    extract_all_text()

    if debug:
        print("Classifying...")

    output = classify_llm(text, ignore=ignore)

    print(output)

    category = output.split(",")[0].split("Classification:")[1].strip(" ")
    confidence = output.split(",")[1].split("Confidence_%:")[1].strip(" ")
    reasoning = output.split("Reasoning:")[1].strip(" ")

    classification = {}
    classification["document_name"] = doc_name,
    classification["classification"] = category
    classification["%_match"] = confidence
    classification["reasoning"] = reasoning
    if not os.path.exists("output/classifications"):
        os.makedirs("output/classifications")
    with open(os.path.join('output/classifications', f'{doc_name.replace(" ", "_").replace(".pdf", "")}.json'), 'w') as json_file:
        json.dump(classification, json_file, indent=4)
    if debug:
        print(doc_name, "->" , category)
        print("-"*50)

    if auto_move:
        if debug:
            print("Moving document")
        # add pdf document to the correct folder in docs

        source_path = os.path.join('input', 'unknown', doc_name)
        destination_path = os.path.join('input', 'docs', category, doc_name)
        text_output_path = os.path.join('output', 'dev/text', category, doc_name.replace('.pdf', '.txt'))

    # Move the PDF document to the correct folder
        shutil.move(source_path, destination_path)

        with open(text_output_path, 'w') as text_file:
            text_file.write(text)

        # Delete the original document from the unknown folder
        if os.path.exists(source_path):
            os.remove(source_path)

def classify_all():
    for doc in os.listdir(unkown_path):
        if doc.endswith(".pdf"):
            classify(doc, True)

if __name__ == "__main__":
    for doc in os.listdir(unkown_path):
        if doc.endswith(".pdf"):
            classify(doc, True)
