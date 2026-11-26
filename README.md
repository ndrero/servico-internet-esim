# GlobalSIM — Serviço Internacional de Internet por eSIM

Trabalho prático da disciplina Estruturas de Dados II — Sistemas de Informação, DCET/UNEB.
Profa. Maria Inés Restovic.

Aplicação Web em Python/Flask para administrar os países atendidos, os clientes, os eSIMs e a rede internacional da GlobalSIM, uma empresa fictícia de internet móvel por eSIM. O desenvolvimento é incremental e aplica uma estrutura de dados por etapa:

| Etapa | Estrutura | Aplicação | Status |
|-------|-----------|-----------|--------|
| 1 | Tabela Hash | Países atendidos e consulta de cobertura | Concluída |
| 2 | Árvore B | Clientes, eSIMs e pacotes | Em andamento |
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
pip install flask pandas

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
├── clientes.py          # índice Árvore B (cpf -> id) + DataFrame dos clientes
├── gerar_clientes.py    # gera ~1.000 clientes fictícios
├── pacotes.py           # índice Árvore B (código -> id) + DataFrame dos pacotes
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
| `/estatisticas` | GET | Exibe a instrumentação da tabela hash |

As rotas que alteram dados usam POST e redirecionam para a listagem (padrão Post/Redirect/Get).

### Instrumentação

O módulo `instrumentacao.py` mede, com `time.perf_counter_ns()`, o tempo de cada operação na tabela hash: inserção, busca, alteração, remoção e listagem. Para cada operação, guarda a quantidade de execuções e o tempo total. A página `/estatisticas` mostra esses dados junto com o total de registros, o que permite observar que o custo das operações não cresce com o número de países. Cada medição também é exibida no terminal.

## Etapa 2. Árvore B

### Estrutura

Clientes e pacotes de dados são indexados por duas Árvores B (`estruturas/arvore_b.py`). A árvore funciona como **índice**: guarda só a chave e o **id** do registro, e os dados ficam num **DataFrame** do pandas carregado do JSON, que faz o papel do arquivo binário de registros.

| Tabela | Chave na árvore | Elemento na árvore | Dados |
|--------|-----------------|--------------------|-------|
| Clientes | `cpf` | `id` do cliente (índice do DataFrame) | `clientes.json` → DataFrame indexado por `id` |
| Pacotes | `codigo` (`EUR30`, `GLB30`...) | `id` = número da linha no DataFrame | `pacotes.json` → DataFrame (linha 0, 1, 2...) |

Uma busca desce a árvore pela chave, pega o id e lê a linha no DataFrame (`df.loc[id]`). A árvore usa a definição por **ordem M** do material da disciplina: cada página guarda de M a 2M chaves (a raiz pode ter menos) e todas as folhas ficam no mesmo nível. A ordem é configurável (`ArvoreB(ordem)`); usamos M = 2. Busca, inserção, alteração e remoção custam **O(log n)**.

| Método | O que faz |
|--------|-----------|
| `buscar(chave)` | desce da raiz até achar a chave ou chegar numa folha, contando páginas visitadas e comparações |
| `inserir(chave, elemento)` | insere na folha; se a página passar de 2M chaves, divide (split) e a chave do meio sobe; se a raiz se dividir, a árvore cresce em altura |
| `atualizar(chave, elemento)` | troca os dados guardados na chave |
| `remover(chave)` | remove a chave; se uma página ficar com menos de M chaves, pega emprestado de uma irmã ou junta as duas (opcional no enunciado) |
| `listar()` | percurso em ordem (o resultado sai ordenado pela chave) |
| `listar_pagina(inicio, quantidade)` | percurso em ordem que para ao juntar uma página da listagem |
| `listar_menores(chave)` / `listar_maiores(chave)` | percurso em ordem só pelas subárvores que podem ter chaves na faixa |
| `resumo()` / `niveis()` | instrumentação e chaves de cada página, nível por nível |

`pesquisar` e `alterar` são os mesmos métodos com os nomes do material da disciplina.

Na remoção de uma chave que está numa página interna, ela é trocada pela antecessora (a maior chave da subárvore da esquerda, que sempre está numa folha) e a remoção continua na folha. Se a raiz ficar sem chaves, o filho único vira a nova raiz e a árvore diminui de altura.

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

Ao iniciar, `clientes.json` e `pacotes.json` são carregados em DataFrames e cada registro gera uma entrada (chave → id) na sua árvore. Toda busca passa pela árvore; inserção e alteração escrevem no DataFrame, que é gravado de volta no JSON. Um cliente novo recebe o próximo id da tabela; um pacote novo vai para o fim do DataFrame e seu id é a nova posição.

