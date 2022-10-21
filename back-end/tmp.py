from src.internal.auth import *

with open("tmp.txt", "w") as f:

    f.write(get_password_hash("Password1234!"))
