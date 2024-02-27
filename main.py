import os

print("Welcome to Kemono Downloader")
print("\nThis script was created by e42b, access the project repository at https://github.com/e43b/Kemono-Downloader/")

print("\nTo access the script in English, type 1")
print("Para acessar o script em Português digite 2")

option = input("\nEnter your option: ")

if option == "1":
    # Runs the script with the interface in English
    os.system("python code_en/main.py")
elif option == "2":
    # Runs the script with the interface in Portuguese
    os.system("python code_pt/main.py")
else:
    print("Invalid option. Please choose a valid one.")
