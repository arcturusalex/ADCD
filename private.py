import requests
import argparse
import json
import confused_tester

parser = argparse.ArgumentParser()
parser.add_argument('-a', "--api_key", help="api key for private repos")
parser.add_argument('-o', "--organisation", help="organisation name found in github URL", required=True)
args = parser.parse_args()

headers = {}
repo_list = []


if args.api_key:
    headers['Authorization'] = f'token {args.api_key}'

def get_repos(header_dict=None): # todo fix args[organisation] to be more generic add as function parameter
    if header_dict is None:
        header_dict = {}
    counter = 0
    while(True):
        req = requests.get(f"https://api.github.com/orgs/{args.organisation}/repos?type=all&page={counter}&per_page=100", headers=header_dict)
        counter += 1
        response = json.loads(req.text)
        if len(response):
            for repo in response:
                repo_list.append(repo['full_name'])
        else:
            return repo_list # if I want to make this more generic in the future


def get_dependency_files(repolist, header_dict={}):
    """needs a list with each entry being org/repo""" # todo should probably just store this as a list of byte files and then write and test on the fly
    jslist = []
    pythonlist = []
    mavenlist = []
    rubylist = []
    phplist = []
    for repo in repolist:
        print(f"checking {repo} for dependencies")
        req = requests.get(f"https://raw.githubusercontent.com/{repo}/master/package.json", headers=header_dict)
        name = repo.replace('/', '')
        if req.status_code == 200:
            with open(f"{name}.package.json", 'w') as f:
                f.write(req.text)
                jslist.append(f"{name}.package.json")
                continue
        req = requests.get(f"https://raw.githubusercontent.com/{repo}/master/requirements.txt", headers=header_dict)
        if req.status_code == 200:
            with open(f"{name}.requirements.txt", 'w') as f:
                f.write(req.text)
                pythonlist.append(f"{name}.requirements.txt")
            continue
        req = requests.get(f"https://raw.githubusercontent.com/{repo}/master/pom.xml", headers=header_dict)
        if req.status_code == 200:
            with open(f"{name}.pom.xml", 'w') as f:
                f.write(req.text)
                mavenlist.append(f"{name}.pom.xml")
            continue
        req = requests.get(f"https://raw.githubusercontent.com/{repo}/master/Gemfile", headers=header_dict)
        if req.status_code == 200:
            with open(f"{name}.Gemfile", 'w') as f:
                f.write(req.text)
                rubylist.append(f"{name}.Gemfile")
            continue
        # todo php composer files - unsure of php project layout for composer - think it's composer.json
    return{"js": jslist, "python": pythonlist, "maven": mavenlist, "ruby": rubylist, "php": phplist}

print("getting repos")
get_repos(headers)
print("checking for dependency files")
dependency_dict = get_dependency_files(repo_list, headers)
final_js_vulns = confused_tester.dependency_checker("npm", dependency_dict['js'])
print("JS results:", final_js_vulns)
final_python_vulns = confused_tester.dependency_checker("pip", dependency_dict['python'])
print("Python results:", final_python_vulns)
final_maven_vulns = confused_tester.dependency_checker("mvn", dependency_dict['maven'])
print("Maven results:", final_maven_vulns)
#confused_tester.dependency_checker("ruby", dependency_dict['ruby']) todo
#confused_tester.dependency_checker("php", dependency_dict['php']) todo
