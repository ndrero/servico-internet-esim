"""
Árvore B de ordem M.

- cada página guarda no máximo 2M chaves e, menos a raiz, no mínimo M;
- quando uma página passa de 2M chaves, ela é dividida (split) e a chave
  do meio sobe para o pai; se a raiz se dividir, a árvore cresce em altura.
"""


class Pagina:
    def __init__(self):
        self.chaves = []     # chaves em ordem crescente
        self.elementos = []  # dado de cada chave (ex.: o cliente)
        self.filhos = []     # vazio se a página for folha

    def eh_folha(self):
        return len(self.filhos) == 0


class ArvoreB:
    def __init__(self, ordem=2):
        self.ordem = ordem       # M: mínimo de chaves por página
        self.maximo = 2 * ordem  # 2M: máximo de chaves por página
        self.raiz = Pagina()
        self.splits = 0
        self.ultima_busca = {"paginas_visitadas": 0, "caminho": []}

    def _posicao(self, pagina, chave):
        # primeira posição cuja chave é >= a procurada
        i = 0
        while i < len(pagina.chaves) and chave > pagina.chaves[i]:
            i += 1
        return i

    # ---------------- Busca e alteração ----------------

    def _achar(self, chave):
        # desce da raiz até achar a chave; devolve a página, a posição e o caminho
        caminho = []
        pagina = self.raiz
        while True:
            caminho.append(list(pagina.chaves))
            i = self._posicao(pagina, chave)
            if i < len(pagina.chaves) and pagina.chaves[i] == chave:
                return pagina, i, caminho
            if pagina.eh_folha():
                return None, None, caminho
            pagina = pagina.filhos[i]

    def buscar(self, chave):
        pagina, i, caminho = self._achar(chave)
        self.ultima_busca = {"paginas_visitadas": len(caminho), "caminho": caminho}
        if pagina is None:
            return None
        return pagina.elementos[i]

    def atualizar(self, chave, elemento):
        pagina, i, _ = self._achar(chave)
        if pagina is None:
            return False
        pagina.elementos[i] = elemento
        return True

    # ---------------- Inserção ----------------

    def inserir(self, chave, elemento):
        sobe = self._inserir(self.raiz, chave, elemento)
        if sobe:
            # a raiz se dividiu: nasce uma raiz nova e a árvore cresce em altura
            chave_meio, elemento_meio, nova_pagina = sobe
            nova_raiz = Pagina()
            nova_raiz.chaves = [chave_meio]
            nova_raiz.elementos = [elemento_meio]
            nova_raiz.filhos = [self.raiz, nova_pagina]
            self.raiz = nova_raiz

    def _inserir(self, pagina, chave, elemento):
        i = self._posicao(pagina, chave)
        if i < len(pagina.chaves) and pagina.chaves[i] == chave:
            return None  # chave repetida: não insere

        if pagina.eh_folha():
            pagina.chaves.insert(i, chave)
            pagina.elementos.insert(i, elemento)
        else:
            sobe = self._inserir(pagina.filhos[i], chave, elemento)
            if sobe is None:
                return None
            # o filho se dividiu: a chave do meio entra nesta página
            chave_meio, elemento_meio, nova_pagina = sobe
            pagina.chaves.insert(i, chave_meio)
            pagina.elementos.insert(i, elemento_meio)
            pagina.filhos.insert(i + 1, nova_pagina)

        if len(pagina.chaves) > self.maximo:
            return self._dividir(pagina)
        return None

    def _dividir(self, pagina):
        # corta a página ao meio; devolve a chave do meio e a página nova da direita
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

    # ---------------- Percurso e instrumentação ----------------

    def listar(self):
        # percurso em ordem: sai ordenado pela chave
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

    def niveis(self):
        # chaves de cada página, nível por nível (usado na altura e no nº de páginas)
        resultado = []
        nivel = [self.raiz] if self.raiz.chaves else []
        while nivel:
            resultado.append([pagina.chaves for pagina in nivel])
            nivel = [filho for pagina in nivel for filho in pagina.filhos]
        return resultado

    def tamanho(self):
        return len(self.listar())

    def altura(self):
        return len(self.niveis())

    def resumo(self):
        registros = self.tamanho()
        paginas = sum(len(nivel) for nivel in self.niveis())
        return {
            "ordem": self.ordem,
            "registros": registros,
            "altura": self.altura(),
            "paginas": paginas,
            "ocupacao_media": round(registros / paginas, 2) if paginas else 0,
            "splits": self.splits,
        }
