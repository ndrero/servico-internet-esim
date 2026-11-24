# GlobalSIM — Serviço Internacional de Internet por eSIM

Trabalho prático da disciplina Estruturas de Dados II — Sistemas de Informação, DCET/UNEB.
Profa. Maria Inés Restovic.

Aplicação Web em Python/Flask para administrar os países atendidos, os clientes, os eSIMs e a rede internacional da GlobalSIM, uma empresa fictícia de internet móvel por eSIM. O desenvolvimento é incremental e aplica uma estrutura de dados por etapa:

| Etapa | Estrutura | Aplicação | Status |
|-------|-----------|-----------|--------|
| 1 | Tabela Hash | Países atendidos e consulta de cobertura | Concluída |
| 2 | Árvore B | Clientes, eSIMs e pacotes | Concluída |
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

# (opcional) gerar os ~1.000 clientes de teste em clientes.json
python gerar_clientes.py

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
├── estruturas/
│   └── arvore_b.py      # implementação da Árvore B
├── clientes.py          # clientes na Árvore B (chave: id)
├── gerar_clientes.py    # gera ~1.000 clientes fictícios
├── pacotes.py           # pacotes na Árvore B (chave: código do pacote)
├── roteiro.py           # diferencial: relatório da viagem
├── paises.json          # países cadastrados (persistência)
├── clientes.json        # clientes cadastrados (persistência)
├── pacotes.json         # pacotes disponíveis (persistência)
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
| `/estatisticas` | GET | Exibe a instrumentação das estruturas |

As rotas que alteram dados usam POST e redirecionam para a listagem (padrão Post/Redirect/Get).

### Instrumentação

O módulo `instrumentacao.py` mede, com `time.perf_counter_ns()`, o tempo de cada operação na tabela hash: inserção, busca, alteração, remoção e listagem. Para cada operação, guarda a quantidade de execuções e o tempo total. A página `/estatisticas` mostra esses dados junto com o total de registros, o que permite observar que o custo das operações não cresce com o número de países. Cada medição também é exibida no terminal.

## Etapa 2. Árvore B

### Estrutura

Clientes e pacotes de dados ficam em duas Árvores B (`estruturas/arvore_b.py`): os clientes indexados pelo **id** e os pacotes pelo **código** (`EUR30`, `GLB30`...). A árvore usa a definição por **ordem M** do material da disciplina: cada página guarda de M a 2M chaves (a raiz pode ter menos) e todas as folhas ficam no mesmo nível. A ordem é configurável (`ArvoreB(ordem)`); usamos M = 2. Busca, inserção e alteração custam **O(log n)**.

| Método | O que faz |
|--------|-----------|
| `buscar(chave)` | desce da raiz até achar a chave ou chegar numa folha, contando páginas visitadas e comparações |
| `inserir(chave, elemento)` | insere na folha; se a página passar de 2M chaves, divide (split) e a chave do meio sobe; se a raiz se dividir, a árvore cresce em altura |
| `atualizar(chave, elemento)` | troca os dados guardados na chave |
| `listar()` | percurso em ordem (o resultado sai ordenado pela chave) |

A remoção é opcional no enunciado e não foi implementada.

### Dados

Cliente (campos do enunciado + extras):

```json
{
    "id": 58372,
    "nome": "Maria Silva",
    "email": "maria.silva372@email.com",
    "esim": "ESIM-83921",
    "pacote": "EUR30",
    "status": "ativo",
    "cpf": "12345678900",
    "telefone": "+55 71 99999-0001",
    "pais_origem": "BR"
}
```

`gerar_clientes.py` cria cerca de 1.000 clientes com id e eSIM únicos, pacote existente em `pacotes.json`, status (`ativo`, `inativo` ou `suspenso`) e país de origem existente em `paises.json`. Aceita a quantidade e uma semente: `python gerar_clientes.py 1000 2026`. O arquivo `clientes.json` é sobrescrito.

### Persistência

Ao iniciar, `clientes.json` e `pacotes.json` são carregados nas árvores. Toda busca passa pela árvore. Depois de cada alteração, a árvore é percorrida em ordem e gravada de volta no arquivo.

