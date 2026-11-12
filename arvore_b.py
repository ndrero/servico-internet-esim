"""
Árvore B.

Regras da árvore B de ordem M:
- cada página guarda no máximo 2M chaves;
- quando uma página passa de 2M chaves, ela é dividida ao meio
  e a chave do meio sobe para a página pai;
- se a raiz se dividir, nasce uma raiz nova e a árvore cresce em altura.
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
        self.max_chaves = 2 * ordem
        self.raiz = Pagina()

    def pesquisar(self, chave):
        pagina = self.raiz
        while True:
            i = 0
            while i < len(pagina.chaves) and chave > pagina.chaves[i]:
                i += 1
            if i < len(pagina.chaves) and chave == pagina.chaves[i]:
                return pagina.elementos[i]   
                # achou
            if pagina.eh_folha():
                return None                  
                # não existe
            pagina = pagina.filhos[i]        
            # desce para o filho certo

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