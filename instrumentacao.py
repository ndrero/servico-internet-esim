import time

# Para cada operação: quantas vezes rodou e o tempo total gasto (em nanossegundos)
estatisticas = {
    "insercao": {"quantidade": 0, "tempo_total_ns": 0},
    "busca": {"quantidade": 0, "tempo_total_ns": 0},
    "alteracao": {"quantidade": 0, "tempo_total_ns": 0},
    "remocao": {"quantidade": 0, "tempo_total_ns": 0},
    "listagem": {"quantidade": 0, "tempo_total_ns": 0},
}

# Mesmas medições para as operações nas Árvores B (clientes e pacotes)
estatisticas_arvore = {
    "insercao": {"quantidade": 0, "tempo_total_ns": 0},
    "busca": {"quantidade": 0, "tempo_total_ns": 0},
    "alteracao": {"quantidade": 0, "tempo_total_ns": 0},
    "listagem": {"quantidade": 0, "tempo_total_ns": 0},
}

def agora():
    return time.perf_counter_ns()

def registrar(operacao, inicio, tabela=estatisticas):
    duracao = agora() - inicio
    tabela[operacao]["quantidade"] += 1
    tabela[operacao]["tempo_total_ns"] += duracao
    estrutura = "arvore b" if tabela is estatisticas_arvore else "hash"
    print(f"[instrumentacao] {estrutura} {operacao}: {duracao} ns")
