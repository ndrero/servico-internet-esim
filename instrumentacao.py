import time

# Para cada operação: quantas vezes rodou e o tempo total gasto (em nanossegundos)
estatisticas = {
    "insercao": {"quantidade": 0, "tempo_total_ns": 0},
    "busca": {"quantidade": 0, "tempo_total_ns": 0},
    "alteracao": {"quantidade": 0, "tempo_total_ns": 0},
    "remocao": {"quantidade": 0, "tempo_total_ns": 0},
    "listagem": {"quantidade": 0, "tempo_total_ns": 0},
}

def agora():
    return time.perf_counter_ns()

def registrar(operacao, inicio):
    duracao = agora() - inicio
    estatisticas[operacao]["quantidade"] += 1
    estatisticas[operacao]["tempo_total_ns"] += duracao
    print(f"[instrumentacao] {operacao}: {duracao} ns")
