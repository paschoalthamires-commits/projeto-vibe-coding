import time

def tempo_inicial():
    print("Temporizador iniciado")

def tempo_passivo(seconds):
    for i in range(1, seconds + 1):
        time.sleep(1)
        print(f"Tempo passivo: {i} segundos", end='\r')
    print("\nTemporador terminou!")

tempo_inicial()
while True:
    seconds = input("Digite a quantidade de tempo (inserir por teclado) ou 'sair' para sair do programa: ")
    if seconds.lower() == 'sair':
        break
    try:
        seconds = int(seconds)
    except ValueError:
        print("Erro! Por favor, digite uma quantidade válida.")
        continue
    tempo_passivo(seconds)