from hashing import hash_password, verify_password

pwd = "password_super_panjang"

hashed = hash_password(pwd)

print("Hash:", hashed)
print("verify: ", verify_password(pwd, hashed))