### Funcionalidades

| Rota | Método | Função |
|------|--------|--------|
| `/clientes` | GET | Lista os clientes em ordem, 50 por página (`?pagina=`); busca por id (`?id=`) |
| `/clientes/cadastrar` | POST | Insere um cliente (rejeita id ou eSIM repetido; eSIM em branco gera um novo) |
| `/clientes/atualizar/<id>` | GET / POST | Altera os dados de um cliente, incluindo eSIM, pacote e status (o id não muda) |
| `/consulta?id=&destino=` | GET | Consulta integrada: cliente na Árvore B × país na Tabela Hash |
| `/pacotes` | GET | Lista os pacotes |
| `/pacotes/cadastrar` | POST | Insere um pacote (rejeita código duplicado) |
| `/pacotes/atualizar/<codigo>` | GET / POST | Altera os dados de um pacote |

### Integração Árvore B × Tabela Hash

A página `/consulta` (menu **Consulta**) recebe o id do cliente e o código do destino e faz duas buscas:

1. `clientes.buscar(id)` na Árvore B: nome, eSIM, status e pacote;
2. `paises.get(codigo)` na Tabela Hash: país, região, operadora e tecnologia.

O resultado mostra as duas respostas juntas e se o pacote do cliente cobre a região do destino.

### Instrumentação

Cada árvore conta: altura, registros, número de páginas (nós), splits, e páginas visitadas, comparações e caminho da última operação (busca, inserção ou alteração). Os tempos das operações são medidos como na Etapa 1, numa tabela separada (`estatisticas_arvore` em `instrumentacao.py`). Tudo aparece em `/estatisticas`.

Uma observação que dá para ver na instrumentação: como o `clientes.json` está ordenado por id, a carga insere as chaves em ordem crescente. Cada split deixa a página da esquerda com só M chaves, que nunca mais recebe inserções. Com isso as páginas ficam perto do mínimo (cerca de 2 chaves por página com M = 2: registros ÷ páginas) e a árvore fica com altura 6 para 1.000 clientes.

## Diferencial: Planejamento de viagens com múltiplos destinos

O cliente cadastra um roteiro com vários países, na ordem em que serão visitados (ex.: `BR → PT → FR → IT`), e o sistema gera um relatório da viagem inteira, combinando as estruturas do trabalho:

- **Tabela Hash**: cobertura, operadora e tecnologia de cada destino; destinos sem cobertura são sinalizados.
- **Árvore B**: localiza o cliente e o seu pacote; o sistema verifica se o pacote cobre todas as regiões do roteiro e recomenda um pacote adequado.
- **Grafo** (Etapa 3, ainda não implementado): rota de menor latência (Dijkstra) entre destinos consecutivos e latência total da viagem.

### Como está implementado

A página `/roteiro` (menu **Viagem**) recebe o id do cliente e os destinos na ordem da viagem (ex.: `BR, PT, FR, IT`). A função `gerar_relatorio` do arquivo `roteiro.py` faz:

1. busca o cliente na Árvore B de clientes pelo id;
2. consulta cada destino na Tabela Hash de países; o que não estiver na tabela aparece como **sem cobertura**;
3. busca o pacote do cliente na Árvore B de pacotes e compara as regiões do pacote com as regiões do roteiro;
4. se faltar alguma região, percorre os pacotes em ordem e recomenda o mais barato que cubra todas.

## Decisões de implementação

- **Tabela Hash**: implementada com o `dict` do Python (aceito pela professora na Etapa 1).
- **Árvore B**: definida pela ordem M do material da disciplina (M a 2M chaves por página), com M = 2 para que as divisões apareçam com poucos registros. A remoção, opcional no enunciado, não foi implementada.
- **Chave dos clientes**: `id` numérico, como no enunciado. CPF, telefone e país de origem ficam como campos extras.
- **Pacotes**: também guardados numa Árvore B, indexados pelo código (o enunciado permite deixá-los em lista).
- **Origem da rota (Etapa 3)**: será o campo `pais_origem` do cliente.

