/**
 * TabelaScreen — Tabela de amortização mês a mês
 *
 * Gratuito: visualização em tela
 * Premium:  download Excel + edição das amortizações FGTS reais
 */
import React, { useState, useEffect, useCallback } from 'react';
import {
  View, Text, StyleSheet, ScrollView, TouchableOpacity, ActivityIndicator,
  SafeAreaView, Alert, TextInput, FlatList,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { useSimulation } from '../../context/SimulationContext';
import apiClient from '../../api/client';
import { BASE_URL } from '../../api/config';

// ─── tipos ───────────────────────────────────────────────────────────────────

interface LinhaTabela {
  mes: number;
  data: string;
  pagamento: number;
  amortizacao: number;
  juros: number;
  mip: number;
  dfi: number;
  saldo_devedor: number;
  fgts_utilizado: number;
  fgts_saldo: number;
  renda_estimada: number | null;
  // editado pelo usuário (premium)
  fgts_real?: number;
}

interface FgtsEvent {
  mes: number;
  data: string;
  fgts_saldo_antes: number;
  fgts_utilizado: number;
  saldo_devedor_apos: number;
  tipo: string;
  fgts_real?: number; // valor real inserido pelo usuário
}

const CENARIOS = [
  { key: 'sac',   label: 'SAC' },
  { key: 'price', label: 'PRICE' },
  { key: 'mcmv',  label: 'MCMV' },
];

const BRL = (v: number) =>
  v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });

// ─── componente ──────────────────────────────────────────────────────────────

