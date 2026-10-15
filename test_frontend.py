import unittest
from html.parser import HTMLParser
import copy
import main
from json_handler import json_read, json_write

class SimpleHTMLInspector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.forms = []
        self.inputs = []
        self.links = []
        self.buttons = []
        self._current_form = None

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        if tag == "form":
            form_info = {
                "action": attr_dict.get("action", ""),
                "method": attr_dict.get("method", "get").lower(),
                "inputs": [],
                "buttons": []
            }
            self.forms.append(form_info)
            self._current_form = form_info
        elif tag == "input":
            input_info = {
                "name": attr_dict.get("name"),
                "type": attr_dict.get("type", "text"),
                "id": attr_dict.get("id"),
                "required": "required" in attr_dict
            }
            self.inputs.append(input_info)
            if self._current_form:
                self._current_form["inputs"].append(input_info)
        elif tag == "button":
            btn_info = {
                "type": attr_dict.get("type", "submit"),
                "id": attr_dict.get("id")
            }
            self.buttons.append(btn_info)
            if self._current_form:
                self._current_form["buttons"].append(btn_info)
        elif tag == "a":
            href = attr_dict.get("href")
            if href:
                self.links.append(href)

    def handle_endtag(self, tag):
        if tag == "form":
            self._current_form = None


class TestFrontendParidade(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Salva o estado original do banco json e da memória
        cls.backup_json = json_read("paises.json")
        cls.backup_memory = copy.deepcopy(main.paises)

    @classmethod
    def tearDownClass(cls):
        # Restaura o estado original ao finalizar
        json_write(cls.backup_json, "paises.json")
        main.paises = cls.backup_memory

    def setUp(self):
        main.app.testing = True
        self.client = main.app.test_client()

    def test_01_formulario_cadastro_campos_e_estrutura(self):
        """Verifica se a rota / renderiza o formulário com todos os campos necessários."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200, "A rota / deve retornar status 200")
        
        html = response.data.decode("utf-8")
        inspector = SimpleHTMLInspector()
        inspector.feed(html)

        # Procura o formulário de cadastro
        cadastro_forms = [
            f for f in inspector.forms 
            if f["action"] == "/cadastrar" and f["method"] == "post"
        ]
        self.assertTrue(
            len(cadastro_forms) > 0, 
            "Formulário com action='/cadastrar' e method='POST' não encontrado na página de cadastro."
        )

        form = cadastro_forms[0]
        input_names = {inp["name"] for inp in form["inputs"] if inp["name"]}
        campos_obrigatorios_esperados = {"codigo", "pais", "regiao", "operadora", "tecnologia"}

        self.assertTrue(
            campos_obrigatorios_esperados.issubset(input_names),
            f"Nem todos os campos esperados estão no formulário. Encontrados: {input_names}, Esperados: {campos_obrigatorios_esperados}"
        )

    def test_02_fluxo_submissao_cadastro(self):
        """Verifica se a submissão do formulário cadastra o país e redireciona para /paises."""
        dados_teste = {
            "codigo": "TST",
            "pais": "Pais de Teste",
            "regiao": "Europa",
            "operadora": "Operadora Teste",
            "tecnologia": "5G"
        }
        response = self.client.post("/cadastrar", data=dados_teste, follow_redirects=False)
        self.assertEqual(response.status_code, 302, "Cadastro deve responder com redirecionamento (302)")
        self.assertTrue(
            response.location.endswith("/paises"), 
            f"Deveria redirecionar para /paises, mas redirecionou para: {response.location}"
        )

        # Verifica se foi inserido no dicionário (tabela hash em memória)
        self.assertIn("TST", main.paises, "O país cadastrado deve estar na tabela hash do backend")
        self.assertEqual(main.paises["TST"]["pais"], "Pais de Teste")

    def test_03_listagem_paises_renderizacao_e_delecao(self):
        """Verifica se a página /paises renderiza os dados da tabela hash e os botões de exclusão."""
        response = self.client.get("/paises")
        self.assertEqual(response.status_code, 200, "A rota /paises deve retornar status 200")

        html = response.data.decode("utf-8")
        inspector = SimpleHTMLInspector()
        inspector.feed(html)

        # Verifica se os dados do país de teste cadastrado estão visíveis no HTML
        self.assertIn("TST", html, "O código 'TST' deve ser renderizado na tabela")
        self.assertIn("Pais de Teste", html, "O nome 'Pais de Teste' deve ser renderizado na tabela")
        self.assertIn("Operadora Teste", html, "A operadora deve ser renderizada na tabela")

        # Verifica se existe o formulário para deletar o país cadastrado
        delete_forms = [
            f for f in inspector.forms 
            if f["action"] == "/deletar/TST" and f["method"] == "post"
        ]
        self.assertTrue(
            len(delete_forms) > 0,
            "Não foi encontrado formulário com action='/deletar/TST' e method='POST' para exclusão"
        )

    def test_04_fluxo_submissao_delecao(self):
        """Verifica se a deleção via POST /deletar/<codigo> remove o país e redireciona."""
        self.assertIn("TST", main.paises, "Pré-condição: TST deve existir antes de deletar")

        response = self.client.post("/deletar/TST", follow_redirects=False)
        self.assertEqual(response.status_code, 302, "Deleção deve redirecionar (302)")
        self.assertTrue(
            response.location.endswith("/paises"),
            f"Deveria redirecionar para /paises, mas foi para {response.location}"
        )

        # Verifica se foi removido da tabela hash
        self.assertNotIn("TST", main.paises, "TST não deve mais estar na tabela hash")

        # Verifica se sumiu da página de listagem
        response_list = self.client.get("/paises")
        html_list = response_list.data.decode("utf-8")
        self.assertNotIn("Pais de Teste", html_list, "'Pais de Teste' não deve mais aparecer em /paises")

    def test_05_paridade_de_navegacao(self):
        """Verifica se as duas telas possuem links recíprocos de navegação."""
        # 1. Página de Cadastro deve ter link para /paises
        resp_cad = self.client.get("/")
        insp_cad = SimpleHTMLInspector()
        insp_cad.feed(resp_cad.data.decode("utf-8"))
        has_paises_link = any(link == "/paises" or link.endswith("/paises") for link in insp_cad.links)
        self.assertTrue(has_paises_link, "A tela de cadastro deve conter link para /paises")

        # 2. Página de Países deve ter link para / (ou tela de cadastro)
        resp_paises = self.client.get("/paises")
        insp_paises = SimpleHTMLInspector()
        insp_paises.feed(resp_paises.data.decode("utf-8"))
        has_home_link = any(link == "/" or link.endswith("/") for link in insp_paises.links)
        self.assertTrue(has_home_link, "A tela de países deve conter link para / (Cadastro)")


if __name__ == "__main__":
    unittest.main()
