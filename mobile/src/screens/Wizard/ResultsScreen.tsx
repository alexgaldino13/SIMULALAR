import React, { useState } from 'react';
import {
  StyleSheet, Text, View, ScrollView, TouchableOpacity, SafeAreaView,
  Alert, ActivityIndicator, Linking,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { useSimulation } from '../../context/SimulationContext';
import { authService } from '../../api/authService';
import { BASE_URL } from '../../api/config';
import SimulationCharts from '../../components/SimulationCharts';
import { TextInputMask } from 'react-native-masked-text';
import apiClient from '../../api/client';

// Ícones por tipo de cenário
const SCENARIO_ICONS: Record<string, string> = {
  price:              'business-outline',
  sac:                'trending-down-outline',
  mcmv:               'home-outline',
  consorcio:          'people-outline',
  aluguel_investimento: 'stats-chart-outline',
  guardar_dinheiro:   'wallet-outline',
  banco_cef:          'card-outline',
  banco_bb:           'card-outline',
  banco_bradesco:     'card-outline',
  banco_itau:         'card-outline',
  banco_santander:    'card-outline',
};

// Explicações em linguagem simples por cenário
const SCENARIO_MEANING: Record<string, string> = {
  price:   'Você paga a mesma parcela todo mês do começo ao fim. Fácil de planejar.',
  sac:     'Sua parcela começa maior mas cai a cada mês. No total, você paga menos.',
  mcmv:    'Taxa subsidiada pelo governo. Se você se qualifica, é o financiamento mais barato.',
  consorcio: 'Sem juros, sem banco. Mas você pode esperar de 1 a 10 anos para ser contemplado.',
  aluguel_investimento: 'Você continua alugando e investe a diferença. Funciona se o retorno do investimento superar o custo do aluguel.',
  guardar_dinheiro: 'Você poupa até ter o valor total. Economiza todos os juros, mas demora mais.',
  banco_cef:       'Caixa Econômica Federal — banco do governo, taxa de referência SBPE.',
  banco_bb:        'Banco do Brasil — uma das menores taxas entre os bancos privados.',
  banco_bradesco:  'Bradesco — taxa um pouco acima da CEF, porém com bom atendimento.',
  banco_itau:      'Itaú — taxas competitivas, especialmente para clientes do banco.',
  banco_santander: 'Santander — taxa levemente acima da média, mas com condições flexíveis.',
};

export default function ResultsScreen({ route, navigation }: any) {
  const { results } = route?.params || { results: null };
  const { data: wizardData, leadCaptured, leadInfo, setLeadCaptured } = useSimulation();
  const [saving, setSaving] = React.useState(false);
  const [unlocked, setUnlocked] = React.useState(leadCaptured);
  const [leadLoading, setLeadLoading] = React.useState(false);
  const [leadForm, setLeadForm] = React.useState(leadInfo || { nome: '', whatsapp: '' });
  const [expandedCard, setExpandedCard] = useState<string | null>(null);

  if (!results) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>Nenhum dado de simulação encontrado.</Text>
        <TouchableOpacity onPress={() => navigation.navigate('Step1')} style={styles.retryButton}>
          <Text style={styles.retryButtonText}>Voltar ao Início</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const handleLeadSubmit = async () => {
    if (!leadForm.nome || !leadForm.whatsapp) {
      Alert.alert('Dados Necessários', 'Por favor, preencha seu nome e WhatsApp para ver o relatório completo.');
      return;
    }
    setLeadLoading(true);
    try {
      await apiClient.post('/api/v1/capturar-lead/', {
        ...leadForm,
        origem: 'MOBILE',
        valor_imovel: results.valor_imovel,
        perfil: wizardData.perfil_objetivos.perfil_usuario,
      });
      setLeadCaptured(true, leadForm);
      setUnlocked(true);
    } catch {
      Alert.alert('Erro', 'Ocorreu um problema. Tente novamente.');
    } finally {
      setLeadLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const payload = {
        titulo: `Simulação ${results.valor_imovel_fmt || ''}`,
        dados_wizard: wizardData,
        resultados: results,
      };
      await authService.saveSimulation(payload);
      Alert.alert('Sucesso 🎉', 'Simulação salva no seu histórico!', [
        { text: 'Ir para Dashboard', onPress: () => navigation.navigate('Dashboard') },
        { text: 'Ok', style: 'cancel' },
      ]);
    } catch {
      Alert.alert('Ops!', 'Não conseguimos salvar sua simulação agora.');
    } finally {
      setSaving(false);
    }
  };

  const ResultCard = ({ cardKey, value }: any) => {
    const isRecommendation = results.analise?.melhor_cenario === cardKey;
    const isExpanded = expandedCard === cardKey;
    const icon = SCENARIO_ICONS[cardKey] || 'business-outline';
    const meaning = SCENARIO_MEANING[cardKey];

    return (
      <TouchableOpacity
        style={[styles.card, isRecommendation ? styles.cardHighlighted : {}]}
        onPress={() => setExpandedCard(isExpanded ? null : cardKey)}
        activeOpacity={0.85}
      >
        {isRecommendation && (
          <View style={styles.bestBadge}>
            <Text style={styles.bestBadgeText}>✓ RECOMENDADO</Text>
          </View>
        )}
        <View style={styles.cardHeader}>
          <View style={styles.cardTitleRow}>
            <Ionicons name={icon as any} size={20} color="#6a11cb" style={{ marginRight: 8 }} />
            <Text style={styles.cardTitle}>{value.metodo}</Text>
          </View>
          <Ionicons name={isExpanded ? 'chevron-up' : 'chevron-down'} size={18} color="#666" />
        </View>

        {/* Linha resumo sempre visível */}
        <View style={styles.summaryRow}>
          <View style={styles.summaryItem}>
            <Text style={styles.summaryLabel}>Parcela inicial</Text>
            <Text style={styles.summaryValue}>{value.parcela_inicial || 'N/A'}</Text>
          </View>
          <View style={styles.summaryDivider} />
          <View style={styles.summaryItem}>
            <Text style={styles.summaryLabel}>Custo total</Text>
            <Text style={[styles.summaryValue, { color: '#ef4444' }]}>{value.total_custo || 'N/A'}</Text>
          </View>
        </View>

        {/* Detalhes expandidos */}
        {isExpanded && (
          <>
            <View style={styles.divider} />
            {!!value.taxa_aa && <DetailRow label="Taxa de juros" value={value.taxa_aa} />}
            {!!value.cet_anual && value.cet_anual !== '0,00%' && (
              <DetailRow label="CET anual" value={value.cet_anual} color="#10b981" />
            )}
            {!!value.prazo_anos && (
              <DetailRow label="Prazo" value={`${value.prazo_anos} anos`} />
            )}
            {!!value.comprometimento_renda && value.comprometimento_renda > 0 && (
              <DetailRow
                label="% da renda comprometida"
                value={`${value.comprometimento_renda}%`}
                color={value.comprometimento_renda > 30 ? '#f59e0b' : '#10b981'}
              />
            )}
            {!!value.total_juros && value.total_juros !== 'N/A' && (
              <DetailRow label="Total de juros" value={value.total_juros} color="#f59e0b" />
            )}
            {!!value.contemplacao_estimada && (
              <DetailRow label="Contemplação estimada" value={value.contemplacao_estimada} />
            )}
            {!!value.saldo_final && (
              <DetailRow label="Patrimônio no final" value={value.saldo_final} color="#10b981" />
            )}
            {!!meaning && (
              <View style={styles.meaningBox}>
                <Text style={styles.meaningLabel}>💡 O que isso significa?</Text>
                <Text style={styles.meaningText}>{meaning}</Text>
              </View>
            )}
          </>
        )}
        {!isExpanded && (
          <Text style={styles.tapHint}>Toque para ver detalhes</Text>
        )}
      </TouchableOpacity>
    );
  };

  const DetailRow = ({ label, value, color }: any) => (
    <View style={styles.detailRow}>
      <Text style={styles.detailLabel}>{label}</Text>
      <Text style={[styles.detailValue, color ? { color } : {}]}>{value}</Text>
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <LinearGradient colors={['#0f0c29', '#302b63', '#24243e']} style={StyleSheet.absoluteFill} />

      {!unlocked ? (
        <View style={styles.leadGate}>
          <View style={styles.leadCard}>
            <Text style={styles.leadEmoji}>🚀</Text>
            <Text style={styles.leadTitle}>Sua simulação está pronta!</Text>
            <Text style={styles.leadSubtitle}>
              Informe seus dados para receber o relatório completo e nossa recomendação personalizada.
            </Text>
            <View style={styles.linksRow}>
              <TouchableOpacity onPress={() => Linking.openURL(`${BASE_URL}/privacy/`)}>
                <Text style={styles.linkText}>Privacidade</Text>
              </TouchableOpacity>
              <Text style={styles.linkDivider}>|</Text>
              <TouchableOpacity onPress={() => Linking.openURL(`${BASE_URL}/terms/`)}>
                <Text style={styles.linkText}>Termos</Text>
              </TouchableOpacity>
            </View>

            <View style={styles.mobileInputContainer}>
              <TextInputMask
                type={'custom'}
                options={{ mask: '********************************' }}
                style={styles.mobileInput}
                placeholder="Seu Nome"
                placeholderTextColor="#555"
                value={leadForm.nome}
                onChangeText={(v) => setLeadForm({ ...leadForm, nome: v })}
              />
            </View>
            <View style={styles.mobileInputContainer}>
              <TextInputMask
                type={'cel-phone'}
                options={{ maskType: 'BRL', withDDD: true, dddMask: '(99) ' }}
                style={styles.mobileInput}
                placeholder="WhatsApp (opcional)"
                placeholderTextColor="#555"
                value={leadForm.whatsapp}
                onChangeText={(v) => setLeadForm({ ...leadForm, whatsapp: v })}
              />
            </View>

            <TouchableOpacity style={styles.unlockButton} onPress={handleLeadSubmit} disabled={leadLoading}>
              {leadLoading ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <Text style={styles.unlockButtonText}>Ver Resultados Gratuitos →</Text>
              )}
            </TouchableOpacity>
          </View>
        </View>
      ) : (
        <ScrollView contentContainerStyle={styles.scrollContent}>
          {/* Banner de recomendação */}
          <View style={styles.recommendationBanner}>
            <Text style={styles.bannerLabel}>RECOMENDAÇÃO SIMULALAR</Text>
            <Text style={styles.recommendationText}>
              {results.analise?.texto_principal || 'Análise indisponível'}
            </Text>
          </View>

          {/* Dados do imóvel */}
          {results.valor_imovel_fmt && (
            <View style={styles.summaryBanner}>
              <View style={styles.summaryBannerItem}>
                <Text style={styles.summaryBannerLabel}>Imóvel</Text>
                <Text style={styles.summaryBannerValue}>{results.valor_imovel_fmt}</Text>
              </View>
              {results.entrada_efetiva > 0 && (
                <View style={styles.summaryBannerItem}>
                  <Text style={styles.summaryBannerLabel}>Entrada</Text>
                  <Text style={styles.summaryBannerValue}>
                    {results.valor_imovel_fmt ? `${results.entrada_pct?.toFixed(0)}%` : 'N/A'}
                  </Text>
                </View>
              )}
              {results.renda_minima_recomendada > 0 && (
                <View style={styles.summaryBannerItem}>
                  <Text style={styles.summaryBannerLabel}>Renda mín.</Text>
                  <Text style={[styles.summaryBannerValue, { fontSize: 13 }]}>
                    {results.custas_iniciais?.total_fmt || '–'}
                  </Text>
                </View>
              )}
            </View>
          )}

          {/* Alertas */}
          {results.analise?.alertas?.length > 0 && (
            <View style={styles.alertsContainer}>
              {results.analise.alertas.map((alerta: string, i: number) => (
                <View key={i} style={styles.alertRow}>
                  <Ionicons name="warning-outline" size={16} color="#f59e0b" style={{ marginRight: 8, marginTop: 2 }} />
                  <Text style={styles.alertText}>{alerta}</Text>
                </View>
              ))}
            </View>
          )}

          {/* Gráfico */}
          <SimulationCharts results={results} />

          {/* Cards de resultado */}
          {results.resultados &&
            Object.entries(results.resultados).map(([key, value]: any) => (
              <ResultCard key={key} cardKey={key} value={value} />
            ))}

          {/* MCMV se não elegível */}
          {results.mcmv && !results.mcmv.elegivel && (
            <View style={styles.mcmvInfo}>
              <Ionicons name="information-circle-outline" size={16} color="#6a11cb" style={{ marginRight: 6 }} />
              <Text style={styles.mcmvInfoText}>
                <Text style={{ fontWeight: 'bold' }}>MCMV: </Text>
                {results.mcmv.motivo}
              </Text>
            </View>
          )}

          {/* Custas */}
          {results.custas_iniciais && (
            <View style={styles.custasBox}>
              <Text style={styles.custasTitle}>📋 Custas de Aquisição</Text>
              <DetailRow label="ITBI" value={results.custas_iniciais.itbi_fmt} />
              <DetailRow label="Cartório/Registro" value={results.custas_iniciais.cartorio_fmt} />
              <DetailRow label="Escritura" value={results.custas_iniciais.escritura_fmt} />
              <DetailRow label="Avaliação bancária" value="R$ 1.000,00" />
              <View style={styles.divider} />
              <DetailRow label="Total de custas" value={results.custas_iniciais.total_fmt} color="#f59e0b" />
            </View>
          )}

          {/* Botões de ação */}
          <TouchableOpacity
            style={[styles.saveButton, saving ? { opacity: 0.7 } : {}]}
            onPress={handleSave}
            disabled={saving}
          >
            <LinearGradient
              colors={['#6a11cb', '#2575fc']}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 0 }}
              style={styles.saveGradient}
            >
              {saving ? (
                <ActivityIndicator size="small" color="#fff" />
              ) : (
                <>
                  <Ionicons name="cloud-upload-outline" size={20} color="#fff" style={{ marginRight: 8 }} />
                  <Text style={styles.saveButtonText}>Salvar no Histórico</Text>
                </>
              )}
            </LinearGradient>
          </TouchableOpacity>

          <TouchableOpacity style={styles.redoButton} onPress={() => navigation.navigate('Step1')}>
            <Text style={styles.redoButtonText}>Fazer Nova Simulação</Text>
          </TouchableOpacity>
        </ScrollView>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0f0c29' },
  errorContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 20 },
  errorText: { color: '#fff', marginBottom: 20 },
  retryButton: { backgroundColor: '#6a11cb', padding: 15, borderRadius: 10 },
  retryButtonText: { color: '#fff', fontWeight: 'bold' },
  scrollContent: { padding: 20, paddingBottom: 60 },

  /* Lead gate */
  leadGate: { flex: 1, justifyContent: 'center', padding: 20 },
  leadCard: { backgroundColor: '#1e1b4b', padding: 28, borderRadius: 30, alignItems: 'center' },
  leadEmoji: { fontSize: 40, marginBottom: 10 },
  leadTitle: { color: '#fff', fontSize: 22, fontWeight: 'bold', textAlign: 'center', marginBottom: 8 },
  leadSubtitle: { color: 'rgba(255,255,255,0.55)', fontSize: 14, textAlign: 'center', marginBottom: 20, lineHeight: 20 },
  linksRow: { flexDirection: 'row', marginBottom: 20 },
  linkText: { color: '#7f7fd5', textDecorationLine: 'underline', fontSize: 12 },
  linkDivider: { color: '#444', marginHorizontal: 10 },
  mobileInputContainer: { width: '100%', backgroundColor: 'rgba(255,255,255,0.1)', borderRadius: 15, marginBottom: 10, padding: 15 },
  mobileInput: { color: '#fff', fontSize: 16 },
  unlockButton: { width: '100%', backgroundColor: '#6a11cb', padding: 18, borderRadius: 15, alignItems: 'center', marginTop: 10 },
  unlockButtonText: { color: '#fff', fontWeight: 'bold', fontSize: 16 },

  /* Banners */
  recommendationBanner: { backgroundColor: '#1e1b4b', padding: 20, borderRadius: 20, marginBottom: 12, borderWidth: 1, borderColor: '#6a11cb' },
  bannerLabel: { color: '#FFD700', fontSize: 11, fontWeight: '900', letterSpacing: 1.5, marginBottom: 8 },
  recommendationText: { color: '#fff', fontSize: 15, lineHeight: 22 },

  summaryBanner: { flexDirection: 'row', backgroundColor: 'rgba(106,17,203,0.12)', borderRadius: 16, padding: 15, marginBottom: 12, borderWidth: 1, borderColor: 'rgba(106,17,203,0.3)' },
  summaryBannerItem: { flex: 1, alignItems: 'center' },
  summaryBannerLabel: { color: 'rgba(255,255,255,0.45)', fontSize: 11, fontWeight: '700' },
  summaryBannerValue: { color: '#fff', fontSize: 15, fontWeight: 'bold', marginTop: 2 },

  /* Alertas */
  alertsContainer: { backgroundColor: 'rgba(245,158,11,0.08)', borderRadius: 16, padding: 15, marginBottom: 12, borderWidth: 1, borderColor: 'rgba(245,158,11,0.3)' },
  alertRow: { flexDirection: 'row', alignItems: 'flex-start', marginBottom: 8 },
  alertText: { color: '#f59e0b', fontSize: 13, flex: 1, lineHeight: 18 },

  /* Cards */
  card: { backgroundColor: 'rgba(255,255,255,0.05)', borderRadius: 20, padding: 18, marginBottom: 12, borderWidth: 1, borderColor: 'rgba(255,255,255,0.08)' },
  cardHighlighted: { borderColor: '#6a11cb', borderWidth: 1.5, backgroundColor: 'rgba(106,17,203,0.08)' },
  bestBadge: { position: 'absolute', top: 0, right: 0, backgroundColor: '#6a11cb', paddingHorizontal: 10, paddingVertical: 4, borderBottomLeftRadius: 12, borderTopRightRadius: 20 },
  bestBadgeText: { color: '#fff', fontSize: 10, fontWeight: 'bold' },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
  cardTitleRow: { flexDirection: 'row', alignItems: 'center', flex: 1 },
  cardTitle: { color: '#fff', fontSize: 16, fontWeight: 'bold', flex: 1 },
  summaryRow: { flexDirection: 'row', alignItems: 'center' },
  summaryItem: { flex: 1, alignItems: 'center' },
  summaryLabel: { color: 'rgba(255,255,255,0.45)', fontSize: 11 },
  summaryValue: { color: '#fff', fontSize: 16, fontWeight: 'bold', marginTop: 2 },
  summaryDivider: { width: 1, height: 40, backgroundColor: 'rgba(255,255,255,0.1)', marginHorizontal: 10 },
  tapHint: { color: 'rgba(255,255,255,0.25)', fontSize: 11, textAlign: 'center', marginTop: 10 },
  divider: { height: 1, backgroundColor: 'rgba(255,255,255,0.08)', marginVertical: 12 },
  detailRow: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 6 },
  detailLabel: { color: 'rgba(255,255,255,0.5)', fontSize: 13 },
  detailValue: { color: '#fff', fontSize: 13, fontWeight: '600' },
  meaningBox: { backgroundColor: 'rgba(106,17,203,0.12)', borderRadius: 12, padding: 12, marginTop: 10 },
  meaningLabel: { color: '#6a11cb', fontSize: 12, fontWeight: '700', marginBottom: 4 },
  meaningText: { color: 'rgba(255,255,255,0.7)', fontSize: 13, lineHeight: 18 },

  /* MCMV info */
  mcmvInfo: { flexDirection: 'row', backgroundColor: 'rgba(106,17,203,0.08)', borderRadius: 14, padding: 14, marginBottom: 12, alignItems: 'flex-start' },
  mcmvInfoText: { color: 'rgba(255,255,255,0.6)', fontSize: 13, flex: 1, lineHeight: 18 },

  /* Custas */
  custasBox: { backgroundColor: 'rgba(255,255,255,0.04)', borderRadius: 18, padding: 18, marginBottom: 12, borderWidth: 1, borderColor: 'rgba(255,255,255,0.08)' },
  custasTitle: { color: '#fff', fontSize: 15, fontWeight: 'bold', marginBottom: 12 },

  /* Botões */
  saveButton: { width: '100%', borderRadius: 15, overflow: 'hidden', marginTop: 20 },
  saveGradient: { flexDirection: 'row', height: 55, alignItems: 'center', justifyContent: 'center' },
  saveButtonText: { color: '#fff', fontSize: 16, fontWeight: 'bold' },
  redoButton: { marginTop: 20, padding: 20, alignItems: 'center' },
  redoButtonText: { color: '#aaa' },
});
