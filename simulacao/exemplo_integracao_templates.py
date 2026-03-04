"""
Exemplo de Integração de Monetização em Templates Django

Este arquivo mostra como usar o sistema de monetização em templates reais.
Copie e adapte conforme sua arquitetura de templates.
"""

# ============================================================================
# 1. TEMPLATE BASE - base.html
# ============================================================================

TEMPLATE_BASE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}FI - Financiamento Imobiliário{% endblock %}</title>
    
    <!-- CSS -->
    <link rel="stylesheet" href="{% static 'css/style.css' %}">
    
    <!-- Google AdSense (para web) - opcional -->
    {% if not request.premium_manager.eh_premium %}
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-app-pub-xxxxxxxxxxxxxxxx"></script>
    {% endif %}
    
    {% block extra_head %}{% endblock %}
</head>
<body>
    
    <!-- HEADER COM STATUS PREMIUM -->
    <header class="site-header">
        <div class="container">
            <div class="header-top">
                <h1 class="logo">💰 FI - Financiamento Imobiliário</h1>
                
                <!-- Status Premium / Menu de Usuário -->
                <div class="header-right">
                    {% if request.user.is_authenticated %}
                        <div class="user-menu">
                            {% if request.premium_manager.eh_premium %}
                                <span class="badge badge-premium">
                                    ⭐ PREMIUM 
                                    (até {{ request.premium_manager.perfil.premium_expira|date:"d/m/Y" }})
                                </span>
                            {% else %}
                                <a href="{% url 'upgrade_premium' %}" class="btn btn-upgrade">
                                    ✨ Upgrade para Premium
                                </a>
                            {% endif %}
                            
                            <span class="user-name">{{ request.user.first_name|default:request.user.username }}</span>
                            <a href="{% url 'logout' %}" class="logout-link">Sair</a>
                        </div>
                    {% else %}
                        <a href="{% url 'login' %}" class="btn btn-primary">Entrar</a>
                        <a href="{% url 'signup' %}" class="btn btn-secondary">Criar Conta</a>
                    {% endif %}
                </div>
            </div>
        </div>
    </header>
    
    <!-- BANNER ANÚNCIO - TOPO (visível apenas para usuários grátis) -->
    {% if not request.premium_manager.eh_premium %}
    <div class="ad-banner-top">
        <ins class="adsbygoogle"
             style="display:block"
             data-ad-client="ca-app-pub-3940256099942544"
             data-ad-slot="6300978111"
             data-ad-format="horizontal"
             data-full-width-responsive="true"></ins>
        <script>
            (adsbygoogle = window.adsbygoogle || []).push({});
        </script>
    </div>
    {% endif %}
    
    <!-- CONTEÚDO PRINCIPAL -->
    <main class="site-main">
        <div class="container">
            {% if messages %}
                {% for message in messages %}
                <div class="alert alert-{{ message.tags }}">
                    {{ message }}
                </div>
                {% endfor %}
            {% endif %}
            
            {% block content %}{% endblock %}
        </div>
    </main>
    
    <!-- BANNER ANÚNCIO - RODAPÉ (visível apenas para usuários grátis) -->
    {% if not request.premium_manager.eh_premium %}
    <div class="ad-banner-bottom">
        <ins class="adsbygoogle"
             style="display:block"
             data-ad-client="ca-app-pub-3940256099942544"
             data-ad-slot="6300978111"
             data-ad-format="horizontal"
             data-full-width-responsive="true"></ins>
        <script>
            (adsbygoogle = window.adsbygoogle || []).push({});
        </script>
    </div>
    {% endif %}
    
    <!-- FOOTER -->
    <footer class="site-footer">
        <div class="container">
            <p>&copy; 2026 FI - Financiamento Imobiliário. Todos os direitos reservados.</p>
        </div>
    </footer>
    
    <!-- JavaScript -->
    <script src="{% static 'js/main.js' %}"></script>
    {% block extra_js %}{% endblock %}
    
</body>
</html>
"""


# ============================================================================
# 2. TEMPLATE DE SIMULAÇÃO - simulacao_form.html
# ============================================================================

TEMPLATE_SIMULACAO = """
{% extends "base.html" %}
{% load static %}

{% block title %}Simulador de Financiamento{% endblock %}

