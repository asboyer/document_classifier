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

                shutil.move(f"input/docs/{overarch}/{file}", "input/unknown")
                if os.path.exists(f'output/dev/text/{overarch}/{file.replace('.pdf', '.txt')}'):
                    os.remove(f'output/dev/text/{overarch}/{file.replace('.pdf', '.txt')}')
                    
                classify_all()
                test_counter+=1


                result = check(overarch, file)

                print(file, result)

                if result == "Failure":
                    os.system("git stash")
                else:
                    os.system("git add .")
                    os.system("git commit -m 'successful test")
                    successes+=1
    
    print(f"Success rate: {successes}/{test_counter}")