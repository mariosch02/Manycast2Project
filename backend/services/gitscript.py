import os
import git
import json

LOCAL_REPO_PATH = '../anycast-census' 
TEST_LOCAL_REPO_PATH = 'backend/anycast-census/2024/03/21' 
GITHUB_REPO_URL = "https://github.com/anycast-census/anycast-census.git"  



# Function to update or clone a repository
def update_cloned_repo(repo_path, repo_url):
    try:
        if not os.path.exists(repo_path):
            print(f"Cloning repository from {repo_url} to {repo_path}...")
            git.Repo.clone_from(repo_url, repo_path) 
            print(f"Repository cloned successfully at {repo_path}")
        else:
            print(f"Repository exists. Pulling the latest changes at {repo_path}...")
            repo = git.Repo(repo_path)
            repo.git.fetch()  # Fetch latest changes
            repo.git.reset('--hard', 'origin/main')  # Replace 'main' with your branch name
            print(f"Repository updated at {repo_path}")
    except Exception as e:
        print(f"Error updating repository: {e}")

# update_cloned_repo(LOCAL_REPO_PATH, GITHUB_REPO_URL)







import os
import git
import json

LOCAL_REPO_PATH = './anycast-census' 
TEST_LOCAL_REPO_PATH = './anycast-census/2024/03/21' 
GITHUB_REPO_URL = "https://github.com/anycast-census/anycast-census.git"  



# Function to update or clone a repository
def update_cloned_repo(repo_path, repo_url):
    try:
        if not os.path.exists(repo_path):
            print(f"Cloning repository from {repo_url} to {repo_path}...")
            git.Repo.clone_from(repo_url, repo_path) 
            print(f"Repository cloned successfully at {repo_path}")
        else:
            print(f"Repository exists. Pulling the latest changes at {repo_path}...")
            repo = git.Repo(repo_path)
            repo.git.fetch()  # Fetch latest changes
            repo.git.reset('--hard', 'origin/main')  # Replace 'main' with your branch name
            print(f"Repository updated at {repo_path}")
    except Exception as e:
        print(f"Error updating repository: {e}")

# # update_cloned_repo(LOCAL_REPO_PATH, GITHUB_REPO_URL)

# # process_directories_only(LOCAL_REPO_PATH)
# # process_year_and_month_directories(LOCAL_REPO_PATH)












# def process_directories_only(repo_path):
#     """Loop through all directories, including hidden, and print them in order."""
#     for root, dirs, files in os.walk(repo_path, topdown=False, followlinks=True):
#         # Sort directories
#         dirs.sort()  # Sort subdirectories

#         print(f"Processing directory: {root}")  # Log the current directory

#         # Log subdirectories
#         # if dirs:
#         #     print(f"Subdirectories found in {root}:")
#         #     for dir in dirs:
#         #         dir_path = os.path.join(root, dir)
#         #         print(f"- {dir_path}")  # Print the path of each subdirectory
                
#         #         # Check if the directory is hidden
#         #         if dir.startswith('.'):
#         #             print(f"  (Hidden directory: {dir})")
        
#         # # Log files in the directory
#         # if files:
#         #     print(f"Files found in {root}:")
#         #     for file in files:
#         #         print(f"- {file}")        

# def process_year_and_month_directories(repo_path):
#     """Loop through year and month directories, reading JSON files."""
#     for root, dirs, files in os.walk(repo_path, topdown=True, followlinks=True):
#         # Sort directories and files
#         dirs.sort()  
#         files.sort()  

#         # Only process the "2024" directory and its month subdirectories
#         if "2024" in root:
#             print(f"Processing directory: {root}")

#             # Read JSON files in the current directory (month subdirectories)
#             for file in files:
#                 if file.endswith('.json') and not file.startswith('.'):  # Ignore hidden files
#                     file_path = os.path.join(root, file)
#                     print(f"  - Reading JSON file: {file_path}")
#                     try:
#                         with open(file_path, 'r') as json_file:
#                             data = json.load(json_file)  # Load JSON data
#                             print(f"    JSON data: {data}")  # Print JSON data
#                     except Exception as e:
#                         print(f"    Error reading {file_path}: {e}")

# # process_year_and_month_directories(LOCAL_REPO_PATH)
                        
def insertData(TEST_LOCAL_REPO_PATH, db):
    Directoryfiles = os.listdir(TEST_LOCAL_REPO_PATH)
    print(Directoryfiles[0])
    file_path = os.path.join(TEST_LOCAL_REPO_PATH, Directoryfiles[0])
    if (os.path.isfile(file_path)):
         if(Directoryfiles[0].endswith(".json")):
            try:
                with open(file_path, 'r') as file:
                        # Parse the JSON content
                    json_data = json.load(file)
                    print(json_data[0]["prefix"])    
                        # Now you have the JSON data, you can print it or process it further
                    # print(json.dumps(json_data, indent=4))  # Pretty-print the JSON
            except json.JSONDecodeError as e:
                print(f"Error reading JSON file {Directoryfiles[0]}: {e}")
            except Exception as e:
                print(f"An error occurred with file {Directoryfiles[0]}: {e}")
    else:
        print(f"Skipping {Directoryfiles[0]}, it is not a file.")
    return str(db)
#     # for item in Directoryfiles:
#     #     file_path = os.path.join(TEST_LOCAL_REPO_PATH, item)
#     #     if (os.path.isfile(file_path)):
#     #         if(item.endswith(".json")):
#     #             try:
#     #                 with open(file_path, 'r') as file:
#     #                     # Parse the JSON content
#     #                     json_data = json.load(file)
                        
#     #                     # Now you have the JSON data, you can print it or process it further
#     #                     print(json.dumps(json_data, indent=4))  # Pretty-print the JSON
#     #             except json.JSONDecodeError as e:
#     #                 print(f"Error reading JSON file {item}: {e}")
#     #             except Exception as e:
#     #                 print(f"An error occurred with file {item}: {e}")
#     #     else:
#     #         print(f"Skipping {item}, it is not a file.")

# insertData(TEST_LOCAL_REPO_PATH)




# # Write a function
# # That goes to ./anycast-census/2024/03/21 
# # Will place each file to the correct tables


# # 1st => 2024-03-21_v4_locations.json 
# # 2nd => 2024-03-32_v4.json [PRIORITY]



  