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
    for root, dirs, files in os.walk("testing"):
            for file in files:
                if file == ".DS_Store":
                    continue
                file_path = os.path.join(root, file)
                
                overarch = root.split("docs/")[1]

                shutil.move(f"input/docs/{overarch}/{file}", "input/unknown")
                if os.path.exists(f'output/dev/text/{overarch}/{file.replace('.pdf', '.txt')}'):
                    os.remove(f'output/dev/text/{overarch}/{file.replace('.pdf', '.txt')}')
                    
                classify_all()

                print(file, check(overarch, file))