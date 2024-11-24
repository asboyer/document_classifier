import google.generativeai as genai
import os, json, shutil
from dotenv import load_dotenv
from keys import get_mappings, get_common_ignore, folders
load_dotenv()

genai.configure(api_key=os.getenv("API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

def create_prompt(unkown_text, images=False, manual=False, common=False, ignore=None):
    prompt = f"""
    Your job is to classify documents. You have been given a document that you need to classify.
    You have been given the text from that document{", as well as one or more images of that document" if images else ""}.
    You have also been given categories of documents that have already been classified.

    The document is one of the following categories: {', '.join(folders)}.

    I am now going to give you all the known information about the documents in each category.
    Each category will be seperated by a line of stars, like this: "*****************".
    Each document will first have the title of the document, followed by the text from that document.
    Each document will be separated by a line of dashes, like this: "-----------------".
    """

    if common:
        prompt += f"""
        Here are some common keywords that will most likely appear across all documents of all categories: {', '.join(get_common_ignore()["keys"])}.
        These keywords are not very helpful in determining the category of a document.
        """

    for category in folders:
        prompt += f"\n{'*'*50}\n"

        if manual:
            mappings = get_mappings()
            prompt += f"""
            This is the information for the {category} category: {mappings[category]["description"]}.
            Some important keywords for this category are: {', '.join(mappings[category]["manual_keywords"])}.
            """

        if images:
            prompt += f"""
            The images are sorted by document. It will be formated like so:
            For a given document, its corresponding images will be titled like so "[document_title]_[i].png", where i will be the index of the image.
            So, for example, if there are three images for a document titled "example1.pdf", the images will be titled like so:
            "example1_0.png", "example1_1.png", and "example1_2.png".
            These are the names of the images in the {category} category:"""
            for file in os.listdir(f"output/dev/images/{category}"):
                if f"{file.split("_")[0]}.txt" == ignore:
                    continue
                prompt += f"\n{file}"

        prompt += f"""
        This is the text from all known documents in the {category} category:
        """
        for file in os.listdir(f"output/dev/text/{category}"):
            if file == ignore:
                continue
            try:
                with open(f"output/dev/text/{category}/{file}", "r", encoding='utf-8') as f:
                    text = f.read()
                    prompt += f"{file}\n{text}\n{'-'*50}\n"
            except UnicodeDecodeError:
                with open(f"output/dev/text/{category}/{file}", "r", encoding='latin-1') as f:
                    text = f.read()
                    prompt += f"{file}\n{text}\n{'-'*50}\n"

    prompt += f"""
    Now that you have all the information, you need to classify the inputted, unknown document.
    Here is the text from that unknown document:
    {unkown_text}
    """

    if images:
        prompt += f"""
        Here are the image titles for the unknown document:
        """
        for file in os.listdir("output/dev/images/unknown"):
            prompt += f"{file}\n"
    
    prompt += f"""
    THIS STEP IS VERY IMPORTANT! OUTPUT YOUR CLASSIFICATION IN THE FOLLOWING FORMAT:
    "Classification: [category]", Confidence_%: [confidence_%], Reasoning: [reasoning]
    For example, if you think the document is in the example category with 80% confidence, you would output:
    "Classification: example", Confidence_%: 80, Reasoning: [reasoning]

    ONLY OUTPUT THE CLASSIFICATION, CONFIDENCE, AND REASONING. DO NOT OUTPUT ANYTHING ELSE.
    """

    return prompt

def classify_llm(unkown_text, images=False, ignore=None, debug=False):
    content = []
    prompt = create_prompt(unkown_text, images=images, ignore=ignore)
    if images:
        if not os.path.exists("output/dev/files.json"):
            with open("output/dev/files.json", "w") as f:
                json.dump({}, f)
        with open("output/dev/files.json", "r") as f:
            files = json.load(f)
        for category in folders:
            for file in os.listdir(f"output/dev/images/{category}"):
                if file == ".DS_Store":
                    continue
                if f"{file.split("_")[0]}.txt" == ignore:
                    continue
                if file in files.keys():
                    if debug:
                        print("Already uploaded", file)
                    content.append(genai.get_file(files[file]))
                    content.append("\n\n")
                    prompt.replace(file, f"{file} aka {files[file]}")
                    continue
                image_path = f"output/dev/images/{category}/{file}"
                myfile = genai.upload_file(mime_type="image/png", path=image_path)
                if debug:
                    print("Uploading", image_path)
                content.append(myfile)
                content.append("\n\n")
                prompt.replace(file, f"{file} aka {myfile.name}")
                files[file] = myfile.name
        
        for file in os.listdir("output/dev/images/unknown"):
            if file == ".DS_Store":
                continue
            image_path = f"output/dev/images/unknown/{file}"
            myfile = genai.upload_file(mime_type="image/png", path=image_path)
            if debug:
                print("Uploading", image_path)
            content.append(myfile)
            content.append("\n\n")
            prompt.replace(file, f"{file} aka {myfile.name}")
            files[file] = myfile.name

        with open("output/dev/files.json", "w") as f:
            json.dump(files, f)
    
    content_strings = []
    if debug:
        for item in content:
            if not type(item) == str:
                content_strings.append(f"{item.name} | {item.display_name}")

    with open("output/dev/prompt.txt", "w") as f:
        f.write(prompt)
        f.write("\n\n")
        f.write('\n'.join(content_strings))

    if images:
        content.append(prompt)
        return model.generate_content(content).text
    else:
        return model.generate_content(prompt).text