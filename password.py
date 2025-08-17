import secrets
import string
import sys


if len(sys.argv) < 2:
    print("Usage: python passwords.py <website_name>")
    print("Example: python passwords.py 'example.com'")
    exit()

website = sys.argv[1]
if not website:
    print("Website name cannot be empty.")
    exit()


def generate_password(length=24):
    characters = string.ascii_letters + string.digits + string.punctuation
    return "".join(secrets.choice(characters) for _ in range(length))

password = generate_password()
print(f"{website} - {password}")
