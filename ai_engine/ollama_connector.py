import ollama

def testar_conexao():
    try:
        # Aqui ele pede a lista de modelos para o seu Ollama
        modelos = ollama.list()
        print("✅ Conexão com Ollama realizada com sucesso!")
        print("Modelos encontrados na sua máquina:")
        
        # Ajuste aqui: trocamos m['name'] por m.model
        for m in modelos.models:
            print(f"- {m.model}")
            
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")

if __name__ == "__main__":
    testar_conexao()
