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
            
        repo_url = repo['clone_url']
        series = get_series_name(repo['name'])
        temp_dir = os.path.join(base_dir, 'temp', repo['name'])
        
        # Clone repository
        Repo.clone_from(repo_url, temp_dir)
        
        # Create series directory if it doesn't exist
        series_dir = os.path.join(base_dir, series)
        os.makedirs(series_dir, exist_ok=True)
        
        # Copy device and stddriver directories
        for dir_name in ['device', 'stddriver']:
            src_dir = os.path.join(temp_dir, 'Library', dir_name)
            dst_dir = os.path.join(series_dir, dir_name)
            
            if os.path.exists(src_dir):
                if os.path.exists(dst_dir):
                    shutil.rmtree(dst_dir)
                shutil.copytree(src_dir, dst_dir)
        
        # Clean up
        shutil.rmtree(temp_dir)

if __name__ == '__main__':
    sync_bsp_files()
