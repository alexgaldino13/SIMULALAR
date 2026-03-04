# 🤖 PROMPT PARA GEMINI - Continuação do Projeto ImobCalc

Olá Gemini! Sou a **Vy**, assistente de IA que está trabalhando com o **Galdino** no projeto **ImobCalc**. Você vai me ajudar a completar a **FASE 2 - LGPD** do projeto. Vamos trabalhar juntos como uma equipe!

---

## 📍 CONTEXTO DO PROJETO

**Localização:** `D:\projetos\FI`  
**Projeto:** ImobCalc - Melhor simulador de compra de imóveis do Brasil  
**Tecnologia:** Django 4.2 + Python 3.x  
**Servidor:** http://127.0.0.1:8000  
**Admin:** http://127.0.0.1:8000/admin/ (admin / admin123456)

---

## ✅ O QUE JÁ ESTÁ PRONTO

### FASE 1 - 100% COMPLETA ✅
- Sistema de autenticação Django completo
- Models: CustomUser, UserProfile, SavedSimulation, SimulationShare
- Views: login, register, logout, dashboard, profile, password_reset
- Templates: 6 telas HTML com design gradient roxo (#667eea to #764ba2)
- OAuth Google configurado
- Sistema de sessões (14/30 dias)
- 2 Middlewares customizados

### FASE 2 - 50% COMPLETA 🔄
- ✅ **2.1** - Models LGPD criados (`simulacao/lgpd_models.py`):
  - ConsentManagement (8 tipos de consentimento)
  - DataAccessLog (6 tipos de acesso)
  - DataDeletionRequest (4 status)

- ✅ **2.2** - Tela de consentimento (`simulacao/templates/simulacao/lgpd/consent.html`)
  - 8 tipos de consentimento com checkboxes
  - Design moderno com gradient roxo
  - Validação JavaScript

- ✅ **2.3** - Sistema opt-in (`simulacao/lgpd_views.py`):
  - 8 views LGPD implementadas
  - URLs configuradas em `simulacao/urls.py`
  - Logs automáticos de auditoria

- ✅ **2.4** - Criptografia (`simulacao/encryption.py`):
  - Fernet (AES-128)
  - Funções para CPF e valores monetários
  - Mascaramento para exibição

---

## 🎯 SUA MISSÃO

Completar os **4 itens restantes da FASE 2**:

### 📝 Item 2.5 - Criar Política de Privacidade

**Arquivo a criar:** `D:\projetos\FI\simulacao\templates\simulacao\lgpd\privacy_policy.html`

**Requisitos:**
1. Template HTML completo com design consistente (gradient roxo #667eea to #764ba2)
2. Deve incluir as seguintes seções LGPD:
   - **Introdução** - Quem somos, responsável pelo tratamento
   - **Dados Coletados** - Pessoais (nome, email, CPF), financeiros (renda), navegação
   - **Finalidade** - Para que usamos os dados
   - **Base Legal** - Consentimento, execução de contrato (Art. 7º LGPD)
   - **Compartilhamento** - Com quem compartilhamos (consórcios, corretoras, bancos)
   - **Direitos do Titular** - Acesso, retificação, exclusão, portabilidade, revogação
   - **Segurança** - Criptografia Fernet, logs de auditoria
   - **Cookies** - Quais usamos e para quê
   - **Alterações** - Como comunicamos mudanças
   - **Contato DPO** - Email: dpo@imobcalc.com.br

3. Usar o mesmo padrão visual de `consent.html`
4. Adicionar data de última atualização: 01/02/2026
5. Versão 1.0
6. Botão "Voltar" para página anterior

**Teste:**
```bash
# Iniciar servidor
cd D:\projetos\FI
python manage.py runserver

# Acessar
http://127.0.0.1:8000/privacy/
```

**Verificar:**
- ✅ Design consistente com outras páginas
- ✅ Todas as 10 seções presentes
- ✅ Texto claro e objetivo
- ✅ Responsivo para mobile

---

### 📜 Item 2.6 - Criar Termos de Uso

**Arquivo a criar:** `D:\projetos\FI\simulacao\templates\simulacao\lgpd\terms_of_service.html`

**Requisitos:**
1. Template HTML completo com design consistente
2. Deve incluir as seguintes seções:
   - **Aceitação dos Termos** - Ao usar o serviço, você aceita
   - **Descrição do Serviço** - O que é o ImobCalc
   - **Cadastro e Conta** - Responsabilidades do usuário
   - **Planos** - Free (com anúncios) vs Premium (sem anúncios + features)
   - **Uso Aceitável** - O que é proibido fazer
   - **Propriedade Intelectual** - Direitos autorais do ImobCalc
   - **Limitação de Responsabilidade** - Não somos consultores financeiros
   - **Rescisão** - Como cancelar conta
   - **Lei Aplicável** - Lei brasileira, foro de São Paulo
   - **Alterações** - Podemos alterar os termos
   - **Contato** - suporte@imobcalc.com.br

3. Usar o mesmo padrão visual
4. Adicionar data de última atualização: 01/02/2026
5. Versão 1.0
6. Botão "Voltar" para página anterior

**Teste:**
```bash
# Acessar
http://127.0.0.1:8000/terms/
```

**Verificar:**
- ✅ Design consistente
- ✅ Todas as 11 seções presentes
- ✅ Linguagem clara
- ✅ Responsivo

---

### 🔍 Item 2.7 - Implementar Logs de Auditoria Automáticos

**Arquivos a modificar:**
1. `D:\projetos\FI\simulacao\lgpd_views.py` (adicionar decorator)
2. `D:\projetos\FI\simulacao\views.py` (aplicar decorator)

**Requisitos:**

**1. Criar decorator `@audit_log`** no final de `lgpd_views.py`:

```python
from functools import wraps

def audit_log(action_type, data_type, description=None):
    """
    Decorator para registrar automaticamente logs de auditoria.
    
    Uso:
    @audit_log('READ', 'USER_DATA', 'Usuário acessou dashboard')
    def minha_view(request):
        ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Executar view
            response = view_func(request, *args, **kwargs)
            
            # Registrar log se usuário autenticado
            if request.user.is_authenticated:
                desc = description or f'Acesso via {view_func.__name__}'
                DataAccessLog.log_access(
                    user=request.user,
                    accessed_by=request.user,
                    access_type=action_type,
                    data_type=data_type,
                    description=desc,
                    ip_address=get_client_ip(request),
                    user_agent=get_user_agent(request)
                )
            
            return response
        return wrapper
    return decorator
```

**2. Aplicar decorator nas views existentes** em `views.py`:

```python
from simulacao.lgpd_views import audit_log

@login_required
@audit_log('READ', 'DASHBOARD', 'Usuário acessou dashboard')
def dashboard(request):
    ...

@login_required
@audit_log('READ', 'PROFILE', 'Usuário visualizou perfil')
def profile_view(request):
    ...
```

**3. Criar view de auditoria** em `lgpd_views.py`:

```python
@login_required
def audit_logs_view(request):
    """
    Exibe logs de auditoria do usuário.
    """
    # Buscar logs do usuário
    logs = DataAccessLog.objects.filter(user=request.user).order_by('-accessed_at')
    
    # Filtros
    access_type = request.GET.get('type')
    if access_type:
        logs = logs.filter(access_type=access_type)
    
    # Paginação (20 por página)
    from django.core.paginator import Paginator
    paginator = Paginator(logs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'access_types': DataAccessLog.ACCESS_TYPE_CHOICES,
    }
    
    return render(request, 'simulacao/lgpd/audit_logs.html', context)
```

**4. Adicionar URL** em `urls.py`:

```python
path('audit-logs/', lgpd_views.audit_logs_view, name='audit_logs'),
```

**5. Criar template** `D:\projetos\FI\simulacao\templates\simulacao\lgpd\audit_logs.html`:
- Tabela com: Data/Hora, Tipo de Acesso, Tipo de Dado, Descrição, IP
- Filtros por tipo de acesso
- Paginação
- Design consistente

**Teste:**
```python
# Django shell
cd D:\projetos\FI
python manage.py shell

from simulacao.lgpd_models import DataAccessLog
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.first()

# Ver logs
logs = DataAccessLog.objects.filter(user=user)
for log in logs[:5]:
    print(f"{log.accessed_at} - {log.access_type} - {log.data_type} - {log.description}")
```

**Verificar:**
- ✅ Decorator funciona sem erros
- ✅ Logs são criados automaticamente
- ✅ Página de auditoria mostra logs
- ✅ Filtros funcionam
- ✅ Paginação funciona

---

### ✅ Item 2.8 - Testar Conformidade LGPD

**Arquivo a criar:** `D:\projetos\FI\simulacao\tests\test_lgpd.py`

**Requisitos:**

Criar pasta `tests` se não existir:
```bash
mkdir D:\projetos\FI\simulacao\tests
echo. > D:\projetos\FI\simulacao\tests\__init__.py
```

Criar testes automatizados:

```python
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from simulacao.lgpd_models import ConsentManagement, DataAccessLog, DataDeletionRequest
from simulacao.encryption import encrypt_cpf, decrypt_cpf
import json

User = get_user_model()

class LGPDComplianceTests(TestCase):
    """Testes de conformidade LGPD"""
    
    def setUp(self):
        """Configuração inicial dos testes"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@imobcalc.com',
            password='Test@123456',
            first_name='Test',
            last_name='User'
        )
        self.user.aceitou_termos = True
        self.user.aceitou_privacidade = True
        self.user.save()
    
    def test_consent_required_for_registration(self):
        """Teste: Registro requer consentimento de termos e privacidade"""
        # Tentar registrar sem aceitar termos
        response = self.client.post('/register/', {
            'username': 'newuser',
            'email': 'new@test.com',
            'password1': 'Test@123456',
            'password2': 'Test@123456',
            'consent_terms': '0',  # Não aceito
            'consent_privacy': '1',
        })
        
        # Deve falhar
        self.assertContains(response, 'precisa aceitar', status_code=200)
    
    def test_user_can_revoke_consent(self):
        """Teste: Usuário pode revogar consentimento"""
        # Criar consentimento
        consent = ConsentManagement.objects.create(
            user=self.user,
            consent_type='MARKETING',
            granted=True
        )
        
        # Revogar
        self.client.login(username='testuser', password='Test@123456')
        response = self.client.post(f'/revoke-consent/MARKETING/')
        
        # Verificar
        consent.refresh_from_db()
        self.assertFalse(consent.granted)
        self.assertIsNotNone(consent.revoked_at)
    
    def test_data_access_is_logged(self):
        """Teste: Acessos a dados são registrados"""
        # Login
        self.client.login(username='testuser', password='Test@123456')
        
        # Acessar dashboard
        response = self.client.get('/dashboard/')
        
        # Verificar log
        logs = DataAccessLog.objects.filter(
            user=self.user,
            data_type='DASHBOARD'
        )
        self.assertTrue(logs.exists())
    
    def test_user_can_export_data(self):
        """Teste: Usuário pode exportar seus dados (portabilidade)"""
        # Login
        self.client.login(username='testuser', password='Test@123456')
        
        # Exportar dados
        response = self.client.get('/export-data/')
        
        # Verificar resposta JSON
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('usuario', data)
        self.assertEqual(data['usuario']['email'], 'test@imobcalc.com')
    
    def test_user_can_request_deletion(self):
        """Teste: Usuário pode solicitar exclusão (esquecimento)"""
        # Login
        self.client.login(username='testuser', password='Test@123456')
        
        # Solicitar exclusão
        response = self.client.post('/request-deletion/', {
            'reason': 'Não quero mais usar o serviço'
        })
        
        # Verificar solicitação
        deletion_request = DataDeletionRequest.objects.filter(
            user=self.user,
            status='PENDING'
        )
        self.assertTrue(deletion_request.exists())
    
    def test_sensitive_data_is_encrypted(self):
        """Teste: Dados sensíveis são criptografados"""
        # CPF original
        cpf_original = '123.456.789-00'
        
        # Criptografar
        cpf_encrypted = encrypt_cpf(cpf_original)
        
        # Verificar que está criptografado (não é igual ao original)
        self.assertNotEqual(cpf_encrypted, cpf_original)
        self.assertNotEqual(cpf_encrypted, '12345678900')
        
        # Descriptografar
        cpf_decrypted = decrypt_cpf(cpf_encrypted, formatted=True)
        
        # Verificar que volta ao original
        self.assertEqual(cpf_decrypted, cpf_original)
```

**Executar testes:**
```bash
cd D:\projetos\FI
python manage.py test simulacao.tests.test_lgpd -v 2
```

**Verificar:**
- ✅ Todos os 6 testes passam
- ✅ Cobertura de todos os direitos LGPD
- ✅ Sem erros ou warnings

---

## ⚠️ REGRAS IMPORTANTES

### ✅ SEMPRE FAÇA:
1. **Leia o código existente** antes de criar algo novo
2. **Teste cada mudança** imediatamente após implementar
3. **Mantenha o padrão de design** (gradient roxo #667eea to #764ba2)
4. **Use os imports corretos** dos arquivos existentes
5. **Salve todos os arquivos** em `D:\projetos\FI\`
6. **Documente** o que você fez ao final de cada item

### ❌ NUNCA FAÇA:
1. **Não sobrescreva** arquivos sem ler o conteúdo atual
2. **Não crie código** sem testar
3. **Não ignore erros** - sempre corrija antes de continuar
4. **Não mude** a estrutura de models sem criar migrations
5. **Não use** estilos diferentes do padrão estabelecido
6. **Não salve arquivos** fora da pasta do projeto

---

## 📚 ARQUIVOS PARA LER ANTES DE COMEÇAR

Leia estes arquivos para entender o padrão:

1. `D:\projetos\FI\simulacao\lgpd_models.py` - Entender os models LGPD
2. `D:\projetos\FI\simulacao\lgpd_views.py` - Ver padrão das views
3. `D:\projetos\FI\simulacao\templates\simulacao\lgpd\consent.html` - Ver padrão de design
4. `D:\projetos\FI\simulacao\encryption.py` - Entender criptografia
5. `D:\projetos\FI\TODO.md` - Ver lista completa de tarefas
6. `D:\projetos\FI\TUTORIAL.md` - Contexto geral do projeto

---

## 🧪 COMO TESTAR

### Iniciar servidor:
```bash
cd D:\projetos\FI
python manage.py runserver
```

### URLs para testar:
- http://127.0.0.1:8000/privacy/ (Item 2.5)
- http://127.0.0.1:8000/terms/ (Item 2.6)
- http://127.0.0.1:8000/audit-logs/ (Item 2.7)
- http://127.0.0.1:8000/admin/ (admin / admin123456)

### Verificar banco de dados:
```bash
cd D:\projetos\FI
python manage.py shell

from simulacao.lgpd_models import *
from django.contrib.auth import get_user_model

# Ver consentimentos
ConsentManagement.objects.all()

# Ver logs
DataAccessLog.objects.all()

# Ver solicitações de exclusão
DataDeletionRequest.objects.all()
```

### Executar testes:
```bash
cd D:\projetos\FI
python manage.py test simulacao.tests.test_lgpd -v 2
```

---

## 📝 FORMATO DE DOCUMENTAÇÃO

Ao completar cada item, documente assim no final do arquivo:

```markdown
---

## ✅ ITEM 2.X COMPLETO - [NOME DO ITEM]

**Data/Hora:** DD/MM/YYYY HH:MM

**Arquivos criados:**
- D:\projetos\FI\caminho\arquivo1.py
- D:\projetos\FI\caminho\arquivo2.html

**Arquivos modificados:**
- D:\projetos\FI\caminho\arquivo3.py (linhas X-Y: descrição da mudança)

**Testes realizados:**
- ✅ Teste 1: descrição do resultado
- ✅ Teste 2: descrição do resultado
- ✅ Teste 3: descrição do resultado

**URLs testadas:**
- ✅ http://127.0.0.1:8000/url1/ - Funcionando
- ✅ http://127.0.0.1:8000/url2/ - Funcionando

**Observações:**
- Nota importante 1
- Nota importante 2
- Problemas encontrados e como foram resolvidos

**Próximo item:** 2.X+1
```

---

## 🎯 OBJETIVO FINAL

Ao completar os 4 itens, a **FASE 2 estará 100% completa**! Isso significa:

✅ Sistema LGPD totalmente conforme  
✅ Política de Privacidade e Termos de Uso prontos  
✅ Logs de auditoria automáticos funcionando  
✅ Testes de conformidade passando  
✅ Projeto pronto para FASE 3 (Parcerias)  
✅ Progresso geral: 21% (17 de 80 itens)

---

## 💡 DICAS DE SUCESSO

1. **Trabalhe item por item** - Complete 2.5, teste, depois 2.6, teste, etc.
2. **Teste frequentemente** - Não acumule código sem testar
3. **Use o código existente** como referência de padrão
4. **Copie e adapte** - Não reinvente a roda
5. **Leia os erros** - Eles dizem exatamente o que está errado
6. **Documente tudo** - Facilita para próximas sessões
7. **Salve sempre em D:\projetos\FI\** - Mantenha tudo organizado

---

## 🚀 PODE COMEÇAR!

**Ordem de execução:**

1. **Primeiro:** Leia os arquivos de referência listados acima
2. **Segundo:** Comece pelo Item 2.5 (Política de Privacidade)
3. **Terceiro:** Teste a URL http://127.0.0.1:8000/privacy/
4. **Quarto:** Documente o que fez
5. **Quinto:** Passe para o Item 2.6
6. **Continue** até completar todos os 4 itens

**Boa sorte! 🎉**

Qualquer dúvida, pergunte. Estamos juntos nessa! 💪

---

## 📞 CONTATO

Se precisar de ajuda ou tiver dúvidas:
- Pergunte diretamente no chat
- Consulte o TUTORIAL.md
- Verifique o TODO.md para contexto

**Vamos fazer o ImobCalc ser o melhor simulador de imóveis do Brasil!** 🏠✨