{% block content %}

<div class="simulacao-wrapper">
    
    <!-- Aviso se limite atingido (usuário grátis) -->
    {% if not request.premium_manager.pode_fazer_simulacao %}
    <div class="alert alert-warning alert-limite">
        <strong>⚠️ Limite Diário Atingido</strong>
        <p>Você realizou 5 simulações hoje. Limite para usuários grátis.</p>
        <a href="{% url 'upgrade_premium' %}" class="btn btn-warning">
            Upgrade para Premium (Ilimitado)
        </a>
    </div>
    {% endif %}
    
    <!-- Formulário de Simulação -->
    {% if request.premium_manager.pode_fazer_simulacao %}
    <div class="simulacao-form-container">
        <h1>Simulador de Financiamento Imobiliário</h1>
        
        <form method="post" action="{% url 'simular' %}">
            {% csrf_token %}
            
            <div class="form-group">
                <label for="valor_imovel">Valor do Imóvel (R$)</label>
                <input 
                    type="number" 
                    id="valor_imovel" 
                    name="valor_imovel" 
                    placeholder="300.000"
                    required>
            </div>
            
            <div class="form-group">
                <label for="taxa_anual">Taxa de Juros Anual (%)</label>
                <input 
                    type="number" 
                    id="taxa_anual" 
                    name="taxa_anual" 
                    placeholder="7.5"
                    step="0.1"
                    required>
            </div>
            
            <div class="form-group">
                <label for="prazo_meses">Prazo (meses)</label>
                <input 
                    type="number" 
                    id="prazo_meses" 
                    name="prazo_meses" 
                    placeholder="360"
                    required>
            </div>
            
            <button type="submit" class="btn btn-primary btn-large">
                🔢 Calcular Simulação
            </button>
        </form>
    </div>
    {% else %}
    <div class="bloqueado-content">
        <h2>Você atingiu seu limite de simulações</h2>
        <p>Usuários grátis podem fazer 5 simulações por dia.</p>
        <a href="{% url 'upgrade_premium' %}" class="btn btn-primary btn-large">
            ✨ Upgrade para Premium (Ilimitado)
        </a>
    </div>
    {% endif %}
    
</div>

{% endblock %}
"""


# ============================================================================
# 3. TEMPLATE DE RESULTADOS - resultado.html
# ============================================================================

TEMPLATE_RESULTADO = """
{% extends "base.html" %}
{% load static custom_filters %}

{% block title %}Resultado da Simulação{% endblock %}

{% block content %}

