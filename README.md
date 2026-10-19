# GlobalSIM — Serviço Internacional de Internet por eSIM

Trabalho prático da disciplina Estruturas de Dados II — Sistemas de Informação, DCET/UNEB.
Profa. Maria Inés Restovic.

Aplicação Web em Python/Flask para administrar os países atendidos, os clientes, os eSIMs e a rede internacional da GlobalSIM, uma empresa fictícia de internet móvel por eSIM. O desenvolvimento é incremental e aplica uma estrutura de dados por etapa:

| Etapa | Estrutura | Aplicação | Status |
|-------|-----------|-----------|--------|
| 1 | Tabela Hash | Países atendidos e consulta de cobertura | Concluída |
| 2 | Árvore B | Clientes, eSIMs e pacotes | A fazer |
| 3 | Grafo | Rede internacional e rotas de menor latência | A fazer |

## Equipe

- Caio Henrique de Souza Alves
- Andrei Rodrigues
- Gustavo Henrique
- Rafael Rodrigues
## Como executar

Pré-requisito: Python 3.

```bash
# criar e ativar o ambiente virtual
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# instalar dependências
pip install flask

# iniciar a aplicação
python main.py
```

Depois, acesse http://127.0.0.1:5000 no navegador.

## Estrutura do projeto

```
servico-internet-esim/
├── main.py              # aplicação Flask e rotas
├── json_handler.py      # leitura e gravação dos arquivos JSON
├── instrumentacao.py    # medição de tempo das operações
├── paises.json          # países cadastrados (persistência)
└── templates/           # páginas HTML (Jinja)
```

## Etapa 1. Tabela Hash

### Estrutura

Os países atendidos ficam em uma tabela hash, implementada com o `dict` do Python, cuja chave é o código internacional de duas letras do país (`BR`, `PT`, `IT`...). Com isso, inserção, busca, alteração e remoção têm custo médio **O(1)**, independentemente da quantidade de países cadastrados.

Exemplo de registro:

```json
{
    "codigo": "IT",
    "pais": "Itália",
    "regiao": "Europa",
    "operadora": "Operadora IT",
    "tecnologia": "5G"
}
```

### Persistência

Ao iniciar, a aplicação carrega o arquivo `paises.json` na tabela hash. Todas as operações são feitas na estrutura em memória, e cada alteração (cadastro, atualização ou remoção) grava a tabela de volta no arquivo.

### Funcionalidades

| Rota | Método | Função |
|------|--------|--------|
| `/` | GET | Formulário de cadastro de país |
| `/cadastrar` | POST | Insere um país (rejeita código duplicado) |
| `/paises` | GET | Lista os países cadastrados |
| `/buscar?codigo=XX` | GET | Consulta a cobertura pelo código do país |
| `/buscar/<codigo>` | GET | Retorna os dados do país em JSON |
| `/atualizar/<codigo>` | GET / POST | Altera os dados de um país |
| `/deletar/<codigo>` | POST | Remove um país |
| `/estatisticas` | GET | Exibe a instrumentação da tabela hash |

As rotas que alteram dados usam POST e redirecionam para a listagem (padrão Post/Redirect/Get).

### Instrumentação

O módulo `instrumentacao.py` mede, com `time.perf_counter_ns()`, o tempo de cada operação na tabela hash: inserção, busca, alteração, remoção e listagem. Para cada operação, guarda a quantidade de execuções e o tempo total. A página `/estatisticas` mostra esses dados junto com o total de registros, o que permite observar que o custo das operações não cresce com o número de países. Cada medição também é exibida no terminal.

## Diferencial: Planejamento de viagens com múltiplos destinos

O cliente cadastra um roteiro com vários países, na ordem em que serão visitados (ex.: `BR → PT → FR → IT`), e o sistema gera um relatório da viagem inteira, combinando as três estruturas:

- **Tabela Hash**: cobertura, operadora e tecnologia de cada destino; destinos sem cobertura são sinalizados.
- **Árvore B**: localiza o cliente e o seu pacote; o sistema verifica se o pacote cobre todas as regiões do roteiro e recomenda um pacote adequado.
- **Grafo**: rota de menor latência (Dijkstra) entre destinos consecutivos e latência total da viagem.
