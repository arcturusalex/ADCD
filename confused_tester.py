import subprocess
import json


def dependency_checker(language, dependency_list):
    """language has to be npm for JS, pip for python, composer for php and mvn for maven"""
    results_dict = {}
    for dependency in dependency_list:
        result = subprocess.run(['./depconf', '-l', language, dependency], stdout=subprocess.PIPE)
        results_dict[dependency] = result.stdout.decode('utf-8')
    return results_dict