<div class="resultado-wrapper">
    
    <h1>Resultado da Simulação</h1>
    
    <!-- ALERTAS DE LIMITE -->
    <div class="limites-info">
        {% if not request.premium_manager.pode_exportar %}
        <div class="alert alert-info">
            <strong>📥 Exportação para Excel</strong><br>
            Você atingiu seu limite de 1 exportação por mês.
            <a href="{% url 'upgrade_premium' %}">Upgrade para Premium</a> para ilimitado.
        </div>
        {% endif %}
        
        {% if not request.premium_manager.pode_comparar %}
        <div class="alert alert-info">
            <strong>📊 Comparações</strong><br>
            Você atingiu seu limite de 2 comparações por dia.
            <a href="{% url 'upgrade_premium' %}">Upgrade para Premium</a> para ilimitado.
        </div>
        {% endif %}
    </div>
    
    <!-- ANÚNCIO INTERSTICIAL (entre título e conteúdo) -->
    {% if not request.premium_manager.eh_premium %}
    <div class="ad-intersticial">
        <ins class="adsbygoogle"
             style="display:block; text-align:center;"
             data-ad-layout="in-article"
             data-ad-format="fluid"
             data-ad-client="ca-app-pub-3940256099942544"
             data-ad-slot="8168151479"></ins>
        <script>
            (adsbygoogle = window.adsbygoogle || []).push({});
        </script>
    </div>
    {% endif %}
    
    <!-- RESUMO GERAL -->
    <div class="resultado-resumo">
        <div class="resumo-card">
            <h3>Parcela Mensal</h3>
            <p class="valor-grande">{{ dados.parcela_inicial|formatar_moeda_brl }}</p>
            <p class="percentual">
                {% widthratio dados.parcela_inicial renda_mensal 100 %}% da renda
            </p>
        </div>
        
        <div class="resumo-card">
            <h3>Total de Juros</h3>
            <p class="valor-grande">{{ dados.total_juros|formatar_moeda_brl }}</p>
            <p class="percentual">
                {{ dados.taxa_anual|formatar_percentual }} a.a.
            </p>
        </div>
        
        <div class="resumo-card">
            <h3>Total Pago</h3>
            <p class="valor-grande">{{ dados.total_pago|formatar_moeda_brl }}</p>
            <p class="percentual">
                {{ prazo_meses }} meses
            </p>
        </div>
    </div>
    
    <!-- TABELA DE AMORTIZAÇÃO (amostra) -->
    <div class="tabela-container">
        <h2>Primeiros 12 meses</h2>
        
        <table class="tabela-amortizacao">
            <thead>
                <tr>
                    <th>Mês</th>
                    <th>Saldo Devedor</th>
                    <th>Juros</th>
                    <th>Amortização</th>
                    <th>Parcela</th>
                </tr>
            </thead>
            <tbody>
                {% for mes in dados.tabela|slice:":12" %}
                <tr>
                    <td>{{ forloop.counter }}</td>
                    <td>{{ mes.saldo_devedor|formatar_moeda_brl }}</td>
                    <td>{{ mes.juros|formatar_moeda_brl }}</td>
                    <td>{{ mes.amortizacao|formatar_moeda_brl }}</td>
                    <td class="parcela-cell">{{ mes.parcela|formatar_moeda_brl }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        
        <p class="tabela-nota">
            * Mostrando primeiros 12 meses. 
            {% if request.premium_manager.pode_exportar %}
                <a href="{% url 'exportar' %}">Clique para exportar tabela completa em Excel</a>
            {% else %}
                <a href="{% url 'upgrade_premium' %}">Upgrade para Premium</a> para exportar tabela completa
            {% endif %}
        </p>
    </div>
    
    <!-- ANÚNCIO NO MEIO DO CONTEÚDO -->
    {% if not request.premium_manager.eh_premium %}
    <div class="ad-middle">
        <ins class="adsbygoogle"
             style="display:block"
             data-ad-client="ca-app-pub-3940256099942544"
             data-ad-slot="6300978111"
             data-ad-format="horizontal"
             data-full-width-responsive="true"></ins>
        <script>
            (adsbygoogle = window.adsbygoogle || []).push({});
        </script>
    </div>
    {% endif %}
    
    <!-- GRÁFICOS -->
    <div class="graficos-container">
        <h2>
            {% if request.premium_manager.pode_acessar_graficos_avancados %}
            📈 Gráficos Avançados
            {% else %}
            📊 Gráficos
            {% endif %}
        </h2>
        
        {% if request.premium_manager.pode_acessar_graficos_avancados %}
            <!-- Gráficos Premium -->
            <div class="grafico" id="grafico-saldo-devedor"></div>
            <div class="grafico" id="grafico-juros-acumulado"></div>
            
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <script>
                // Gráficos avançados para premium
                // ... código de gráfico ...
            </script>
        {% else %}
            <!-- Aviso para upgrade -->
            <div class="alert alert-info">
                <strong>🔒 Gráficos Avançados</strong>
                <p>Recursos como gráficos de evolução, análise comparativa e projeções estão disponíveis no plano Premium.</p>
                <a href="{% url 'upgrade_premium' %}" class="btn btn-primary">
                    Upgrade para Premium
                </a>
            </div>
        {% endif %}
    </div>
    
    <!-- BOTÕES DE AÇÃO -->
    <div class="botoes-acao">
        
        <!-- Botão Comparar (com verificação de limite) -->
        {% if request.premium_manager.pode_comparar %}
            <a href="{% url 'comparar' %}?dados={{ dados_encoded }}" class="btn btn-primary">
                📊 Comparar Cenários
            </a>
        {% else %}
            <button disabled class="btn btn-secondary" title="Limite diário atingido">
                📊 Comparar (Limite Atingido)
            </button>
            <small>Limite: 2/dia para grátis</small>
        {% endif %}
        
        <!-- Botão Exportar Excel (com verificação de limite) -->
        {% if request.premium_manager.pode_exportar %}
            <a href="{% url 'exportar' %}?dados={{ dados_encoded }}" class="btn btn-primary">
                📥 Exportar para Excel
            </a>
        {% else %}
            <button disabled class="btn btn-secondary" title="Limite mensal atingido">
                📥 Exportar (Limite Atingido)
            </button>
            <small>Limite: 1/mês para grátis</small>
            <a href="{% url 'upgrade_premium' %}" class="btn btn-warning">
                Upgrade para Premium (Ilimitado)
            </a>
        {% endif %}
        
        <!-- Botão Nova Simulação -->
        <a href="{% url 'simular' %}" class="btn btn-secondary">
            🔄 Nova Simulação
        </a>
    </div>
    
</div>

{% endblock %}
"""


# ============================================================================
# 4. TEMPLATE PREMIUM UPGRADE - upgrade_premium.html
# ============================================================================

TEMPLATE_UPGRADE = """
{% extends "base.html" %}
{% load static %}

{% block title %}Upgrade Premium{% endblock %}

{% block content %}

<div class="upgrade-wrapper">
    
    {% if request.premium_manager.eh_premium %}
    
        <!-- Caso: Usuário JÁ é Premium -->
        <div class="premium-ativo">
            <h1>✨ Você é Premium!</h1>
            
            <div class="premium-status">
                <p class="status-info">
                    <strong>Status:</strong> Ativo
                </p>
                <p class="status-info">
                    <strong>Plano:</strong> 
                    {% if "mensal" in request.premium_manager.perfil.produto_premium %}
                        Premium Mensal
                    {% else %}
                        Premium Anual
                    {% endif %}
                </p>
                <p class="status-info">
                    <strong>Válido até:</strong> 
                    {{ request.premium_manager.perfil.premium_expira|date:"d 'de' F 'de' Y" }}
                </p>
                <p class="status-info">
                    <strong>Dias restantes:</strong>
                    {{ request.premium_manager._calcular_dias_restantes }} dias
                </p>
            </div>
            
            <div class="beneficios-premium">
                <h2>Seus Benefícios</h2>
                <ul>
                    <li>✓ Sem anúncios</li>
                    <li>✓ Simulações ilimitadas</li>
                    <li>✓ Exportação Excel ilimitada</li>
                    <li>✓ Gráficos avançados</li>
                    <li>✓ Comparações ilimitadas</li>
                    {% if "anual" in request.premium_manager.perfil.produto_premium %}
                    <li>✓ Suporte prioritário</li>
                    {% endif %}
                </ul>
            </div>
            
            <a href="{% url 'inicio' %}" class="btn btn-primary btn-large">
                ← Voltar ao Simulador
            </a>
        </div>
    
    {% else %}
    
        <!-- Caso: Usuário é GRÁTIS -->
        <div class="premium-opcoes">
            
            <h1>✨ Upgrade para Premium</h1>
            <p class="intro-texto">
                Desbloqueie recursos ilimitados e remova anúncios por um preço muito acessível!
            </p>
            
            <!-- Comparação de Planos -->
            <div class="planos-comparacao">
                
                <table class="tabela-comparacao">
                    <thead>
                        <tr>
                            <th>Recurso</th>
                            <th>Grátis</th>
                            <th>Premium</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Simulações/dia</td>
                            <td>5</td>
                            <td>Ilimitado ✓</td>
                        </tr>
                        <tr>
                            <td>Comparações/dia</td>
                            <td>2</td>
                            <td>Ilimitado ✓</td>
                        </tr>
                        <tr>
                            <td>Exportação Excel/mês</td>
                            <td>1</td>
                            <td>Ilimitado ✓</td>
                        </tr>
                        <tr>
                            <td>Anúncios</td>
                            <td>Sim</td>
                            <td>Nenhum ✓</td>
                        </tr>
                        <tr>
                            <td>Gráficos Avançados</td>
                            <td>-</td>
                            <td>Sim ✓</td>
                        </tr>
                        <tr>
                            <td>Múltiplos Cenários</td>
                            <td>2</td>
                            <td>Ilimitado ✓</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            
            <!-- Seleção de Plano -->
            <div class="planos-selecao">
                
                <!-- Plano Mensal -->
                <div class="plano-card">
                    <div class="plano-header">
                        <h2>📅 Premium Mensal</h2>
                    </div>
                    <div class="plano-preco">
                        <span class="valor-grande">R$ 9,90</span>
                        <span class="periodo">/mês</span>
                    </div>
                    <ul class="plano-beneficios">
                        <li>✓ Sem anúncios</li>
                        <li>✓ Simulações ilimitadas</li>
                        <li>✓ Exportação ilimitada</li>
                        <li>✓ Gráficos avançados</li>
                        <li>✓ Comparações ilimitadas</li>
                        <li>✓ Cancela quando quiser</li>
                    </ul>
                    <button 
                        class="btn btn-primary btn-comprar" 
                        onclick="comprarPlano('com.ficalc.premium.mensal')">
                        Comprar Agora
                    </button>
                </div>
                
                <!-- Plano Anual (Destaque) -->
                <div class="plano-card plano-destaque">
                    <div class="plano-badge">
                        <span class="badge-texto">MELHOR VALOR</span>
                        <span class="badge-desconto">58% OFF</span>
                    </div>
                    <div class="plano-header">
                        <h2>🎯 Premium Anual</h2>
                    </div>
                    <div class="plano-preco">
                        <span class="valor-grande">R$ 49,90</span>
                        <span class="periodo">/ano</span>
                        <p class="economia">
                            Economize R$ 69,90 em relação ao plano mensal
                        </p>
                    </div>
                    <ul class="plano-beneficios">
                        <li>✓ Sem anúncios</li>
                        <li>✓ Simulações ilimitadas</li>
                        <li>✓ Exportação ilimitada</li>
                        <li>✓ Gráficos avançados</li>
                        <li>✓ Comparações ilimitadas</li>
                        <li>✓ Suporte prioritário</li>
                    </ul>
                    <button 
                        class="btn btn-primary btn-comprar btn-destaque" 
                        onclick="comprarPlano('com.ficalc.premium.anual')">
                        Comprar Agora
                    </button>
                </div>
            </div>
            
            <!-- FAQ -->
            <div class="faq-section">
                <h2>Perguntas Frequentes</h2>
                
                <div class="faq-item">
                    <h3>❓ Como funciona o cancelamento?</h3>
                    <p>
                        Você pode cancelar sua assinatura a qualquer momento pelas configurações da sua conta.
                        Não há multa ou taxa adicional.
                    </p>
                </div>
                
                <div class="faq-item">
                    <h3>❓ Qual é a diferença entre Mensal e Anual?</h3>
                    <p>
                        Os dois planos têm os mesmos recursos. A diferença é na duração e preço:
                        Mensal (R$ 9,90/mês) renova a cada mês, Anual (R$ 49,90) renova a cada ano.
                    </p>
                </div>
                
                <div class="faq-item">
                    <h3>❓ Há período de teste gratuito?</h3>
                    <p>
                        Não, mas a versão grátis já oferece 5 simulações diárias. Você pode testar!
                    </p>
                </div>
                
                <div class="faq-item">
                    <h3>❓ Qual forma de pagamento?</h3>
                    <p>
                        Google Play (Android) ou App Store (iOS) aceitam cartão de crédito, débito e saldo da loja.
                    </p>
                </div>
            </div>
        </div>
    
    {% endif %}
    
</div>

<script>
function comprarPlano(produtoId) {
    // Para app nativa (React Native, Flutter, etc)
    if (window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.iniciarCompra) {
        window.webkit.messageHandlers.iniciarCompra.postMessage({
            'produto': produtoId
        });
    }
    // Para web com Google Play Billing Library
    else if (window.google && window.google.payments) {
        // Implementar fluxo de compra web
        alert('Redirecionando para página de pagamento...');
    }
    // Fallback
    else {
        alert('Compra em: ' + produtoId);
    }
}
</script>

<style>
.upgrade-wrapper {
    max-width: 1000px;
    margin: 40px auto;
    padding: 0 20px;
}

.planos-selecao {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin: 40px 0;
}

.plano-card {
    border: 2px solid #ddd;
    border-radius: 8px;
    padding: 30px;
    background: white;
    transition: all 0.3s ease;
}

.plano-card:hover {
    box-shadow: 0 8px 24px rgba(0,0,0,0.1);
}

.plano-destaque {
    border-color: #FFC000;
    background: linear-gradient(to bottom, #fffef0, white);
    transform: translateY(-5px);
}

.plano-badge {
    position: absolute;
    top: -15px;
    right: 20px;
}

.badge-texto {
    background: #FFC000;
    color: black;
    padding: 5px 15px;
    border-radius: 4px;
    font-weight: bold;
    font-size: 12px;
}

.tabela-comparacao {
    width: 100%;
    border-collapse: collapse;
    margin: 30px 0;
}

.tabela-comparacao th,
.tabela-comparacao td {
    padding: 15px;
    text-align: left;
    border-bottom: 1px solid #ddd;
}

.tabela-comparacao thead {
    background: #1F4E78;
    color: white;
}

@media (max-width: 768px) {
    .planos-selecao {
        grid-template-columns: 1fr;
    }
}
</style>

{% endblock %}
"""


# ============================================================================
# 5. TEMPLATE DE EXEMPLO - exemplo_integracao.html (DEBUG)
# ============================================================================

TEMPLATE_DEBUG = """
{# Template de debug para verificar status de monetização #}

<div style="background: #f5f5f5; padding: 20px; margin: 20px; border-radius: 8px;">
    
    <h3>DEBUG - Status de Monetização</h3>
    
    <table style="width: 100%; border-collapse: collapse;">
        <tr style="background: #ddd;">
            <td style="padding: 10px;"><strong>Usuário</strong></td>
            <td style="padding: 10px;">{{ request.user.username }}</td>
        </tr>
        <tr>
            <td style="padding: 10px;">É Premium?</td>
            <td style="padding: 10px;">
                {% if request.premium_manager.eh_premium %}
                    ✓ SIM
                {% else %}
                    ✗ NÃO
                {% endif %}
            </td>
        </tr>
        <tr>
            <td style="padding: 10px;">Plano</td>
            <td style="padding: 10px;">{{ request.premium_manager.perfil.plano|default:"gratis" }}</td>
        </tr>
        <tr>
            <td style="padding: 10px;">Pode Exportar?</td>
            <td style="padding: 10px;">
                {% if request.premium_manager.pode_exportar_excel %}
                    ✓ SIM
                {% else %}
                    ✗ NÃO (Limite Mensal Atingido)
                {% endif %}
            </td>
        </tr>
        <tr>
            <td style="padding: 10px;">Pode Simular?</td>
            <td style="padding: 10px;">
                {% if request.premium_manager.pode_fazer_simulacao %}
                    ✓ SIM
                {% else %}
                    ✗ NÃO (Limite Diário Atingido)
                {% endif %}
            </td>
        </tr>
        <tr>
            <td style="padding: 10px;">Pode Comparar?</td>
            <td style="padding: 10px;">
                {% if request.premium_manager.pode_comparar_cenarios %}
                    ✓ SIM
                {% else %}
                    ✗ NÃO (Limite Diário Atingido)
                {% endif %}
            </td>
        </tr>
        <tr>
            <td style="padding: 10px;">Acesso a Gráficos Avançados?</td>
            <td style="padding: 10px;">
                {% if request.premium_manager.pode_acessar_graficos_avancados %}
                    ✓ SIM
                {% else %}
                    ✗ NÃO (Apenas Premium)
                {% endif %}
            </td>
        </tr>
        <tr>
            <td style="padding: 10px;">Ver Anúncios?</td>
            <td style="padding: 10px;">
                {% if request.ad_manager.eh_premium %}
                    ✗ NÃO (Premium não vê)
                {% else %}
                    ✓ SIM
                {% endif %}
            </td>
        </tr>
    </table>
    
</div>
"""


if __name__ == '__main__':
    print("✓ Exemplos de templates carregados!")
    print("\nTemplates inclusos:")
    print("1. TEMPLATE_BASE - header, footer, anúncios globais")
    print("2. TEMPLATE_SIMULACAO - formulário com validação de limite")
    print("3. TEMPLATE_RESULTADO - resultado com anúncios e botões de limite")
    print("4. TEMPLATE_UPGRADE - página de upgrade premium")
    print("5. TEMPLATE_DEBUG - debug de status (use em desenvolvimento)")
    print("\nCopie o código HTML para seus arquivos .html em simulacao/templates/")
