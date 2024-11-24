from classifier import classify_all
import os
import shutil
from keys import folders
import time

def check(overarch, file_name):
    # check that file got moved to correct directory
    if os.path.exists(f"input/docs/{overarch}/{file_name}"):
        return "Success"
    else:
        return "Failure"

if __name__ == "__main__":
    start_time = time.time()

    test_counter = 0
    successes = 0
    for r, dirs, f in os.walk("testing"):
        for file in f:
            if file == ".DS_Store":
                continue
            file_path = os.path.join(r, file)

            overarch = r.split("docs/")[1]

            correct_path_pdf = file
            correct_path_text = file.replace('.pdf', '.txt')

            shutil.move(f"input/docs/{overarch}/{file}", "input/unknown")
            if os.path.exists(f'output/dev/text/{overarch}/{file.replace('.pdf', '.txt')}'):
                os.remove(f'output/dev/text/{overarch}/{file.replace('.pdf', '.txt')}')
                
            classify_all(debug=True, images=True)
            test_counter+=1

            result = check(overarch, file)

            print(file, result)

            if result == "Failure":
                # loop through all files in all directories in input/docs and find the file name
                for category in folders:
                    for file in os.listdir(f"input/docs/{category}"):
                        if file == ".DS_Store":
                            continue
                        if os.path.exists(f"input/docs/{overarch}/{file}") and file == correct_path_pdf:
                            pass
                        elif file == correct_path_pdf:
                            shutil.move(f"input/docs/{category}/{file}", f"input/docs/{overarch}")
                    for file in os.listdir(f"output/dev/text/{category}"):
                        if file == ".DS_Store":
                            continue
                        if os.path.exists(f"output/dev/text/{overarch}/{file}") and file == correct_path_text:
                            pass
                        elif file == correct_path_text:
                            shutil.move(f"output/dev/text/{category}/{file}", f"output/dev/text/{overarch}")
                    for file in os.listdir(f"output/dev/images/{category}"):
                        if file == ".DS_Store":
                            continue

                    # is it in the right dir? then remove from wrong dir
                    if os.path.exists(f"output/dev/images/{overarch}/{file}") and file.startswith(correct_path_pdf.split(".pdf")[0]) and overarch != category:
                        os.remove(f"output/dev/images/{category}/{file}")
                    # is it in the wrong dir and not in the right dir? then move to right dir
                    if not os.path.os.path.exists(f"output/dev/images/{overarch}/{file}") and file.startswith(correct_path_pdf.split(".pdf")[0]) and overarch != category:
                        shutil.move(f"output/dev/images/{category}/{file}", f"output/dev/images/{overarch}")
                    # is it in the wrong dir and in the right dir? then remove from wrong dir
                    # 
            else:
                successes+=1
    end_time = time.time()  # End the timer
    total_time = end_time - start_time
    print(f"Success rate: {successes}/{test_counter}", f"Total time: {total_time}")