
document_to_classify = "Sleep Study Report 1.pdf"

from keys import get_common_ignore, extract_all_keywords, extract_all_text, calculate_average_keywords, get_averages, get_mappings, extract_text, extract_keywords, get_keywords, folders, unkown_path
import os, json, shutil

def score_word(keyword, keyword_info, averages, manual_keywords, backup_keywords, ignore=[]):
    """"each word is scored out of 10
    """
    score = 0
    if keyword in ignore:
        return score
    if keyword in averages.keys(): # max from here is an 5
        score += (3 * averages[keyword]["hit_rate"])
        order_diff = abs(averages[keyword]["avg_order"] - keyword_info["order"])
        score += 1.5 - min(1.5, order_diff/4)
        count_diff = abs(averages[keyword]["avg_count"] - keyword_info["count"])
        if count_diff == 0:
            score += 1.5
    if keyword in manual_keywords:
        score += 5
    elif keyword in backup_keywords:
        score += 2

    # use regex to get a close to score
    # maybe also check for text patterns?

    return score

def score(keywords, folder_title):
    mappings = get_mappings()
    folder_keywords = get_keywords(folder_title)
    averages = get_averages(folder_title)
    ignore = get_common_ignore()
    avg_keywords = 0
    for file in folder_keywords:
        avg_keywords += len(folder_keywords[file].keys())
    avg_keywords /= len(folder_keywords.keys())

    manual_keywords = mappings[folder_title]["manual_keywords"]

    backup_keywords = []
    for keyword in manual_keywords:
        if ' ' in keyword:
            words = keyword.split()
            backup_keywords.extend(words)

    manual_count = 0
    word_scores = []
    for keyword in keywords:
        if keyword in manual_keywords:
            manual_count += 1
        score = score_word(keyword, keywords[keyword], averages, manual_keywords, backup_keywords, ignore["keys"])
        if score > 0:
            word_scores.append((keyword, score))
    
    # get the top 9 words by score
    word_scores.sort(key=lambda x: x[1], reverse=True)
    word_scores = word_scores[:9]

    sum_scores = sum([x[1] for x in word_scores])

    avg_diff = len(keywords.keys()) - avg_keywords

    if avg_diff == 0:
        sum_scores += 10
    else:
        score += 10 - min(abs(avg_diff)/7, 10)
    
    percentage_hit_in_manual = (manual_count / len(manual_keywords)) * 10 
    sum_scores += percentage_hit_in_manual
    return sum_scores, word_scores, {"length_bonus": 10 - min(abs(avg_diff)/7, 10)}

def classify(doc_name, auto_move=False, debug=False):
    if debug:
        print("-"*50)
        print("Classifying", doc_name)
        print("Extracting text")

    text = extract_text(os.path.join(unkown_path, doc_name))
    keywords = extract_keywords(text)
    if debug:
        print("Extracting keywords")
    ignore = doc_name.replace(".pdf", ".txt")
    if debug:
        print("Checking for new information")
    extract_all_text()
    extract_all_keywords(ignore=ignore)
    if debug:
        print("Scoring")
    scores = []
    for folder_title in folders:
        scores.append((folder_title, score(keywords, folder_title)))
    
    scores.sort(key=lambda x: x[1], reverse=True)
    if not os.path.exists("output/dev"):
        os.makedirs("output/dev")
    if not os.path.exists("output/dev/results"):
        os.makedirs("output/dev/results")
    if debug:
        print(f"Outputting results in classification/{doc_name.replace(" ", "_").replace(".pdf", "")} folder")
    with open(os.path.join('output/dev/results', f'{doc_name.replace(" ", "_").replace(".pdf", "")}_results.json'), 'w') as json_file:
        json.dump(scores, json_file, indent=4)

    if len(scores) > 1:
        top_score = scores[0][1][0]
        next_score = scores[1][1][0]
        match_strength = (top_score - next_score) / top_score * 150
    else:
        match_strength = 100 

    classification = {}
    classification["document_name"] = doc_name,
    classification["classification"] = scores[0][0]
    classification["%_match"] = match_strength
    if not os.path.exists("output/classifications"):
        os.makedirs("output/classifications")
    with open(os.path.join('output/classifications', f'{doc_name.replace(" ", "_").replace(".pdf", "")}.json'), 'w') as json_file:
        json.dump(classification, json_file, indent=4)
    if debug:
        print(doc_name, "->" , scores[0][0])
        print("-"*50)

    if auto_move:
        if debug:
            print("Moving document")
        # add pdf document to the correct folder in docs

        source_path = os.path.join('input', 'unknown', doc_name)
        destination_path = os.path.join('input', 'docs', scores[0][0], doc_name)
        text_output_path = os.path.join('output', 'dev/text', scores[0][0], doc_name.replace('.pdf', '.txt'))

    # Move the PDF document to the correct folder
        shutil.move(source_path, destination_path)

        with open(text_output_path, 'w') as text_file:
            text_file.write(text)

        # Delete the original document from the unknown folder
        if os.path.exists(source_path):
            os.remove(source_path)

    return scores

def classify_all():
    for doc in os.listdir(unkown_path):
        if doc.endswith(".pdf"):
            classify(doc, True)

if __name__ == "__main__":
    for doc in os.listdir(unkown_path):
        if doc.endswith(".pdf"):
            scores = classify(doc, True)
