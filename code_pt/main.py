import os

print("\nPara baixar um único post com imagens digite 1")
print("Para baixar um único post de texto digite 2")
print("Para baixar todos os posts com imagens de um perfil digite 3")
print("Para baixar todos os posts de texto perfil digite 4")
print("Para baixar todas as DMs de um perfil digite 5")

opcao = input("\nDigite sua opção: ")

if opcao == "1":
    # Executa o script para baixar posts com imagem
    os.system("python scripts/postimg.py")
elif opcao == "2":
    # Executar script para baixar posts de texto
    os.system("python scripts/postmessages.py")
elif opcao == "3":
    # Executar script para baixar todos os posts com imagens de um perfil
    os.system("python scripts/profileimg.py")
elif opcao == "4":
    # Executar script para baixar todos os posts de texto de um perfil
    os.system("python scripts/profilemessages.py")
elif opcao == "5":
    # Executar script para baixar todas as DMs um perfil
    os.system("python scripts/profiledms.py")
else:
    print("Opção inválida. Por favor, escolha uma válida.")
