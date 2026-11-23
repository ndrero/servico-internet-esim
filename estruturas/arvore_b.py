"""
Árvore B.

Regras da árvore B de ordem M:
- cada página guarda no máximo 2M chaves;
- quando uma página passa de 2M chaves, ela é dividida ao meio
  e a chave do meio sobe para a página pai;
- se a raiz se dividir, nasce uma raiz nova e a árvore cresce em altura;
- toda página, menos a raiz, guarda no mínimo M chaves;
- na remoção, se uma página fica com menos de M chaves, ela pega
  uma chave emprestada de uma irmã vizinha ou se junta com ela;
- se a raiz ficar vazia, o filho único vira a raiz e a árvore diminui em altura.

Instrumentação: a árvore conta as divisões (splits), as junções e os
empréstimos da remoção, e quantas páginas foram visitadas e quantas
comparações de chave foram feitas em cada busca.
"""


class Pagina:
    def __init__(self):
        self.chaves = []     # chaves em ordem crescente
        self.elementos = []  # dados de cada chave (ex.: o cliente)
        self.filhos = []     # vazio se a página for folha

    def eh_folha(self):
        return len(self.filhos) == 0


class ArvoreB:
    def __init__(self, ordem=2):
        self.ordem = ordem
        self.min_chaves = ordem
        self.max_chaves = 2 * ordem
        self.raiz = Pagina()

        # instrumentação
        self.splits = 0
        self.juncoes = 0
        self.emprestimos = 0
        self.buscas = 0
        self.total_paginas_visitadas = 0
        self.total_comparacoes = 0
        self.ultima_busca = {"paginas_visitadas": 0, "comparacoes": 0, "caminho": []}

    def pesquisar(self, chave):
        paginas_visitadas = 0
        comparacoes = 0
        caminho = []  # chaves de cada página visitada, da raiz para baixo
        resultado = None

        pagina = self.raiz
        while True:
            paginas_visitadas += 1
            caminho.append(list(pagina.chaves))
            i = 0
            while i < len(pagina.chaves):
                comparacoes += 1
                if chave > pagina.chaves[i]:
                    i += 1
                else:
                    break
            if i < len(pagina.chaves) and chave == pagina.chaves[i]:
                resultado = pagina.elementos[i]  # achou
                break
            if pagina.eh_folha():
                break                            # não existe
            pagina = pagina.filhos[i]            # desce para o filho certo

        self.buscas += 1
        self.total_paginas_visitadas += paginas_visitadas
        self.total_comparacoes += comparacoes
        self.ultima_busca = {
            "paginas_visitadas": paginas_visitadas,
            "comparacoes": comparacoes,
            "caminho": caminho
        }
        return resultado

    # nomes usados no enunciado
    def buscar(self, chave):
        return self.pesquisar(chave)

    def atualizar(self, chave, elemento):
        return self.alterar(chave, elemento)

    def inserir(self, chave, elemento):
        sobe = self._inserir(self.raiz, chave, elemento)
        if sobe:  
            # a raiz se dividiu entao cria uma nova raiz
            chave_meio, elemento_meio, nova_pagina = sobe
            nova_raiz = Pagina()
            nova_raiz.chaves = [chave_meio]
            nova_raiz.elementos = [elemento_meio]
            nova_raiz.filhos = [self.raiz, nova_pagina]
            self.raiz = nova_raiz

    def _inserir(self, pagina, chave, elemento):
        # acha a posição da chave na página
        i = 0
        while i < len(pagina.chaves) and chave > pagina.chaves[i]:
            i += 1
        if i < len(pagina.chaves) and chave == pagina.chaves[i]:
            print("Erro: chave", chave, "já está presente")
            return None

        if pagina.eh_folha():
            pagina.chaves.insert(i, chave)
            pagina.elementos.insert(i, elemento)
        else:
            sobe = self._inserir(pagina.filhos[i], chave, elemento)
            if sobe is None:
                return None
            # o filho se dividiu, entao a chave do meio entra nesta página
            chave_meio, elemento_meio, nova_pagina = sobe
            pagina.chaves.insert(i, chave_meio)
            pagina.elementos.insert(i, elemento_meio)
            pagina.filhos.insert(i + 1, nova_pagina)

        if len(pagina.chaves) > self.max_chaves:
            return self._dividir(pagina)
        return None

    def _dividir(self, pagina):
        self.splits += 1
        meio = len(pagina.chaves) // 2

        nova = Pagina()
        nova.chaves = pagina.chaves[meio + 1:]
        nova.elementos = pagina.elementos[meio + 1:]
        nova.filhos = pagina.filhos[meio + 1:]

        chave_meio = pagina.chaves[meio]
        elemento_meio = pagina.elementos[meio]

        pagina.chaves = pagina.chaves[:meio]
        pagina.elementos = pagina.elementos[:meio]
        pagina.filhos = pagina.filhos[:meio + 1]

        return chave_meio, elemento_meio, nova


    # ---------------- Alteração ----------------

    def alterar(self, chave, elemento):
        # troca os dados guardados na chave (a chave em si não muda)
        pagina = self.raiz
        while True:
            i = self._posicao(pagina, chave)
            if i < len(pagina.chaves) and chave == pagina.chaves[i]:
                pagina.elementos[i] = elemento
                return True
            if pagina.eh_folha():
                return False
            pagina = pagina.filhos[i]

    # ---------------- Remoção ----------------

    def remover(self, chave):
        removeu = self._remover(self.raiz, chave)
        if len(self.raiz.chaves) == 0 and not self.raiz.eh_folha():
            # a raiz ficou vazia, então o filho único vira a raiz
            # e a árvore diminui em altura
            self.raiz = self.raiz.filhos[0]
        return removeu

    def _remover(self, pagina, chave):
        i = self._posicao(pagina, chave)
        achou = i < len(pagina.chaves) and chave == pagina.chaves[i]

        if pagina.eh_folha():
            if not achou:
                return False  # não existe
            pagina.chaves.pop(i)
            pagina.elementos.pop(i)
            return True

        if achou:
            # a chave está numa página interna: troca pela antecessora,
            # que é a maior chave da subárvore da esquerda (sempre numa folha)
            atual = pagina.filhos[i]
            while not atual.eh_folha():
                atual = atual.filhos[-1]
            chave_ant = atual.chaves[-1]
            elemento_ant = atual.elementos[-1]
            self._remover(pagina.filhos[i], chave_ant)
            pagina.chaves[i] = chave_ant
            pagina.elementos[i] = elemento_ant
        else:
            if not self._remover(pagina.filhos[i], chave):
                return False

        # o filho pode ter ficado com menos chaves que o mínimo
        self._corrigir(pagina, i)
        return True

    def _corrigir(self, pai, i):
        filho = pai.filhos[i]
        if len(filho.chaves) >= self.min_chaves:
            return

        esquerda = pai.filhos[i - 1] if i > 0 else None
        direita = pai.filhos[i + 1] if i + 1 < len(pai.filhos) else None

        if esquerda and len(esquerda.chaves) > self.min_chaves:
            self.emprestimos += 1
            # empréstimo da irmã da esquerda: a chave do pai desce para o filho
            # e a maior chave da irmã sobe para o pai
            filho.chaves.insert(0, pai.chaves[i - 1])
            filho.elementos.insert(0, pai.elementos[i - 1])
            pai.chaves[i - 1] = esquerda.chaves.pop()
            pai.elementos[i - 1] = esquerda.elementos.pop()
            if not esquerda.eh_folha():
                filho.filhos.insert(0, esquerda.filhos.pop())
        elif direita and len(direita.chaves) > self.min_chaves:
            self.emprestimos += 1
            # empréstimo da irmã da direita
            filho.chaves.append(pai.chaves[i])
            filho.elementos.append(pai.elementos[i])
            pai.chaves[i] = direita.chaves.pop(0)
            pai.elementos[i] = direita.elementos.pop(0)
            if not direita.eh_folha():
                filho.filhos.append(direita.filhos.pop(0))
        elif esquerda:
            self._juntar(pai, i - 1)
        else:
            self._juntar(pai, i)

    def _juntar(self, pai, i):
        # junta o filho i, a chave i do pai e o filho i + 1 numa página só
        self.juncoes += 1
        esquerda = pai.filhos[i]
        direita = pai.filhos.pop(i + 1)
        esquerda.chaves += [pai.chaves.pop(i)] + direita.chaves
        esquerda.elementos += [pai.elementos.pop(i)] + direita.elementos
        esquerda.filhos += direita.filhos

    def _posicao(self, pagina, chave):
        i = 0
        while i < len(pagina.chaves) and chave > pagina.chaves[i]:
            i += 1
        return i

    # ---------------- Percursos ----------------

    def listar_menores(self, chave):
        # elementos com chave menor que a informada, em ordem
        saida = []
        self._intervalo(self.raiz, None, chave, saida)
        return saida

    def listar_maiores(self, chave):
        # elementos com chave maior que a informada, em ordem
        saida = []
        self._intervalo(self.raiz, chave, None, saida)
        return saida

    def _intervalo(self, pagina, minimo, maximo, saida):
        # percurso em ordem que só desce nas subárvores que podem ter
        # chaves dentro do intervalo (minimo, maximo)
        n = len(pagina.chaves)
        for i in range(n + 1):
            if not pagina.eh_folha():
                acima_do_min = minimo is None or i == n or pagina.chaves[i] > minimo
                abaixo_do_max = maximo is None or i == 0 or pagina.chaves[i - 1] < maximo
                if acima_do_min and abaixo_do_max:
                    self._intervalo(pagina.filhos[i], minimo, maximo, saida)
            if i < n:
                chave = pagina.chaves[i]
                if (minimo is None or chave > minimo) and (maximo is None or chave < maximo):
                    saida.append(pagina.elementos[i])

    def listar_pagina(self, inicio, quantidade):
        # percurso em ordem que pula os 'inicio' primeiros e para depois
        # de juntar 'quantidade' elementos (usado na paginação da listagem)
        saida = []
        self._em_ordem_parcial(self.raiz, [inicio], quantidade, saida)
        return saida

    def _em_ordem_parcial(self, pagina, pular, quantidade, saida):
        for i in range(len(pagina.chaves) + 1):
            if len(saida) >= quantidade:
                return
            if not pagina.eh_folha():
                self._em_ordem_parcial(pagina.filhos[i], pular, quantidade, saida)
            if i < len(pagina.chaves) and len(saida) < quantidade:
                if pular[0] > 0:
                    pular[0] -= 1
                else:
                    saida.append(pagina.elementos[i])

    def listar(self):
        saida = []
        self._em_ordem(self.raiz, saida)
        return saida

    def _em_ordem(self, pagina, saida):
        for i in range(len(pagina.chaves)):
            if not pagina.eh_folha():
                self._em_ordem(pagina.filhos[i], saida)
            saida.append(pagina.elementos[i])
        if not pagina.eh_folha():
            self._em_ordem(pagina.filhos[-1], saida)

    # ---------------- Instrumentação ----------------

    def altura(self):
        if not self.raiz.chaves:
            return 0
        altura = 1
        pagina = self.raiz
        while not pagina.eh_folha():
            pagina = pagina.filhos[0]
            altura += 1
        return altura

    def numero_paginas(self):
        if not self.raiz.chaves:
            return 0
        return self._contar(self.raiz)

    def _contar(self, pagina):
        total = 1
        for filho in pagina.filhos:
            total += self._contar(filho)
        return total

    def tamanho(self):
        return self._contar_chaves(self.raiz)

    def _contar_chaves(self, pagina):
        total = len(pagina.chaves)
        for filho in pagina.filhos:
            total += self._contar_chaves(filho)
        return total

    def resumo(self):
        n_paginas = self.numero_paginas()
        n_chaves = self.tamanho()
        return {
            "ordem": self.ordem,
            "chaves_por_pagina": str(self.min_chaves) + " a " + str(self.max_chaves),
            "registros": n_chaves,
            "altura": self.altura(),
            "paginas": n_paginas,
            "ocupacao_media": round(n_chaves / n_paginas, 2) if n_paginas else 0,
            "splits": self.splits,
            "juncoes": self.juncoes,
            "emprestimos": self.emprestimos,
            "buscas": self.buscas,
            "media_paginas_por_busca": round(self.total_paginas_visitadas / self.buscas, 2) if self.buscas else 0,
            "media_comparacoes_por_busca": round(self.total_comparacoes / self.buscas, 2) if self.buscas else 0,
        }

    def niveis(self):
        resultado = []
        nivel_atual = [self.raiz] if self.raiz.chaves else []
        while nivel_atual:
            resultado.append([pagina.chaves for pagina in nivel_atual])
            proximo = []
            for pagina in nivel_atual:
                proximo.extend(pagina.filhos)
            nivel_atual = proximo
        return resultado

    def imprimir(self, pagina=None, nivel=0):
        if pagina is None:
            pagina = self.raiz
        print("    " * nivel + str(pagina.chaves))
        for filho in pagina.filhos:
            self.imprimir(filho, nivel + 1)