"""
=============================================================
ITEM 6.8 - Testes de Links Afiliados
=============================================================
Cobertura:
  1. Redirecionamento para URL externa do afiliado
  2. Rastreamento de clique (IP, user_agent, pagina_origem)
  3. Rastreamento com usuário autenticado vs. anônimo
  4. Link inativo retorna 404
  5. API de listagem de links ativos (sem filtro)
  6. API de listagem com filtro por tipo
  7. API com tipo inválido retorna lista vazia
=============================================================
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from simulacao.models import LinkAfiliado, CliqueAfiliado

User = get_user_model()


class LinkAfiliadoRedirecionamentoTest(TestCase):
    """Testa o redirecionamento e o rastreamento de cliques."""

    def setUp(self):
        self.client = Client()

        # Cria um link afiliado ativo
        self.link_ativo = LinkAfiliado.objects.create(
            nome='Banco Teste',
            tipo='banco',
            url_afiliado='https://www.bancoteste.com.br/?ref=imobcalc',
            ativo=True,
            comissao_percentual=2.50,
        )

        # Cria um link afiliado inativo
        self.link_inativo = LinkAfiliado.objects.create(
            nome='Banco Inativo',
            tipo='banco',
            url_afiliado='https://www.bancoinativo.com.br/',
            ativo=False,
        )

        # Usuário autenticado
        self.user = User.objects.create_user(
            username='testuser6_8',
            email='testuser68@imobcalc.com',
            password='senha@123',
        )

    # ------------------------------------------------------------------
    # Teste 1 - Redirecionamento para URL do afiliado
    # ------------------------------------------------------------------
    def test_redireciona_para_url_afiliado(self):
        """
        Ao acessar /afiliado/<id>/, o usuário deve ser redirecionado
        para a URL externa do afiliado.
        """
        url = reverse('redirecionar_afiliado', args=[self.link_ativo.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], self.link_ativo.url_afiliado)

    # ------------------------------------------------------------------
    # Teste 2 - Clique é registrado no banco de dados
    # ------------------------------------------------------------------
    def test_clique_registrado_anonimo(self):
        """
        Um clique de usuário anônimo deve ser salvo em CliqueAfiliado
        com usuario=None e o IP registrado.
        """
        url = reverse('redirecionar_afiliado', args=[self.link_ativo.id])
        self.client.get(
            url,
            REMOTE_ADDR='192.168.0.100',
            HTTP_USER_AGENT='TestBrowser/1.0',
            HTTP_REFERER='http://localhost/wizard-v2/resultados/',
        )

        cliques = CliqueAfiliado.objects.filter(link=self.link_ativo)
        self.assertEqual(cliques.count(), 1)

        clique = cliques.first()
        self.assertIsNone(clique.usuario)
        self.assertEqual(clique.ip_address, '192.168.0.100')
        self.assertEqual(clique.user_agent, 'TestBrowser/1.0')
        self.assertEqual(clique.pagina_origem, 'http://localhost/wizard-v2/resultados/')

    # ------------------------------------------------------------------
    # Teste 3 - Clique com usuário autenticado é vinculado ao usuário
    # ------------------------------------------------------------------
    def test_clique_registrado_usuario_autenticado(self):
        """
        Quando um usuário logado clica em um link afiliado, o clique
        deve ser vinculado ao seu registro no banco de dados.
        """
        self.client.login(username='testuser6_8', password='senha@123')
        url = reverse('redirecionar_afiliado', args=[self.link_ativo.id])
        self.client.get(url, REMOTE_ADDR='10.0.0.1')

        clique = CliqueAfiliado.objects.filter(link=self.link_ativo).last()
        self.assertIsNotNone(clique)
        self.assertEqual(clique.usuario, self.user)

    # ------------------------------------------------------------------
    # Teste 4 - Link inativo retorna 404
    # ------------------------------------------------------------------
    def test_link_inativo_retorna_404(self):
        """
        Tentar acessar um link com ativo=False deve retornar HTTP 404.
        """
        url = reverse('redirecionar_afiliado', args=[self.link_inativo.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------
    # Teste 5 - Link inexistente retorna 404
    # ------------------------------------------------------------------
    def test_link_inexistente_retorna_404(self):
        """
        Um ID de link que não existe deve retornar HTTP 404.
        """
        url = reverse('redirecionar_afiliado', args=[9999])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)


class ApiLinksAfiliadosTest(TestCase):
    """Testa a API de listagem de links afiliados."""

    def setUp(self):
        self.client = Client()

        # Links de tipos diferentes
        self.link_banco = LinkAfiliado.objects.create(
            nome='Caixa Econômica',
            tipo='banco',
            url_afiliado='https://www.cef.gov.br/?ref=imobcalc',
            ativo=True,
            descricao='Habitação CEF',
        )
        self.link_consorcio = LinkAfiliado.objects.create(
            nome='Consórcio Nacional',
            tipo='consorcio',
            url_afiliado='https://www.consorcio.com.br/?ref=imobcalc',
            ativo=True,
            descricao='Consórcio imóvel',
        )
        # Link inativo - não deve aparecer na API
        self.link_inativo = LinkAfiliado.objects.create(
            nome='Seguradora Inativa',
            tipo='seguradora',
            url_afiliado='https://www.seguradorainativa.com.br/',
            ativo=False,
        )

    # ------------------------------------------------------------------
    # Teste 6 - API retorna apenas links ativos
    # ------------------------------------------------------------------
    def test_api_retorna_apenas_links_ativos(self):
        """
        GET /api/afiliados/ deve retornar apenas os links com ativo=True,
        com a estrutura JSON correta.
        """
        url = reverse('api_links_afiliados')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertIn('links', data)
        nomes = [l['nome'] for l in data['links']]

        self.assertIn('Caixa Econômica', nomes)
        self.assertIn('Consórcio Nacional', nomes)
        self.assertNotIn('Seguradora Inativa', nomes)

    # ------------------------------------------------------------------
    # Teste 7 - API com filtro por tipo retorna somente aquele tipo
    # ------------------------------------------------------------------
    def test_api_filtro_por_tipo(self):
        """
        GET /api/afiliados/?tipo=banco deve retornar somente links do tipo 'banco'.
        """
        url = reverse('api_links_afiliados') + '?tipo=banco'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        data = response.json()

        for link in data['links']:
            self.assertEqual(link['tipo'], 'banco')

        nomes = [l['nome'] for l in data['links']]
        self.assertIn('Caixa Econômica', nomes)
        self.assertNotIn('Consórcio Nacional', nomes)

    # ------------------------------------------------------------------
    # Teste 8 - API com tipo inválido retorna lista vazia
    # ------------------------------------------------------------------
    def test_api_tipo_invalido_retorna_lista_vazia(self):
        """
        GET /api/afiliados/?tipo=tipoqnaoexiste deve retornar lista vazia,
        sem erro 500.
        """
        url = reverse('api_links_afiliados') + '?tipo=tipoqnaoexiste'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['links'], [])

    # ------------------------------------------------------------------
    # Teste 9 - Estrutura dos campos retornados pela API
    # ------------------------------------------------------------------
    def test_api_estrutura_dos_campos(self):
        """
        Cada item retornado pela API deve conter os campos:
        id, nome, tipo, url, logo, descricao.
        """
        url = reverse('api_links_afiliados')
        response = self.client.get(url)

        data = response.json()
        self.assertGreater(len(data['links']), 0)

        campos_esperados = {'id', 'nome', 'tipo', 'url', 'logo', 'descricao'}
        for link in data['links']:
            self.assertTrue(
                campos_esperados.issubset(link.keys()),
                msg=f"Campos faltando no link '{link.get('nome')}': "
                    f"{campos_esperados - link.keys()}"
            )