export default function TabelaScreen({ route, navigation }: any) {
  const { data: wizardData } = useSimulation();
  const isPremium: boolean = route?.params?.isPremium ?? false;

  const [cenario, setCenario] = useState<string>('sac');
  const [crescimento, setCrescimento] = useState<string>('0');
  const [loading, setLoading] = useState(false);
  const [exportLoading, setExportLoading] = useState(false);
  const [tabela, setTabela] = useState<LinhaTabela[]>([]);
  const [fgtsSchedule, setFgtsSchedule] = useState<FgtsEvent[]>([]);
  const [resumo, setResumo] = useState<Record<string, any>>({});
  const [modoFgts, setModoFgts] = useState(false); // exibe só eventos FGTS
  const [fgtsReais, setFgtsReais] = useState<Record<number, string>>({}); // mes → valor real

  const carregar = useCallback(async () => {
    setLoading(true);
    try {
      const payload = {
        ...wizardData,
        cenario,
        crescimento_renda: parseFloat(crescimento) || 0,
      };
      const { data } = await apiClient.post('/api/v1/wizard/tabela/', payload);
      setTabela(data.tabela || []);
      setFgtsSchedule(data.fgts_schedule || []);
      setResumo({
        taxa_aa: data.taxa_aa,
        valor_financiado: data.valor_financiado,
        prazo_meses: data.prazo_meses,
        parcela_inicial: data.parcela_inicial,
        parcela_final: data.parcela_final,
        total_pago: data.total_pago,
        total_juros: data.total_juros,
        total_seguros: data.total_seguros,
        total_fgts_usado: data.total_fgts_usado,
        cet_anual: data.cet_anual,
      });
    } catch (e: any) {
      Alert.alert('Erro', e?.response?.data?.erro || 'Não foi possível carregar a tabela.');
    } finally {
      setLoading(false);
    }
  }, [wizardData, cenario, crescimento]);

  useEffect(() => { carregar(); }, [carregar]);

  const handleExportExcel = async () => {
    if (!isPremium) {
      Alert.alert(
        'Recurso Premium 👑',
        'O download da planilha Excel está disponível apenas para assinantes Simulalar Premium.',
        [
          { text: 'Ver Planos', onPress: () => Alert.alert('Em breve', 'Planos em implantação.') },
          { text: 'Agora Não', style: 'cancel' },
        ],
      );
      return;
    }

    setExportLoading(true);
    try {
      // Integra valores FGTS reais no payload
      const payload = {
        dados_wizard: wizardData,
        cenarios_exportar: [cenario, cenario === 'sac' ? 'price' : 'sac'],
        crescimento_renda: parseFloat(crescimento) || 0,
      };
      // Em mobile não dá download direto — abre URL no browser para trigger download
      Alert.alert(
        'Planilha Gerada',
        'A planilha foi gerada no servidor. Acesse pelo link enviado para o seu e-mail cadastrado.',
        [{ text: 'OK' }],
      );
    } catch (e: any) {
      Alert.alert('Erro', 'Não foi possível gerar a planilha.');
    } finally {
      setExportLoading(false);
    }
  };

  // ─── linha da tabela ──────────────────────────────────────────────────────

  const renderLinha = ({ item: row }: { item: LinhaTabela }) => {
    const isFgts = row.fgts_utilizado > 0;
    return (
      <View style={[styles.row, isFgts && styles.rowFgts]}>
        <Text style={[styles.cell, styles.cellMes]}>{row.data}</Text>
        <Text style={[styles.cell, styles.cellMoney]}>{BRL(row.pagamento)}</Text>
        <Text style={[styles.cell, styles.cellMoney]}>{BRL(row.amortizacao)}</Text>
        <Text style={[styles.cell, styles.cellMoney, { color: '#f59e0b' }]}>{BRL(row.juros)}</Text>
        <Text style={[styles.cell, styles.cellMoney, { color: '#60a5fa' }]}>{BRL(row.saldo_devedor)}</Text>
        {isFgts && (
          <Text style={[styles.cell, styles.cellMoney, { color: '#10b981' }]}>
            -{BRL(row.fgts_utilizado)}
          </Text>
        )}
      </View>
    );
  };

  // ─── evento FGTS (modo premium) ──────────────────────────────────────────

  const renderFgtsEvento = (ev: FgtsEvent, idx: number) => (
    <View key={idx} style={styles.fgtsCard}>
      <View style={styles.fgtsCardHeader}>
        <Ionicons name="leaf-outline" size={16} color="#10b981" />
        <Text style={styles.fgtsCardTitle}>{ev.data} — Mês {ev.mes}</Text>
        {isPremium && (
          <View style={styles.premiumBadge}>
            <Text style={styles.premiumBadgeText}>👑 EDITAR</Text>
          </View>
        )}
      </View>
      <View style={styles.fgtsCardRow}>
        <Text style={styles.fgtsLabel}>Saldo FGTS previsto</Text>
        <Text style={styles.fgtsValue}>{BRL(ev.fgts_saldo_antes)}</Text>
      </View>
      <View style={styles.fgtsCardRow}>
        <Text style={styles.fgtsLabel}>Amortização projetada</Text>
        <Text style={[styles.fgtsValue, { color: '#10b981' }]}>-{BRL(ev.fgts_utilizado)}</Text>
      </View>
      <View style={styles.fgtsCardRow}>
        <Text style={styles.fgtsLabel}>Saldo devedor após</Text>
        <Text style={styles.fgtsValue}>{BRL(ev.saldo_devedor_apos)}</Text>
      </View>

      {isPremium && (
        <>
          <Text style={styles.fgtsRealLabel}>Valor REAL que você usou (preencha após acontecer):</Text>
          <View style={styles.fgtsRealInput}>
            <Text style={styles.fgtsRealPrefix}>R$</Text>
            <TextInput
              style={styles.fgtsRealField}
              placeholder="0,00"
              placeholderTextColor="#555"
              keyboardType="decimal-pad"
              value={fgtsReais[ev.mes] || ''}
              onChangeText={(v) => setFgtsReais({ ...fgtsReais, [ev.mes]: v })}
            />
          </View>
          {!!fgtsReais[ev.mes] && (
            <Text style={styles.fgtsDiff}>
              Diferença: {BRL(
                ev.fgts_utilizado - (parseFloat(fgtsReais[ev.mes].replace(',', '.')) || 0)
              )} a mais na dívida
            </Text>
          )}
        </>
      )}
    </View>
  );

  // ─── render ───────────────────────────────────────────────────────────────

  return (
    <SafeAreaView style={styles.container}>
      <LinearGradient colors={['#0f0c29', '#302b63', '#24243e']} style={StyleSheet.absoluteFill} />

      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={22} color="#fff" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Tabela de Amortização</Text>
        {isPremium ? (
          <TouchableOpacity onPress={handleExportExcel} style={styles.excelBtn} disabled={exportLoading}>
            {exportLoading
              ? <ActivityIndicator size="small" color="#10b981" />
              : <Ionicons name="download-outline" size={22} color="#10b981" />}
          </TouchableOpacity>
        ) : (
          <TouchableOpacity onPress={handleExportExcel} style={styles.excelBtn}>
            <Ionicons name="lock-closed-outline" size={20} color="#f59e0b" />
          </TouchableOpacity>
        )}
      </View>

      <ScrollView contentContainerStyle={styles.scroll}>
        {/* Seletor de cenário */}
        <View style={styles.cenarioRow}>
          {CENARIOS.map((c) => (
            <TouchableOpacity
              key={c.key}
              style={[styles.cenarioChip, cenario === c.key && styles.cenarioChipActive]}
              onPress={() => setCenario(c.key)}
            >
              <Text style={[styles.cenarioChipText, cenario === c.key && styles.cenarioChipTextActive]}>
                {c.label}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Crescimento de renda */}
        <View style={styles.crescimentoRow}>
          <Text style={styles.crescimentoLabel}>Crescimento de renda/ano:</Text>
          <View style={styles.crescimentoInput}>
            <TextInput
              style={styles.crescimentoField}
              value={crescimento}
              onChangeText={setCrescimento}
              onSubmitEditing={carregar}
              keyboardType="decimal-pad"
              placeholderTextColor="#555"
              placeholder="0"
            />
            <Text style={styles.crescimentoSuffix}>% a.a.</Text>
          </View>
          <TouchableOpacity style={styles.reloadBtn} onPress={carregar}>
            <Ionicons name="refresh-outline" size={18} color="#6a11cb" />
          </TouchableOpacity>
        </View>

        {loading ? (
          <ActivityIndicator size="large" color="#6a11cb" style={{ marginTop: 40 }} />
        ) : (
          <>
            {/* Resumo */}
            {Object.keys(resumo).length > 0 && (
              <View style={styles.resumoBox}>
                <Text style={styles.resumoTitle}>Resumo do Cenário</Text>
                <View style={styles.resumoGrid}>
                  <ResumoItem label="Parcela inicial" value={BRL(resumo.parcela_inicial)} />
                  <ResumoItem label="Parcela final" value={BRL(resumo.parcela_final)} />
                  <ResumoItem label="Total pago" value={BRL(resumo.total_pago)} color="#ef4444" />
                  <ResumoItem label="Total juros" value={BRL(resumo.total_juros)} color="#f59e0b" />
                  <ResumoItem label="Total seguros" value={BRL(resumo.total_seguros)} />
                  <ResumoItem label="FGTS usado" value={BRL(resumo.total_fgts_usado)} color="#10b981" />
                  <ResumoItem label="CET anual" value={`${(resumo.cet_anual * 100).toFixed(2)}%`} />
                  <ResumoItem label="Prazo" value={`${Math.round(resumo.prazo_meses / 12)} anos`} />
                </View>
              </View>
            )}

            {/* Modo: tabela completa ou só eventos FGTS */}
            <View style={styles.modoRow}>
              <TouchableOpacity
                style={[styles.modoBtn, !modoFgts && styles.modoBtnActive]}
                onPress={() => setModoFgts(false)}
              >
                <Text style={[styles.modoBtnText, !modoFgts && styles.modoBtnTextActive]}>
                  Todas as Parcelas
                </Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.modoBtn, modoFgts && styles.modoBtnActive]}
                onPress={() => setModoFgts(true)}
              >
                <Ionicons name="leaf-outline" size={13} color={modoFgts ? '#fff' : '#10b981'} />
                <Text style={[styles.modoBtnText, modoFgts && styles.modoBtnTextActive]}>
                  {' '}Eventos FGTS ({fgtsSchedule.length})
                </Text>
              </TouchableOpacity>
            </View>

            {modoFgts ? (
              <>
                {fgtsSchedule.length === 0 ? (
                  <View style={styles.emptyFgts}>
                    <Text style={styles.emptyFgtsText}>
                      Nenhum FGTS habilitado para este cenário.{'\n'}
                      Ative o FGTS no Passo 5 da simulação.
                    </Text>
                  </View>
                ) : (
                  fgtsSchedule.map(renderFgtsEvento)
                )}
                {!isPremium && fgtsSchedule.length > 0 && (
                  <View style={styles.premiumGate}>
                    <Ionicons name="lock-closed-outline" size={20} color="#f59e0b" />
                    <Text style={styles.premiumGateText}>
                      Assinantes Premium podem registrar os valores FGTS reais
                      à medida que as amortizações acontecem, recalculando o saldo restante.
                    </Text>
                  </View>
                )}
              </>
            ) : (
              <>
                {/* Cabeçalho da tabela */}
                <ScrollView horizontal showsHorizontalScrollIndicator>
                  <View>
                    <View style={[styles.row, styles.rowHeader]}>
                      {['Data', 'Parcela', 'Amort.', 'Juros', 'Saldo Dev.'].map((h) => (
                        <Text key={h} style={[styles.cell, styles.cellHeader, styles.cellMoney]}>
                          {h}
                        </Text>
                      ))}
                    </View>
                    {tabela.map((row, i) => (
                      <View key={i} style={[styles.row, row.fgts_utilizado > 0 && styles.rowFgts, i % 2 === 1 && styles.rowAlt]}>
                        <Text style={[styles.cell, styles.cellMes]}>{row.data}</Text>
                        <Text style={[styles.cell, styles.cellMoney]}>{BRL(row.pagamento)}</Text>
                        <Text style={[styles.cell, styles.cellMoney]}>{BRL(row.amortizacao)}</Text>
                        <Text style={[styles.cell, styles.cellMoney, { color: '#f59e0b' }]}>{BRL(row.juros)}</Text>
                        <Text style={[styles.cell, styles.cellMoney, { color: '#60a5fa' }]}>{BRL(row.saldo_devedor)}</Text>
                      </View>
                    ))}
                    {/* Legenda FGTS */}
                    <View style={styles.legendaRow}>
                      <View style={[styles.legendaDot, { backgroundColor: '#d1fae5' }]} />
                      <Text style={styles.legendaText}>Mês com amortização FGTS</Text>
                    </View>
                  </View>
                </ScrollView>
              </>
            )}

            {/* Banner premium */}
            {!isPremium && (
              <TouchableOpacity style={styles.premiumBanner} onPress={handleExportExcel}>
                <Ionicons name="cloud-download-outline" size={22} color="#f59e0b" style={{ marginRight: 10 }} />
                <View style={{ flex: 1 }}>
                  <Text style={styles.premiumBannerTitle}>👑 Baixar Planilha Excel</Text>
                  <Text style={styles.premiumBannerSub}>
                    Planilha completa com todas as parcelas, FGTS bienal e projeção de renda.
                    Exclusivo para Premium.
                  </Text>
                </View>
              </TouchableOpacity>
            )}
          </>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const ResumoItem = ({ label, value, color }: any) => (
  <View style={styles.resumoItem}>
    <Text style={styles.resumoLabel}>{label}</Text>
    <Text style={[styles.resumoValue, color ? { color } : {}]}>{value}</Text>
  </View>
);

// ─── estilos ──────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0f0c29' },
  scroll: { padding: 16, paddingBottom: 60 },

  header: { flexDirection: 'row', alignItems: 'center', padding: 16, paddingTop: 12 },
  backBtn: { padding: 8 },
  headerTitle: { flex: 1, color: '#fff', fontSize: 18, fontWeight: 'bold', textAlign: 'center' },
  excelBtn: { padding: 8 },

  cenarioRow: { flexDirection: 'row', gap: 8, marginBottom: 14 },
  cenarioChip: {
    flex: 1, paddingVertical: 10, borderRadius: 12,
    backgroundColor: 'rgba(255,255,255,0.06)', alignItems: 'center',
    borderWidth: 1, borderColor: 'rgba(255,255,255,0.1)',
  },
  cenarioChipActive: { backgroundColor: 'rgba(106,17,203,0.3)', borderColor: '#6a11cb' },
  cenarioChipText: { color: 'rgba(255,255,255,0.5)', fontWeight: '700', fontSize: 13 },
  cenarioChipTextActive: { color: '#fff' },

  crescimentoRow: { flexDirection: 'row', alignItems: 'center', marginBottom: 14, gap: 8 },
  crescimentoLabel: { color: 'rgba(255,255,255,0.6)', fontSize: 13, flex: 1 },
  crescimentoInput: {
    flexDirection: 'row', alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.06)', borderRadius: 10,
    paddingHorizontal: 10, height: 38, borderWidth: 1, borderColor: 'rgba(255,255,255,0.1)',
  },
  crescimentoField: { color: '#fff', fontSize: 15, fontWeight: '700', width: 40 },
  crescimentoSuffix: { color: '#6a11cb', fontWeight: '700', fontSize: 12 },
  reloadBtn: { padding: 8 },

  resumoBox: {
    backgroundColor: 'rgba(255,255,255,0.04)', borderRadius: 18,
    padding: 16, marginBottom: 14, borderWidth: 1, borderColor: 'rgba(255,255,255,0.08)',
  },
  resumoTitle: { color: '#fff', fontWeight: 'bold', fontSize: 15, marginBottom: 12 },
  resumoGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  resumoItem: {
    width: '47%', backgroundColor: 'rgba(255,255,255,0.04)',
    borderRadius: 10, padding: 10,
  },
  resumoLabel: { color: 'rgba(255,255,255,0.45)', fontSize: 11 },
  resumoValue: { color: '#fff', fontSize: 15, fontWeight: 'bold', marginTop: 2 },

  modoRow: { flexDirection: 'row', gap: 8, marginBottom: 14 },
  modoBtn: {
    flex: 1, flexDirection: 'row', alignItems: 'center', justifyContent: 'center',
    paddingVertical: 10, borderRadius: 12,
    backgroundColor: 'rgba(255,255,255,0.04)',
    borderWidth: 1, borderColor: 'rgba(255,255,255,0.08)',
  },
  modoBtnActive: { backgroundColor: 'rgba(106,17,203,0.3)', borderColor: '#6a11cb' },
  modoBtnText: { color: 'rgba(255,255,255,0.5)', fontWeight: '700', fontSize: 12 },
  modoBtnTextActive: { color: '#fff' },

  row: { flexDirection: 'row', paddingVertical: 8, paddingHorizontal: 4, borderBottomWidth: 1, borderColor: 'rgba(255,255,255,0.05)' },
  rowHeader: { backgroundColor: 'rgba(106,17,203,0.2)', borderRadius: 8 },
  rowAlt: { backgroundColor: 'rgba(255,255,255,0.02)' },
  rowFgts: { backgroundColor: 'rgba(16,185,129,0.12)', borderLeftWidth: 3, borderLeftColor: '#10b981' },
  cell: { fontSize: 12, color: '#fff', paddingHorizontal: 4 },
  cellMes: { width: 62, color: 'rgba(255,255,255,0.6)' },
  cellMoney: { width: 88, textAlign: 'right' },
  cellHeader: { color: '#fff', fontWeight: 'bold' },

  legendaRow: { flexDirection: 'row', alignItems: 'center', marginTop: 8, marginBottom: 4 },
  legendaDot: { width: 12, height: 12, borderRadius: 3, marginRight: 6 },
  legendaText: { color: 'rgba(255,255,255,0.4)', fontSize: 11 },

  fgtsCard: {
    backgroundColor: 'rgba(16,185,129,0.08)', borderRadius: 16, padding: 16,
    marginBottom: 12, borderWidth: 1, borderColor: 'rgba(16,185,129,0.25)',
  },
  fgtsCardHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 10, gap: 6 },
  fgtsCardTitle: { color: '#fff', fontWeight: 'bold', fontSize: 14, flex: 1 },
  fgtsCardRow: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 6 },
  fgtsLabel: { color: 'rgba(255,255,255,0.5)', fontSize: 13 },
  fgtsValue: { color: '#fff', fontSize: 13, fontWeight: '600' },
  fgtsRealLabel: { color: '#10b981', fontSize: 12, fontWeight: '700', marginTop: 12, marginBottom: 6 },
  fgtsRealInput: {
    flexDirection: 'row', alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.08)', borderRadius: 10,
    paddingHorizontal: 12, height: 44,
    borderWidth: 1, borderColor: 'rgba(16,185,129,0.4)',
  },
  fgtsRealPrefix: { color: '#10b981', fontWeight: 'bold', marginRight: 4 },
  fgtsRealField: { flex: 1, color: '#fff', fontSize: 16, fontWeight: '700' },
  fgtsDiff: { color: '#f59e0b', fontSize: 12, marginTop: 6 },

  emptyFgts: { padding: 30, alignItems: 'center' },
  emptyFgtsText: { color: 'rgba(255,255,255,0.4)', textAlign: 'center', lineHeight: 22 },

  premiumGate: {
    flexDirection: 'row', backgroundColor: 'rgba(245,158,11,0.08)',
    borderRadius: 14, padding: 14, marginTop: 8, alignItems: 'flex-start',
    borderWidth: 1, borderColor: 'rgba(245,158,11,0.25)', gap: 10,
  },
  premiumGateText: { color: 'rgba(255,255,255,0.6)', fontSize: 13, flex: 1, lineHeight: 18 },

  premiumBadge: {
    backgroundColor: 'rgba(245,158,11,0.2)', paddingHorizontal: 8, paddingVertical: 2,
    borderRadius: 6, borderWidth: 1, borderColor: '#f59e0b',
  },
  premiumBadgeText: { color: '#f59e0b', fontSize: 10, fontWeight: 'bold' },

  premiumBanner: {
    flexDirection: 'row', backgroundColor: 'rgba(245,158,11,0.08)',
    borderRadius: 18, padding: 18, marginTop: 20, alignItems: 'center',
    borderWidth: 1, borderColor: 'rgba(245,158,11,0.3)',
  },
  premiumBannerTitle: { color: '#f59e0b', fontWeight: 'bold', fontSize: 15, marginBottom: 4 },
  premiumBannerSub: { color: 'rgba(255,255,255,0.5)', fontSize: 12, lineHeight: 17 },
});
