from classifier import classify_all
import os
import shutil

def check(overarch, file_name):
    # check that file got moved to correct directory
    if os.path.exists(f"input/docs/{overarch}/{file_name}"):
        return "Success"
    else:
        return "Failure"

if __name__ == "__main__":
    test_counter = 0
    successes = 0
    for root, dirs, files in os.walk("testing"):
            for file in files:
                if file == ".DS_Store":
                    continue
                file_path = os.path.join(root, file)
                
                overarch = root.split("docs/")[1]


                correct_path_pdf = file
                correct_path_text = file.replace('.pdf', '.txt')

                shutil.move(f"input/docs/{overarch}/{file}", "input/unknown")
                if os.path.exists(f'output/dev/text/{overarch}/{file.replace('.pdf', '.txt')}'):
                    os.remove(f'output/dev/text/{overarch}/{file.replace('.pdf', '.txt')}')
                    
                classify_all(debug=False, images=True)
                test_counter+=1

                result = check(overarch, file)

                print(file, result)

                if result == "Failure":
                    # loop through all files in all directories in input/docs and find the file name
                    for root, dirs, files in os.walk("input/docs"):
                        for file in files:
                            if file == ".DS_Store":
                                continue
                            if file == correct_path_pdf:
                                shutil.move(f"input/docs/{file}", f"input/docs/{overarch}")
                    # loop through all files in all directories in output/dev/text and find the file name
                    for root, dirs, files in os.walk("output/dev/text"):
                        for file in files:
                            if file == ".DS_Store":
                                continue
                            if file == correct_path_text:
                                shutil.move(f"output/dev/text/{file}", f"output/dev/text/{overarch}")
                    
                    for root, dirs, files in os.walk("output/dev/images"):
                        for file in files:
                            if file == ".DS_Store":
                                continue
                            if file.startswith(correct_path_pdf.split(".pdf")[0]):
                                shutil.move(f"output/dev/images/{file}", f"output/dev/images/{overarch}")
                else:
                    successes+=1
    
    print(f"Success rate: {successes}/{test_counter}")