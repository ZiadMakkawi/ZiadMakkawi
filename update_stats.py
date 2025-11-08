import os
import requests
from datetime import datetime

# Get GitHub token from environment
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
USERNAME = os.environ.get('GITHUB_USERNAME', 'YOUR_USERNAME')

headers = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

def get_user_stats():
    """Get basic user statistics"""
    url = f'https://api.github.com/users/{USERNAME}'
    response = requests.get(url, headers=headers)
    data = response.json()
    
    return {
        'name': data.get('name', USERNAME),
        'public_repos': data.get('public_repos', 0),
        'followers': data.get('followers', 0),
        'following': data.get('following', 0)
    }

def get_total_stars():
    """Calculate total stars across all repositories"""
    total_stars = 0
    page = 1
    
    while True:
        url = f'https://api.github.com/users/{USERNAME}/repos?page={page}&per_page=100'
        response = requests.get(url, headers=headers)
        repos = response.json()
        
        if not repos:
            break
            
        for repo in repos:
            total_stars += repo.get('stargazers_count', 0)
        
        page += 1
    
    return total_stars

def get_total_commits():
    """Get total commits across all repositories"""
    total_commits = 0
    page = 1
    
    # Get all repos
    url = f'https://api.github.com/users/{USERNAME}/repos?page={page}&per_page=100'
    response = requests.get(url, headers=headers)
    repos = response.json()
    
    for repo in repos:
        repo_name = repo['name']
        
        # Get commits for each repo
        try:
            commits_url = f'https://api.github.com/repos/{USERNAME}/{repo_name}/commits?author={USERNAME}&per_page=1'
            commits_response = requests.get(commits_url, headers=headers)
            
            # Get total count from Link header if available
            if 'Link' in commits_response.headers:
                links = commits_response.headers['Link']
                if 'rel="last"' in links:
                    last_page = links.split('page=')[-1].split('>')[0].split('&')[0]
                    total_commits += int(last_page)
            elif commits_response.json():
                # If no pagination, count what we got
                total_commits += len(commits_response.json())
        except:
            continue
    
    return total_commits

def get_lines_of_code():
    """Estimate total lines of code (this is approximate)"""
    total_lines = 0
    page = 1
    
    url = f'https://api.github.com/users/{USERNAME}/repos?page={page}&per_page=100'
    response = requests.get(url, headers=headers)
    repos = response.json()
    
    for repo in repos:
        if repo.get('fork'):
            continue
            
        repo_name = repo['name']
        
        # Get languages used in repo
        try:
            lang_url = f'https://api.github.com/repos/{USERNAME}/{repo_name}/languages'
            lang_response = requests.get(lang_url, headers=headers)
            languages = lang_response.json()
            
            # Sum up bytes (approximate for lines)
            for lang, bytes_count in languages.items():
                # Rough estimate: 30 bytes per line on average
                total_lines += bytes_count // 30
        except:
            continue
    
    return total_lines

def update_readme(stats):
    """Update README.md with new statistics"""
    
    readme_content = f"""# Hi there! 👋

I'm a passionate developer working on various projects. Here are my GitHub statistics:

## 📊 GitHub Statistics

<div align="center">

| Metric | Count |
|--------|-------|
| 📦 **Total Repositories** | {stats['public_repos']} |
| ⭐ **Total Stars Received** | {stats['total_stars']} |
| 💻 **Total Commits** | {stats['total_commits']:,} |
| 📝 **Lines of Code** | {stats['lines_of_code']:,}+ |
| 👥 **Followers** | {stats['followers']} |
| 👤 **Following** | {stats['following']} |

</div>

---

<div align="center">

### 🛠️ Technologies & Tools

![Python](https://img.shields.io/badge/-Python-3776AB?style=flat-square&logo=python&logoColor=white)
![JavaScript](https://img.shields.io/badge/-JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black)
![Git](https://img.shields.io/badge/-Git-F05032?style=flat-square&logo=git&logoColor=white)
![GitHub](https://img.shields.io/badge/-GitHub-181717?style=flat-square&logo=github)
![VS Code](https://img.shields.io/badge/-VS%20Code-007ACC?style=flat-square&logo=visual-studio-code)

</div>

---

<div align="center">

*📅 Last Updated: {datetime.now().strftime('%B %d, %Y at %H:%M UTC')}*

*This README is automatically updated using GitHub Actions*

</div>
"""
    
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("✅ README.md updated successfully!")

def main():
    print("🚀 Fetching GitHub statistics...")
    
    # Get all statistics
    user_stats = get_user_stats()
    print(f"✓ User stats retrieved: {user_stats['public_repos']} repos")
    
    total_stars = get_total_stars()
    print(f"✓ Total stars: {total_stars}")
    
    total_commits = get_total_commits()
    print(f"✓ Total commits: {total_commits}")
    
    lines_of_code = get_lines_of_code()
    print(f"✓ Estimated lines of code: {lines_of_code:,}")
    
    # Combine all stats
    stats = {
        **user_stats,
        'total_stars': total_stars,
        'total_commits': total_commits,
        'lines_of_code': lines_of_code
    }
    
    # Update README
    update_readme(stats)
    
    print("✨ All done!")

if __name__ == '__main__':
    main()
