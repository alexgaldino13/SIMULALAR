# 🚀 PLANO DE LANÇAMENTO - ImobCalc

📅 **Data:** 01 de Fevereiro de 2026  
👤 **Desenvolvedor:** Galdino  
🎯 **Objetivo:** Preparar ImobCalc para lançamento Android/iOS  
📍 **Localização:** D:\PROJETOS\FI

---

## 📋 ÍNDICE

1. [Visão Geral](#visão-geral)
2. [Sistema de Login e Autenticação](#sistema-de-login-e-autenticação)
3. [Dados Sensíveis e Parcerias](#dados-sensíveis-e-parcerias)
4. [Modelo de Monetização](#modelo-de-monetização)
5. [Design e Interface](#design-e-interface)
6. [Testes Finais](#testes-finais)
7. [Roadmap de Implementação](#roadmap-de-implementação)

---

## 🎯 VISÃO GERAL

### Status Atual:
- ✅ Funcionalidades core: 95% completo
- ✅ Cálculos financeiros: 100% funcional
- ✅ Interface wizard: 100% funcional
- 🔄 Melhorias visuais: 5% pendente
- ⏳ Sistema de login: 0%
- ⏳ Monetização: 0%
- ⏳ Design mobile: Material disponível
- ⏳ Testes finais: 0%

### Próximas Fases:
1. **Fase 1:** Sistema de Login e Banco de Dados
2. **Fase 2:** Modelo de Monetização (Free vs Premium)
3. **Fase 3:** Design e Interface Mobile
4. **Fase 4:** Parcerias e Dados Sensíveis
5. **Fase 5:** Testes Finais e Ajustes
6. **Fase 6:** Encapsulamento Android/iOS

---

## 🔐 SISTEMA DE LOGIN E AUTENTICAÇÃO

### Objetivos:
- Permitir usuários salvarem simulações
- Histórico de simulações
- Perfil personalizado
- Sincronização entre dispositivos

### Tecnologias Sugeridas:

#### Opção 1: Django Authentication (Recomendado)
**Vantagens:**
- Já integrado ao Django
- Seguro e testado
- Fácil implementação
- Suporte a OAuth (Google, Facebook, Apple)

**Implementação:**
```python
# models.py
from django.contrib.auth.models import User
from django.db import models

class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefone = models.CharField(max_length=20, blank=True)
    data_nascimento = models.DateField(null=True, blank=True)
    plano = models.CharField(max_length=20, default='free')  # free, premium
    data_assinatura = models.DateTimeField(null=True, blank=True)
    
class SimulacaoSalva(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nome_simulacao = models.CharField(max_length=200)
    data_criacao = models.DateTimeField(auto_now_add=True)
    dados_simulacao = models.JSONField()  # Armazena todos os dados
    favorito = models.BooleanField(default=False)
```

#### Opção 2: Firebase Authentication
**Vantagens:**
- Integração fácil com mobile
- OAuth integrado
- Escalável
- Backend gerenciado

**Desvantagens:**
- Dependência de serviço externo
- Custos podem aumentar

### Funcionalidades do Sistema de Login:

1. **Cadastro/Login:**
   - Email + Senha
   - Google Sign-In
   - Apple Sign-In (obrigatório para iOS)
   - Facebook Login (opcional)

2. **Perfil do Usuário:**
   - Nome completo
   - Email
   - Telefone (opcional)
   - Foto de perfil
   - Plano (Free/Premium)

3. **Gerenciamento de Simulações:**
   - Salvar simulações
   - Nomear simulações
   - Favoritar simulações
   - Compartilhar simulações
   - Exportar para PDF (Premium)
   - Histórico completo

### Estimativa de Tempo:
- **Backend (Django):** 2-3 dias
- **Frontend (Web):** 1-2 dias
- **Integração OAuth:** 1 dia
- **Testes:** 1 dia
- **Total:** 5-7 dias

---

## 🔒 DADOS SENSÍVEIS E PARCERIAS

### Dados que Podemos Coletar:

#### ✅ Dados Não Sensíveis (Permitidos):
- Valor do imóvel desejado
- Entrada disponível
- Renda mensal
- Prazo desejado
- Tipo de financiamento preferido
- Região de interesse (cidade/estado)
- Faixa etária
- Situação de moradia atual

#### ⚠️ Dados Sensíveis (Requer Consentimento LGPD):
- Nome completo
- CPF
- Email
- Telefone
- Endereço completo
- Dados bancários
- Score de crédito

### Estratégia de Parcerias:

#### 1. **Parcerias com Consórcios:**

**Dados a Compartilhar:**
- Interesse em consórcio
- Valor da carta
- Prazo desejado
- Disponibilidade para lance
- Região de interesse

**Modelo de Negócio:**
- Comissão por lead qualificado: R$ 50-150
- Comissão por venda fechada: 1-3% do valor
- Parceria com: Embracon, Rodobens, Porto Seguro, Itaú

**Implementação:**
```python
class LeadConsorcio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    valor_carta = models.DecimalField(max_digits=12, decimal_places=2)
    prazo_desejado = models.IntegerField()
    valor_lance = models.DecimalField(max_digits=12, decimal_places=2)
    regiao = models.CharField(max_length=100)
    status = models.CharField(max_length=20)  # novo, enviado, contatado, convertido
    parceiro = models.CharField(max_length=100)
    data_envio = models.DateTimeField(auto_now_add=True)
    consentimento_lgpd = models.BooleanField(default=False)
```

#### 2. **Parcerias com Corretoras:**

**Dados a Compartilhar:**
- Valor do imóvel
- Região de interesse
- Tipo de imóvel (casa, apto, terreno)
- Entrada disponível
- Prazo para compra

**Modelo de Negócio:**
- Comissão por lead: R$ 30-100
- Comissão por venda: 0.5-1% do valor
- Parceria com: Lopes, Tecnisa, MRV, Cyrela

#### 3. **Parcerias com Bancos:**

**Dados a Compartilhar:**
- Valor do financiamento
- Entrada disponível
- Renda mensal
- Prazo desejado
- Sistema preferido (SAC/PRICE)

**Modelo de Negócio:**
- Comissão por simulação enviada: R$ 20-50
- Comissão por financiamento aprovado: 0.3-0.8% do valor
- Parceria com: Caixa, Itaú, Bradesco, Santander, Banco do Brasil

### Conformidade LGPD:

**Obrigatório:**
1. Termo de Consentimento claro
2. Política de Privacidade detalhada
3. Opção de opt-out
4. Direito ao esquecimento
5. Portabilidade de dados
6. Criptografia de dados sensíveis

**Template de Consentimento:**
```
"Autorizo o ImobCalc a compartilhar meus dados com parceiros 
(bancos, consórcios e corretoras) para receber ofertas personalizadas. 
Posso revogar este consentimento a qualquer momento."

[ ] Aceito receber contato de bancos
[ ] Aceito receber contato de consórcios
[ ] Aceito receber contato de corretoras
```

### Estimativa de Receita com Parcerias:

**Cenário Conservador (1000 usuários/mês):**
- 30% geram leads qualificados = 300 leads
- 300 leads × R$ 50 (média) = R$ 15.000/mês
- 5% convertem em vendas = 15 vendas
- 15 vendas × R$ 2.000 (comissão média) = R$ 30.000/mês
- **Total: R$ 45.000/mês**

**Cenário Otimista (5000 usuários/mês):**
- **Total: R$ 225.000/mês**

---

## 💰 MODELO DE MONETIZAÇÃO

### Versão FREE (Com Anúncios):

**Funcionalidades Incluídas:**
- ✅ Todas as simulações básicas
- ✅ Comparação de cenários
- ✅ Cálculos completos
- ✅ Salvar até 3 simulações
- ❌ Anúncios (banner + interstitial)
- ❌ Marca d'água nos resultados

**Anúncios:**
- Google AdMob
- Banner no topo/rodapé
- Interstitial a cada 3 simulações
- Rewarded ads para funcionalidades extras

**Estimativa de Receita (AdMob):**
- CPM médio Brasil: R$ 2-5
- 1000 usuários ativos/dia
- 5 impressões/usuário/dia
- 5000 impressões/dia × 30 dias = 150.000 impressões/mês
- 150 × R$ 3 (CPM médio) = R$ 450/mês

### Versão PREMIUM (Sem Anúncios):

**Preço Sugerido:**
- Mensal: R$ 9,90
- Anual: R$ 89,90 (25% desconto)
- Vitalício: R$ 199,90 (lançamento)

**Funcionalidades Exclusivas:**

1. **✅ Sem Anúncios**
   - Experiência limpa
   - Sem interrupções

2. **📊 Planilha Detalhada de Acompanhamento**
   - Exportar para Excel/Google Sheets
   - Acompanhamento mês a mês
   - Gráficos de evolução
   - Projeções personalizadas
   - Alertas de vencimento

3. **💾 Simulações Ilimitadas**
   - Salvar quantas quiser
   - Organizar em pastas
   - Tags personalizadas
   - Busca avançada

4. **📄 Exportação PDF Profissional**
   - Relatório completo
   - Sem marca d'água
   - Gráficos coloridos
   - Comparativos lado a lado
   - Logo personalizada (opcional)

5. **🔔 Notificações Inteligentes**
   - Alertas de taxa de juros
   - Oportunidades de amortização
   - Lembretes de FGTS
   - Dicas personalizadas

6. **📈 Análise Avançada**
   - Simulação de cenários "E se?"
   - Análise de sensibilidade
   - Comparação com mercado
   - Recomendações personalizadas

7. **🤝 Suporte Prioritário**
   - Chat direto
   - Resposta em até 24h
   - Consultoria básica

8. **🔄 Sincronização Multi-dispositivo**
   - Web + Mobile
   - Backup automático
   - Acesso offline

**Estimativa de Conversão:**
- 1000 usuários free/mês
- Taxa de conversão: 3-5%
- 30-50 assinantes premium/mês
- 40 × R$ 9,90 = R$ 396/mês (mensal)
- 10 × R$ 89,90 = R$ 899/mês (anual)
- **Total: R$ 1.295/mês**

### Resumo de Receitas Projetadas:

**Mês 1-3 (Lançamento):**
- AdMob: R$ 450
- Premium: R$ 1.295
- Parcerias: R$ 15.000
- **Total: R$ 16.745/mês**

**Mês 6-12 (Crescimento):**
- AdMob: R$ 2.250 (5x usuários)
- Premium: R$ 6.475 (5x conversões)
- Parcerias: R$ 75.000 (5x leads)
- **Total: R$ 83.725/mês**

**Ano 2 (Consolidação):**
- AdMob: R$ 4.500
- Premium: R$ 12.950
- Parcerias: R$ 150.000
- **Total: R$ 167.450/mês**

---

## 🎨 DESIGN E INTERFACE

### Material Disponível:
📁 **D:\PROJETOS\FI\Documentos auxiliares**

**Arquivos Identificados:**
1. Guia de identidade (v1-v6)
2. Logotipo com tipografia
3. Ícone simples para app
4. Logo minimalista
5. Splash screen
6. Telas de onboarding
7. Tela da versão premium (2 versões)

### Tarefas de Design:

#### 1. **Revisar Material Existente:**
- [ ] Analisar guias de identidade (v1-v6)
- [ ] Escolher versão final do logo
- [ ] Validar paleta de cores
- [ ] Verificar tipografia
- [ ] Revisar ícones

#### 2. **Adaptar para Mobile:**
- [ ] Redesenhar wizard para mobile
- [ ] Criar componentes responsivos
- [ ] Adaptar formulários para touch
- [ ] Otimizar para telas pequenas
- [ ] Criar versão tablet

#### 3. **Criar Telas Faltantes:**
- [ ] Tela de login/cadastro
- [ ] Tela de perfil
- [ ] Tela de simulações salvas
- [ ] Tela de configurações
- [ ] Tela de assinatura premium
- [ ] Tela de resultados mobile
- [ ] Tela de comparação

#### 4. **Prototipar:**
- [ ] Criar protótipo no Figma
- [ ] Testar fluxo de navegação
- [ ] Validar com usuários
- [ ] Ajustar baseado em feedback

### Ferramentas Recomendadas:
- **Design:** Figma (protótipos interativos)
- **Ícones:** Material Icons, Font Awesome
- **Ilustrações:** unDraw, Storyset
- **Cores:** Coolors.co (paletas)
- **Tipografia:** Google Fonts

### Estimativa de Tempo:
- Revisão de material: 1 dia
- Adaptação mobile: 3-4 dias
- Telas faltantes: 2-3 dias
- Prototipagem: 2 dias
- **Total: 8-10 dias**

---

## 🧪 TESTES FINAIS

### Tipos de Testes:

#### 1. **Testes Funcionais:**
- [ ] Todos os cálculos corretos
- [ ] Todos os cenários funcionando
- [ ] Formulários validando corretamente
- [ ] Salvamento de simulações
- [ ] Login/logout
- [ ] Recuperação de senha
- [ ] Exportação PDF
- [ ] Exportação Excel

#### 2. **Testes de Usabilidade:**
- [ ] Fluxo intuitivo
- [ ] Tempo para completar simulação
- [ ] Taxa de abandono
- [ ] Feedback de usuários
- [ ] Teste A/B de interfaces

#### 3. **Testes de Performance:**
- [ ] Tempo de carregamento < 3s
- [ ] Responsividade em diferentes dispositivos
- [ ] Consumo de memória
- [ ] Consumo de bateria (mobile)
- [ ] Funcionamento offline

#### 4. **Testes de Segurança:**
- [ ] Proteção contra SQL Injection
- [ ] Proteção contra XSS
- [ ] Criptografia de senhas
- [ ] HTTPS obrigatório
- [ ] Validação de tokens
- [ ] Rate limiting

#### 5. **Testes de Compatibilidade:**
- [ ] Chrome, Firefox, Safari, Edge
- [ ] Android 8+
- [ ] iOS 13+
- [ ] Tablets
- [ ] Diferentes resoluções

#### 6. **Testes de Monetização:**
- [ ] Anúncios carregando corretamente
- [ ] Pagamentos processando
- [ ] Assinaturas renovando
- [ ] Cancelamentos funcionando
- [ ] Reembolsos

### Ferramentas de Teste:
- **Funcional:** Selenium, Pytest
- **Performance:** Lighthouse, GTmetrix
- **Mobile:** BrowserStack, TestFlight
- **Segurança:** OWASP ZAP
- **Analytics:** Google Analytics, Mixpanel

### Estimativa de Tempo:
- Testes funcionais: 3 dias
- Testes de usabilidade: 2 dias
- Testes de performance: 1 dia
- Testes de segurança: 2 dias
- Testes de compatibilidade: 2 dias
- Correções: 3-5 dias
- **Total: 13-15 dias**

---

## 📅 ROADMAP DE IMPLEMENTAÇÃO

### FASE 1: Sistema de Login (Semana 1-2)
**Duração:** 5-7 dias

**Tarefas:**
- [ ] Implementar Django Authentication
- [ ] Criar models (PerfilUsuario, SimulacaoSalva)
- [ ] Criar views de login/cadastro
- [ ] Integrar OAuth (Google, Apple)
- [ ] Criar telas de perfil
- [ ] Implementar salvamento de simulações
- [ ] Testar fluxo completo

**Entregável:** Sistema de login funcional

---

### FASE 2: Monetização (Semana 2-3)
**Duração:** 5-7 dias

**Tarefas:**
- [ ] Integrar Google AdMob
- [ ] Configurar anúncios (banner, interstitial)
- [ ] Implementar sistema de assinaturas
- [ ] Integrar gateway de pagamento (Stripe/PagSeguro)
- [ ] Criar tela de upgrade premium
- [ ] Implementar controle de features por plano
- [ ] Testar fluxo de pagamento

**Entregável:** Sistema de monetização funcional

---

### FASE 3: Features Premium (Semana 3-4)
**Duração:** 5-7 dias

**Tarefas:**
- [ ] Implementar exportação PDF
- [ ] Criar planilha de acompanhamento (Excel)
- [ ] Desenvolver sistema de notificações
- [ ] Implementar análise avançada
- [ ] Criar dashboard premium
- [ ] Testar todas as features

**Entregável:** Features premium completas

---

### FASE 4: Design Mobile (Semana 4-6)
**Duração:** 8-10 dias

**Tarefas:**
- [ ] Revisar material de design
- [ ] Criar protótipo Figma
- [ ] Adaptar interface para mobile
- [ ] Implementar design responsivo
- [ ] Criar componentes reutilizáveis
- [ ] Testar em diferentes dispositivos

**Entregável:** Interface mobile completa

---

### FASE 5: Parcerias e LGPD (Semana 6-7)
**Duração:** 5-7 dias

**Tarefas:**
- [ ] Criar sistema de leads
- [ ] Implementar consentimento LGPD
- [ ] Desenvolver API para parceiros
- [ ] Criar política de privacidade
- [ ] Implementar termos de uso
- [ ] Configurar criptografia de dados
- [ ] Testar conformidade

**Entregável:** Sistema de parcerias e conformidade LGPD

---

### FASE 6: Testes Finais (Semana 7-9)
**Duração:** 13-15 dias

**Tarefas:**
- [ ] Testes funcionais completos
- [ ] Testes de usabilidade
- [ ] Testes de performance
- [ ] Testes de segurança
- [ ] Testes de compatibilidade
- [ ] Correção de bugs
- [ ] Otimizações

**Entregável:** App testado e otimizado

---

### FASE 7: Encapsulamento (Semana 9-11)
**Duração:** 10-14 dias

**Tarefas:**
- [ ] Configurar React Native / Flutter
- [ ] Adaptar código para mobile
- [ ] Configurar build Android
- [ ] Configurar build iOS
- [ ] Testar em dispositivos reais
- [ ] Preparar assets (ícones, splash)
- [ ] Configurar deep links
- [ ] Preparar para stores

**Entregável:** Apps Android e iOS prontos

---

### FASE 8: Lançamento (Semana 11-12)
**Duração:** 5-7 dias

**Tarefas:**
- [ ] Criar conta Google Play Console
- [ ] Criar conta Apple Developer
- [ ] Preparar screenshots e descrições
- [ ] Submeter para review
- [ ] Configurar analytics
- [ ] Preparar landing page
- [ ] Estratégia de marketing
- [ ] Lançamento soft (beta)
- [ ] Lançamento oficial

**Entregável:** App publicado nas stores

---

## 📊 RESUMO EXECUTIVO

### Tempo Total Estimado:
**11-12 semanas (2.5-3 meses)**

### Investimento Necessário:
- Conta Apple Developer: $99/ano
- Conta Google Play: $25 (único)
- Servidor/Hospedagem: R$ 100-300/mês
- Gateway de pagamento: 3-5% por transação
- Marketing inicial: R$ 2.000-5.000
- **Total inicial: ~R$ 3.000-6.000**

### Receita Projetada (Ano 1):
- Mês 1-3: R$ 16.745/mês
- Mês 4-6: R$ 50.000/mês
- Mês 7-12: R$ 83.725/mês
- **Total Ano 1: ~R$ 650.000**

### ROI Esperado:
- Investimento: R$ 6.000
- Receita Ano 1: R$ 650.000
- **ROI: 10.733%**

---

## 🎯 PRÓXIMOS PASSOS IMEDIATOS

### Esta Semana:
1. [ ] Revisar material de design
2. [ ] Decidir stack mobile (React Native vs Flutter)
3. [ ] Começar implementação de login
4. [ ] Criar protótipo Figma

### Próxima Semana:
1. [ ] Finalizar sistema de login
2. [ ] Começar integração AdMob
3. [ ] Iniciar sistema de assinaturas

---

**🚀 Vamos transformar o ImobCalc no melhor app de simulação imobiliária do Brasil!**
