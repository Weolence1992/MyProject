import pytest
import requests
import json

response = requests.get("https://jsonplaceholder.org/users")
res = response.status_code
if res == 200:
    print("ЫФЗТЗП")



