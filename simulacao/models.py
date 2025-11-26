# simulacao/models.py
from django.db import models

# ======================================================================
# 1. MODELOS DE USUÁRIO E SIMULAÇÃO (Versão Simples) - MANTIDOS
# ======================================================================

class Usuario(models.Model):
    """
    Representa o usuário do aplicativo (usado atualmente na view de teste).
    """
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome


class Simulacao(models.Model):
    """
    Armazena os parâmetros e resultados principais de uma simulação (Estrutura Antiga).
    """
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    valor_imovel = models.DecimalField(max_digits=15, decimal_places=2)
    entrada = models.DecimalField(max_digits=15, decimal_places=2)
    taxa_anual = models.DecimalField(max_digits=5, decimal_places=2)
    prazo_meses = models.IntegerField()
    parcela_fixa = models.DecimalField(max_digits=15, decimal_places=2)
    total_juros = models.DecimalField(max_digits=15, decimal_places=2)
    data_simulacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Simulação de {self.valor_imovel} por {self.usuario.nome}"


# ======================================================================
# 2. NOVOS CAMPOS PARA DESPESAS DE TRANSAÇÃO - ADICIONADOS À SIMULAÇÃO
# ======================================================================

class Financiamento(models.Model):
    """
    Modelo para armazenar dados de financiamento com suporte a despesas.
    """
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Dados do imóvel
    valor_imovel = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Valor do Imóvel")
    entrada = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Entrada (Recursos Próprios + FGTS)")
    
    # Dados do financiamento
    taxa_juros_anual = models.DecimalField(max_digits=5, decimal_places=3, verbose_name="Taxa de Juros Anual (%)")
    prazo_meses = models.IntegerField(verbose_name="Prazo Total em Meses")
    
    # NOVOS CAMPOS PARA DESPESAS DE TRANSAÇÃO
    valor_despesas = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        verbose_name="Total de Despesas de Transação (ITBI, Cartório, Avaliação, etc.)"
    )
    
    incorporar_despesas = models.BooleanField(
        default=True,
        verbose_name="Incorporar Despesas no Financiamento?"
    )
    
    data_criacao = models.DateTimeField(auto_now_add=True)

    @property
    def principal_financiado(self):
        """
        Calcula o Principal Financiado (Base de cálculo do SAC/PRICE).
        
        Fórmula:
        - Principal Base = Valor do Imóvel - Entrada
        - Se incorporar_despesas: Principal = Principal Base + Despesas
        - Senão: Principal = Principal Base
        """
        principal_base = self.valor_imovel - self.entrada
        
        if self.incorporar_despesas:
            return principal_base + self.valor_despesas
        else:
            return principal_base

    def __str__(self):
        return f"Financiamento de R$ {self.valor_imovel:,.2f} - Prazo {self.prazo_meses} meses"

    class Meta:
        verbose_name = "Financiamento"
        verbose_name_plural = "Financiamentos"


# ======================================================================
# 3. MODELOS PARA COMPARAÇÃO DE MÚltIPLOS CENÁRIOS (Versão Completa) - NOVO
# ======================================================================

class CenarioComparativo(models.Model):
    """
    Armazena o conjunto de dados iniciais para uma rodada de comparação 
    (Valor do imóvel, entrada, etc.), sendo o 'pai' de múltiplos resultados.
    """
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    
    valor_imovel = models.DecimalField(max_digits=15, decimal_places=2)
    entrada = models.DecimalField(max_digits=15, decimal_places=2)
    prazo_anos = models.IntegerField()
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cenário: R${self.valor_imovel} - {self.prazo_anos} anos"


class ResultadoComparacao(models.Model):
    """
    Armazena o resultado final de um método específico (Price, SAC, Consórcio, Renda)
    dentro de um CenarioComparativo.
    """
    METODO_CHOICES = [
        ('PRICE', 'Tabela Price'),
        ('SAC', 'Tabela SAC'),
        ('CONS', 'Consórcio'),
        ('RENDA', 'Aluguel + Investimento')
    ]
    
    cenario = models.ForeignKey(CenarioComparativo, on_delete=models.CASCADE)
    metodo = models.CharField(max_length=5, choices=METODO_CHOICES)
    
    # Resultados Chave para a Comparação
    parcela_inicial = models.DecimalField(max_digits=15, decimal_places=2)
    total_pago = models.DecimalField(max_digits=15, decimal_places=2)
    total_juros_ou_custo = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Detalhes adicionais (como a taxa, que varia por método)
    taxa_juros_anual = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return f"{self.get_metodo_display()} para o Cenário #{self.cenario.id}"
