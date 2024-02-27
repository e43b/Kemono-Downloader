import os

print("\nTo download a single post with images, type 1")
print("To download a single text post, type 2")
print("To download all posts with images from a profile, type 3")
print("To download all text posts from a profile, type 4")
print("To download all DMs from a profile, type 5")

opcao = input("\nEnter your option: ")

if opcao == "1":
    # Execute script to download posts with images
    os.system("python scripts/postimg.py")
elif opcao == "2":
    # Execute script to download text posts
    os.system("python scripts/postmessages.py")
elif opcao == "3":
    # Execute script to download all posts with images from a profile
    os.system("python scripts/profileimg.py")
elif opcao == "4":
    # Execute script to download all text posts from a profile
    os.system("python scripts/profilemessages.py")
elif opcao == "5":
    # Execute script to download all DMs from a profile
    os.system("python scripts/profiledms.py")
else:
    print("Invalid option. Please choose a valid one.")
