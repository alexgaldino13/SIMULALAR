import React from 'react';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity, SafeAreaView, Alert, ActivityIndicator, Linking } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { useSimulation } from '../../context/SimulationContext';
import { authService } from '../../api/authService';
import { BASE_URL } from '../../api/config';
import SimulationCharts from '../../components/SimulationCharts';
import { TextInputMask } from 'react-native-masked-text';
import apiClient from '../../api/client';

export default function ResultsScreen({ route, navigation }: any) {
  const { results } = route?.params || { results: null };
  const { data: wizardData, leadCaptured, leadInfo, setLeadCaptured } = useSimulation();
  const [saving, setSaving] = React.useState(false);
  const [unlocked, setUnlocked] = React.useState(leadCaptured);
  const [leadLoading, setLeadLoading] = React.useState(false);
  const [leadForm, setLeadForm] = React.useState(leadInfo || { nome: '', whatsapp: '' });

  // Proteção contra renderização sem dados
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
      Alert.alert('Dados Necessários', 'Por favor, preencha seu nome e whatsapp para ver o relatório completo.');
      return;
    }

    setLeadLoading(true);
    try {
      await apiClient.post('/api/v1/capturar-lead/', {
        ...leadForm,
        origem: 'MOBILE',
        valor_imovel: results.valor_imovel,
        perfil: wizardData.perfil_objetivos.perfil_usuario
      });
      setLeadCaptured(true, leadForm);
      setUnlocked(true);
    } catch (error) {
      console.error('Erro lead:', error);
      Alert.alert('Erro', 'Ocorreu um problema ao processar seus dados. Tente novamente.');
    } finally {
      setLeadLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const payload = {
        titulo: `Simulação ${results.valor_imovel ? 'R$ ' + results.valor_imovel.toLocaleString('pt-BR') : ''}`,
        dados_wizard: wizardData,
        resultados: results
      };
      await authService.saveSimulation(payload);
      Alert.alert('Sucesso 🎉', 'Simulação salva no seu histórico!', [
        { text: 'Ir para Dashboard', onPress: () => navigation.navigate('Dashboard') },
        { text: 'Ok', style: 'cancel' }
      ]);
    } catch (error: any) {
      Alert.alert('Ops!', 'Não conseguimos salvar sua simulação agora.');
    } finally {
      setSaving(false);
    }
  };

  const ResultCard = ({ title, data, type }: any) => {
    const isRecommendation = results.analise?.melhor_cenario === type;
    return (
      <View style={[styles.card, isRecommendation ? styles.cardHighlighted : {}]}>
        {isRecommendation && (
          <View style={styles.bestBadge}>
            <Text style={styles.bestBadgeText}>RECOMENDADO</Text>
          </View>
        )}
        <View style={styles.cardHeader}>
          <Text style={styles.cardTitle}>{title}</Text>
          <Ionicons name={type === 'consorcio' ? 'people' : 'business'} size={24} color="#6a11cb" />
        </View>
        <View style={styles.divider} />
        <View style={styles.detailRow}>
          <Text style={styles.detailLabel}>Sua Parcela</Text>
          <Text style={styles.detailValue}>{data.parcela_inicial || 'N/A'}</Text>
        </View>
        <View style={styles.detailRow}>
          <Text style={styles.detailLabel}>Custo Final</Text>
          <Text style={[styles.detailValue, { color: '#ff4d4d' }]}>{data.total_custo || 'N/A'}</Text>
        </View>
        {!!data.cet_anual && (
          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>CET Anual</Text>
            <Text style={[styles.detailValue, { color: '#10b981' }]}>{data.cet_anual}</Text>
          </View>
        )}
      </View>
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      <LinearGradient colors={['#0f0c29', '#302b63', '#24243e']} style={StyleSheet.absoluteFill} />

      {!unlocked ? (
        <View style={styles.leadGate}>
          <View style={styles.leadCard}>
            <Text style={styles.leadTitle}>Sua simulação está pronta! 🚀</Text>
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
                  placeholder="WhatsApp"
                  placeholderTextColor="#555"
                  value={leadForm.whatsapp}
                  onChangeText={(v) => setLeadForm({ ...leadForm, whatsapp: v })}
                />
            </View>

            <TouchableOpacity style={styles.unlockButton} onPress={handleLeadSubmit}>
               <Text style={styles.unlockButtonText}>Ver Resultados →</Text>
            </TouchableOpacity>
          </View>
        </View>
      ) : (
        <ScrollView contentContainerStyle={styles.scrollContent}>
          <View style={styles.recommendationBanner}>
              <Text style={styles.bannerTitle}>RECOMENDAÇÃO SIMULALAR</Text>
              <Text style={styles.recommendationText}>{results.analise?.texto_principal || 'Análise indisponível'}</Text>
          </View>

          <SimulationCharts results={results} />

          {results.resultados && Object.entries(results.resultados).map(([key, value]: any) => (
            <ResultCard key={key} title={value.metodo} data={value} type={key} />
          ))}

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
  recommendationBanner: { backgroundColor: '#1e1b4b', padding: 20, borderRadius: 24, marginBottom: 20, borderWidth: 1, borderColor: '#6a11cb' },
  bannerTitle: { color: '#FFD700', fontSize: 12, fontWeight: '900', marginBottom: 10 },
  recommendationText: { color: '#fff', fontSize: 16, lineHeight: 24 },
  card: { backgroundColor: 'rgba(255,255,255,0.05)', borderRadius: 20, padding: 20, marginBottom: 15 },
  cardHighlighted: { borderColor: '#6a11cb', borderWidth: 1 },
  bestBadge: { position: 'absolute', top: 0, right: 0, backgroundColor: '#6a11cb', padding: 5, borderBottomLeftRadius: 10 },
  bestBadgeText: { color: '#fff', fontSize: 10, fontWeight: 'bold' },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 10 },
  cardTitle: { color: '#fff', fontSize: 18, fontWeight: 'bold' },
  divider: { height: 1, backgroundColor: 'rgba(255,255,255,0.1)', marginVertical: 10 },
  detailRow: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 8 },
  detailLabel: { color: '#aaa', fontSize: 14 },
  detailValue: { color: '#fff', fontSize: 14, fontWeight: 'bold' },
  redoButton: { marginTop: 20, padding: 20, alignItems: 'center' },
  redoButtonText: { color: '#aaa' },
  leadGate: { flex: 1, justifyContent: 'center', padding: 20 },
  leadCard: { backgroundColor: '#1e1b4b', padding: 30, borderRadius: 30, alignItems: 'center' },
  leadTitle: { color: '#fff', fontSize: 22, fontWeight: 'bold', textAlign: 'center', marginBottom: 20 },
  linksRow: { flexDirection: 'row', marginBottom: 20 },
  linkText: { color: '#7f7fd5', textDecorationLine: 'underline', fontSize: 12 },
  linkDivider: { color: '#444', marginHorizontal: 10 },
  mobileInputContainer: { width: '100%', backgroundColor: 'rgba(255,255,255,0.1)', borderRadius: 15, marginBottom: 10, padding: 15 },
  mobileInput: { color: '#fff', fontSize: 16 },
  unlockButton: { width: '100%', backgroundColor: '#6a11cb', padding: 18, borderRadius: 15, alignItems: 'center', marginTop: 10 },
  unlockButtonText: { color: '#fff', fontWeight: 'bold', fontSize: 16 },
  saveButton: {
    width: '100%',
    borderRadius: 15,
    overflow: 'hidden',
    marginTop: 20,
    elevation: 4,
    shadowColor: '#6a11cb',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 5,
  },
  saveGradient: {
    flexDirection: 'row',
    height: 55,
    alignItems: 'center',
    justifyContent: 'center',
  },
  saveButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  }
});
