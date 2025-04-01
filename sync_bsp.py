import os
import requests
import shutil
from git import Repo
import re

def get_nuvoton_repos():
    repos = []
    page = 1
    while True:
        response = requests.get(f'https://api.github.com/users/OpenNuvoton/repos?page={page}&per_page=100')
        if not response.json():
            break
        repos.extend(response.json())
        page += 1
    return repos

def is_bsp_repo(repo_name):
    return bool(re.match(r'.*BSP.*', repo_name))

def get_series_name(repo_name):
    # Extract NuMicro series name from repository name
    series_match = re.search(r'(M[0-9]+[A-Z]*)', repo_name)
    return series_match.group(1) if series_match else 'Unknown'

def sync_bsp_files():
    repos = get_nuvoton_repos()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    for repo in repos:
        if not is_bsp_repo(repo['name']):
            continue
            
        print(f"\nProcessing repository: {repo['name']}")
        repo_url = repo['clone_url']
        series = get_series_name(repo['name'])
        temp_dir = os.path.join(base_dir, 'temp', repo['name'])
        
        print(f"Cloning from {repo_url} to {temp_dir}")
        try:
            # Clone repository
            # if os.path.exists(temp_dir):
                # shutil.rmtree(temp_dir)
            Repo.clone_from(repo_url, temp_dir)
        except Exception as e:
            print(f"Error cloning repository: {e}")
            continue
        
        # Create series directory if it doesn't exist
        series_dir = os.path.join(base_dir, series)
        print(f"Creating series directory: {series_dir}")
        os.makedirs(series_dir, exist_ok=True)
        
        # Copy device and StdDriver directories
        for dir_name in ['Device', 'StdDriver']:
            src_dir = os.path.join(temp_dir, 'Library', dir_name)
            dst_dir = os.path.join(series_dir, dir_name)
            
            print(f"Checking directory: {src_dir}")
            if os.path.exists(src_dir):
                print(f"Copying {dir_name} from {src_dir} to {dst_dir}")
                # if os.path.exists(dst_dir):
                    # shutil.rmtree(dst_dir)
                shutil.copytree(src_dir, dst_dir)
            else:
                print(f"Warning: Source directory not found: {src_dir}")
        
        # Clean up
        print(f"Cleaning up temporary directory: {temp_dir}")
        # shutil.rmtree(temp_dir)

if __name__ == '__main__':
    sync_bsp_files()
