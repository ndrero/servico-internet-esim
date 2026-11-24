class Pagina:
    def __init__(self):
        self.chaves = []
        self.elementos = []
        self.filhos = []

    def eh_folha(self):
        return len(self.filhos) == 0


class ArvoreB:
    def __init__(self, ordem=2):
        self.ordem = ordem
        self.max_chaves = 2 * ordem
        self.raiz = Pagina()

        # instrumentação
        self.registros = 0
        self.altura = 1
        self.paginas = 1
        self.splits = 0
        self.ultima_busca = {"paginas_visitadas": 0, "comparacoes": 0, "caminho": []}

    def _localizar(self, chave):
        # desce da raiz até achar a chave, devolve a página, posição ou devolve None
        comparacoes = 0
        caminho = []
        resultado = None
        pagina = self.raiz

        while True:
            caminho.append(list(pagina.chaves))
            i = 0
            while i < len(pagina.chaves):
                comparacoes += 1
                if chave <= pagina.chaves[i]:
                    break
                i += 1

            if i < len(pagina.chaves) and chave == pagina.chaves[i]:
                resultado = (pagina, i)
                break
            if pagina.eh_folha():
                break
            pagina = pagina.filhos[i]

        self.ultima_busca = {
            "paginas_visitadas": len(caminho),
            "comparacoes": comparacoes,
            "caminho": caminho
        }
        return resultado

    def buscar(self, chave):
        achou = self._localizar(chave)
        if achou is None:
            return None
        pagina, i = achou
        return pagina.elementos[i]

    def atualizar(self, chave, elemento):
        achou = self._localizar(chave)
        if achou is None:
            return False
        pagina, i = achou
        pagina.elementos[i] = elemento
        return True

    def inserir(self, chave, elemento):
        if self._localizar(chave) is not None:
            return False                   # chave repetida

        sobe = self._inserir(self.raiz, chave, elemento)
        self.registros += 1

        if sobe is not None:
            # a raiz se dividiu: nasce uma raiz nova e a árvore cresce
            chave_meio, elemento_meio, nova = sobe
            raiz = Pagina()
            raiz.chaves = [chave_meio]
            raiz.elementos = [elemento_meio]
            raiz.filhos = [self.raiz, nova]
            self.raiz = raiz
            self.altura += 1
            self.paginas += 1
        return True

    def _inserir(self, pagina, chave, elemento):
        i = 0
        while i < len(pagina.chaves) and chave > pagina.chaves[i]:
            i += 1

        if pagina.eh_folha():
            pagina.chaves.insert(i, chave)
            pagina.elementos.insert(i, elemento)
        else:
            sobe = self._inserir(pagina.filhos[i], chave, elemento)
            if sobe is not None:
                # o filho se dividiu: a chave do meio entra nesta página
                chave_meio, elemento_meio, nova = sobe
                pagina.chaves.insert(i, chave_meio)
                pagina.elementos.insert(i, elemento_meio)
                pagina.filhos.insert(i + 1, nova)

        if len(pagina.chaves) > self.max_chaves:
            return self._dividir(pagina)
        return None

    def _dividir(self, pagina):
        meio = self.ordem                  # a página está com 2M + 1 chaves
        chave_meio = pagina.chaves[meio]
        elemento_meio = pagina.elementos[meio]

        # metade da direita
        nova = Pagina()
        nova.chaves = pagina.chaves[meio + 1:]
        nova.elementos = pagina.elementos[meio + 1:]
        nova.filhos = pagina.filhos[meio + 1:]

        # metade da esquerda
        pagina.chaves = pagina.chaves[:meio]
        pagina.elementos = pagina.elementos[:meio]
        pagina.filhos = pagina.filhos[:meio + 1]

        self.splits += 1
        self.paginas += 1
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
