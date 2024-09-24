import os
import git

LOCAL_REPO_PATH = './anycast-census' 
GITHUB_REPO_URL = "https://github.com/anycast-census/anycast-census.git"  

# If reposotory does not exists clone it
# Otherwise just pull changes
def update_cloned_repo(repo_path, repo_url):
    try:
        if not os.path.exists(repo_path):
            print(f"Cloning repository from {repo_url} to {repo_path}...")
            git.Repo.clone_from(repo_url, repo_path) 
            print(f"Repository cloned successfully at {repo_path}")
        else:
            print(f"Repository exists. Pulling the latest changes at {repo_path}...")
            repo = git.Repo(repo_path)
            repo.git.pull()  
            print(f"Repository updated at {repo_path}")
    except Exception as e:
        print(f"Error updating repository: {e}")

update_cloned_repo(LOCAL_REPO_PATH, GITHUB_REPO_URL)