### Funcionalidades

| Rota | Método | Função |
|------|--------|--------|
| `/clientes` | GET | Lista os clientes em ordem, 50 por página (`?pagina=`); busca por CPF (`?cpf=`) mostrando o caminho percorrido na árvore; filtra por faixa (`?filtro=menores\|maiores&referencia=`) |
| `/clientes/cadastrar` | POST | Insere um cliente (rejeita CPF ou eSIM repetido; eSIM em branco gera um novo; o id é gerado) |
| `/clientes/atualizar/<cpf>` | GET / POST | Altera os dados de um cliente, incluindo eSIM, pacote e status (CPF e id não mudam) |
| `/clientes/deletar/<id>` | POST | Remove um cliente |
| `/consulta?cpf=&destino=` | GET | Consulta integrada: cliente na Árvore B × país na Tabela Hash |
| `/pacotes` | GET | Lista os pacotes e desenha as páginas da árvore |
| `/pacotes/cadastrar` | POST | Insere um pacote (rejeita código duplicado) |
| `/pacotes/atualizar/<codigo>` | GET / POST | Altera os dados de um pacote |
| `/pacotes/deletar/<codigo>` | POST | Remove um pacote (bloqueado se algum cliente ainda usa o pacote) |

### Integração Árvore B × Tabela Hash

A página `/consulta` (menu **Consulta**) recebe o CPF do cliente e o código do destino e faz duas buscas:

1. `clientes.buscar(cpf)` na Árvore B (acha o id) e no DataFrame: nome, eSIM, status e pacote;
2. `paises.get(codigo)` na Tabela Hash: país, região, operadora e tecnologia.

O resultado mostra as duas respostas juntas, a instrumentação de cada busca (páginas visitadas, comparações e caminho na árvore; tempo das duas) e se o pacote do cliente cobre a região do destino.

### Instrumentação

Cada árvore conta: altura, número de páginas (nós), ocupação média, splits, junções e empréstimos (da remoção), e páginas visitadas e comparações por busca. Os tempos das operações são medidos como na Etapa 1, numa tabela separada (`estatisticas_arvore` em `instrumentacao.py`). Tudo aparece em `/clientes` e `/estatisticas`.

Uma observação que dá para ver na instrumentação: o `clientes.json` está ordenado por id, mas a chave da árvore é o CPF, que nessa ordem aparece embaralhado. Por isso a carga não insere as chaves em ordem crescente e as páginas ficam mais cheias (cerca de 2,7 chaves por página com M = 2), com altura 5 para 1.000 clientes.

## Diferencial: Planejamento de viagens com múltiplos destinos

O cliente cadastra um roteiro com vários países, na ordem em que serão visitados (ex.: `BR → PT → FR → IT`), e o sistema gera um relatório da viagem inteira, combinando as três estruturas:

- **Tabela Hash**: cobertura, operadora e tecnologia de cada destino; destinos sem cobertura são sinalizados.
- **Árvore B**: localiza o cliente e o seu pacote; o sistema verifica se o pacote cobre todas as regiões do roteiro e recomenda um pacote adequado.
- **Grafo**: rota de menor latência (Dijkstra) entre destinos consecutivos e latência total da viagem.

### Como está implementado

A página `/roteiro` (menu **Viagem**) recebe o CPF do cliente e os destinos na ordem da viagem (ex.: `BR, PT, FR, IT`). A função `gerar_relatorio` do arquivo `roteiro.py` faz:

1. busca o cliente na Árvore B de clientes pelo CPF;
2. consulta cada destino na Tabela Hash de países; o que não estiver na tabela aparece como **sem cobertura**;
3. busca o pacote do cliente na Árvore B de pacotes e compara as regiões do pacote com as regiões do roteiro;
4. se faltar alguma região, percorre os pacotes em ordem e recomenda o mais barato que cubra todas.

## Decisões de implementação

- **Tabela Hash**: implementada com o `dict` do Python (aceito pela professora na Etapa 1).
- **Árvore B**: definida pela ordem M do material da disciplina (M a 2M chaves por página), com M = 2 para que as divisões apareçam com poucos registros. A remoção, opcional no enunciado, foi implementada.
- **Árvore B como índice**: os elementos da árvore são só ids; os registros ficam num DataFrame do pandas carregado do JSON, no lugar de um arquivo binário.
- **Chave dos clientes**: o CPF. O `id` numérico do enunciado continua existindo como índice da linha no DataFrame.
- **Pacotes**: também indexados numa Árvore B pelo código; o id é a posição da linha no DataFrame (o enunciado permite deixá-los em lista).
- **Origem da rota (Etapa 3)**: será o campo `pais_origem` do cliente.

