import os


import json
from uuid import uuid4


interlocutor_id = "0c8d8e0d-6058-460b-b11a-1a112186ad64"
session_id = uuid4()

cookies = {"interlocutor_id": interlocutor_id, "session_id": session_id.__str__()}
print(cookies)
with open("cookies.json", "w", encoding="utf-8") as f:
    json.dump(json.dumps(cookies), f)
