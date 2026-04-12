import React from 'react';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity, SafeAreaView, Alert, ActivityIndicator, Platform } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useSimulation } from '../../context/SimulationContext';
import { authService } from '../../api/authService';
import SimulationCharts from '../../components/SimulationCharts';
import { TextInputMask } from 'react-native-masked-text';
import apiClient from '../../api/client';

export default function ResultsScreen({ route, navigation }: any) {
  const { results } = route.params;
  const { data: wizardData } = useSimulation();
  const [saving, setSaving] = React.useState(false);
  const [unlocked, setUnlocked] = React.useState(false);
  const [leadLoading, setLeadLoading] = React.useState(false);
  const [leadForm, setLeadForm] = React.useState({ nome: '', whatsapp: '' });


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
      setUnlocked(true);
    } catch (error) {
      console.error('Erro lead:', error);
      // Even if API fails, we might want to unlock to not block user, 
      // but let's try to be strict for CPL.
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
      Alert.alert('Sucesso 🎉', 'Esta simulação foi salva no seu histórico e você pode acessá-la quando quiser.', [
        { text: 'Ver no Dashboard', onPress: () => navigation.navigate('Main', { screen: 'Dashboard' }) },
        { text: 'Ficar aqui', style: 'cancel' }
      ]);
    } catch (error: any) {
      console.error('Erro ao salvar:', error.response?.data || error.message);
      Alert.alert('Ops!', 'Não conseguimos salvar sua simulação agora. Tente novamente em instantes.');
    } finally {
      setSaving(false);
    }
  };

  const ResultCard = ({ title, data, type }: any) => {
    const isRecommendation = results.analise?.melhor_cenario === type;
    
    return (
      <View style={[styles.card, isRecommendation ? styles.cardHighlighted : null]}>
        {isRecommendation ? (
          <View style={styles.bestBadge}>
            <Text style={styles.bestBadgeText}>MELHOR OPÇÃO</Text>
          </View>
        ) : null}
        
        <View style={styles.cardHeader}>
          <Text style={styles.cardTitle}>{title}</Text>
          <View style={[styles.iconCircle, { backgroundColor: isRecommendation ? '#6a11cb' : 'rgba(255,255,255,0.05)' }]}>
            <Ionicons 
              name={type === 'consorcio' ? 'dice-outline' : 'trending-down'} 
              size={18} 
              color={isRecommendation ? '#fff' : '#6a11cb'} 
            />
          </View>
        </View>
        
        <View style={styles.divider} />
        
        <View style={styles.detailRow}>
          <Text style={styles.detailLabel}>Parcela Inicial</Text>
          <Text style={styles.detailValue}>{data.parcela_inicial || 'N/A'}</Text>
        </View>

        <View style={styles.detailRow}>
          <Text style={styles.detailLabel}>Custo Total</Text>
          <Text style={styles.detailValue}>{data.total_custo || 'N/A'}</Text>
        </View>

        <View style={styles.detailRow}>
          <Text style={styles.detailLabel}>Prazo Total</Text>
          <Text style={styles.detailValue}>{data.prazo_final_anos} anos</Text>
        </View>

        <TouchableOpacity style={styles.detailButton} onPress={() => {}}>
          <Text style={styles.detailButtonText}>Ver Detalhes do Fluxo</Text>
        </TouchableOpacity>
      </View>
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity 
          onPress={() => navigation.navigate('Main', { screen: 'Dashboard' })}
          style={styles.headerIcon}
        >
          <Ionicons name="close" size={26} color="#fff" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Análise por IA</Text>
        <TouchableOpacity style={styles.headerIcon} onPress={handleSave}>
          <Ionicons name="share-outline" size={24} color="#fff" />
        </TouchableOpacity>
      </View>

      {!unlocked ? (
        <View style={styles.leadGate}>
          <View style={styles.leadCard}>
            <View style={styles.premiumBadge}>
              <Ionicons name="star" size={14} color="#333" />
              <Text style={styles.premiumBadgeText}>ACESSO PREMIUM</Text>
            </View>
            <Text style={styles.leadTitle}>Sua simulação está pronta! 🚀</Text>
            <Text style={styles.leadSubtitle}>
              Informe onde deseja receber o relatório detalhado para desbloquear os resultados.
            </Text>

            <View style={styles.mobileInputContainer}>
               <Ionicons name="person-outline" size={20} color="#888" style={{ marginRight: 10 }} />
               <TextInputMask
                  type={'custom'}
                  options={{ mask: '**************************************************' }}
                  style={styles.mobileInput}
                  placeholder="Seu Nome Completo"
                  placeholderTextColor="#555"
                  value={leadForm.nome}
                  onChangeText={(v) => setLeadForm({ ...leadForm, nome: v })}
                />
            </View>

            <View style={styles.mobileInputContainer}>
               <Ionicons name="logo-whatsapp" size={20} color="#888" style={{ marginRight: 10 }} />
               <TextInputMask
                  type={'cel-phone'}
                  options={{ maskType: 'BRL', withDDD: true, dddMask: '(99) ' }}
                  style={styles.mobileInput}
                  placeholder="Seu WhatsApp com DDD"
                  placeholderTextColor="#555"
                  value={leadForm.whatsapp}
                  onChangeText={(v) => setLeadForm({ ...leadForm, whatsapp: v })}
                />
            </View>

            <TouchableOpacity 
              style={[styles.unlockButton, leadLoading ? styles.buttonDisabled : null]}
              onPress={handleLeadSubmit}
              disabled={leadLoading}
            >
              {leadLoading ? <ActivityIndicator color="#fff" /> : <Text style={styles.unlockButtonText}>Ver Resultados Agora →</Text>}
            </TouchableOpacity>
            
            <Text style={styles.trustText}>🛡️ Seus dados estão seguros conosco.</Text>
          </View>
        </View>
      ) : (
        <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
          {/* RECOMENDAÇÃO INTELIGENTE (BANNER) */}
          <View style={styles.recommendationBanner}>
            <View style={styles.bannerHeader}>
              <View style={styles.sparkleContainer}>
                <Ionicons name="sparkles" size={20} color="#FFD700" />
              </View>
              <Text style={styles.bannerTitle}>RECOMENDAÇÃO SIMULALAR</Text>
            </View>
            <Text style={styles.recommendationText}>
              {results.analise?.texto_principal || 'Analisando os melhores cenários para você...'}
            </Text>
          </View>

          <SimulationCharts results={results} />

          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Cenários Comparados</Text>
            <Text style={styles.sectionSubtitle}>Baseado no seu perfil e prioridade</Text>
          </View>
          
          {results.resultados && Object.entries(results.resultados).map(([key, value]: any) => (
            <ResultCard key={key} title={value.metodo} data={value} type={key} />
          ))}

          <View style={styles.actionContainer}>
            <TouchableOpacity 
              style={[styles.saveButton, saving ? styles.buttonDisabled : null]}
              onPress={handleSave}
              disabled={saving ? true : false}
              activeOpacity={0.8}
            >
              {saving ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <View style={styles.saveButtonContent}>
                  <Ionicons name="save" size={20} color="#fff" style={{ marginRight: 10 }} />
                  <Text style={styles.saveButtonText}>Salvar Simulação</Text>
                </View>
              )}
            </TouchableOpacity>

            <TouchableOpacity 
              style={styles.redoButton}
              onPress={() => navigation.navigate('Step1')}
            >
              <Text style={styles.redoButtonText}>Fazer Nova Simulação</Text>
            </TouchableOpacity>
          </View>
        </ScrollView>
      )}

    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f0c29',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 15,
    paddingVertical: 15,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,255,255,0.08)',
  },
  headerIcon: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: 'rgba(255,255,255,0.05)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  headerTitle: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '800',
    letterSpacing: 0.5,
  },
  scrollContent: {
    padding: 20,
    paddingBottom: 60,
  },
  recommendationBanner: {
    backgroundColor: 'rgba(106, 17, 203, 0.15)',
    borderRadius: 24,
    padding: 24,
    marginBottom: 30,
    borderWidth: 1,
    borderColor: 'rgba(106, 17, 203, 0.4)',
  },
  bannerHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  sparkleContainer: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: 'rgba(255, 215, 0, 0.15)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  bannerTitle: {
    color: '#FFD700',
    fontSize: 13,
    fontWeight: '900',
    marginLeft: 10,
    letterSpacing: 1.2,
  },
  recommendationText: {
    color: '#fff',
    fontSize: 16,
    lineHeight: 25,
    fontWeight: '600',
  },
  sectionHeader: {
    marginBottom: 20,
    marginTop: 10,
  },
  sectionTitle: {
    color: '#fff',
    fontSize: 22,
    fontWeight: '800',
  },
  sectionSubtitle: {
    color: '#888',
    fontSize: 14,
    marginTop: 4,
  },
  card: {
    backgroundColor: 'rgba(255,255,255,0.03)',
    borderRadius: 20,
    padding: 20,
    marginBottom: 18,
    borderWidth: 1.5,
    borderColor: 'rgba(255,255,255,0.06)',
    overflow: 'hidden',
  },
  cardHighlighted: {
    borderColor: '#6a11cb',
    backgroundColor: 'rgba(106, 17, 203, 0.05)',
  },
  bestBadge: {
    position: 'absolute',
    top: 0,
    right: 0,
    backgroundColor: '#6a11cb',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderBottomLeftRadius: 12,
  },
  bestBadgeText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: '900',
    letterSpacing: 0.5,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  cardTitle: {
    color: '#fff',
    fontSize: 20,
    fontWeight: '800',
  },
  iconCircle: {
    width: 36,
    height: 36,
    borderRadius: 18,
    alignItems: 'center',
    justifyContent: 'center',
  },
  divider: {
    height: 1,
    backgroundColor: 'rgba(255,255,255,0.06)',
    marginBottom: 15,
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 14,
  },
  detailLabel: {
    color: '#999',
    fontSize: 14,
    fontWeight: '500',
  },
  detailValue: {
    color: '#fff',
    fontSize: 15,
    fontWeight: '700',
  },
  detailButton: {
    marginTop: 10,
    paddingVertical: 12,
    alignItems: 'center',
    borderTopWidth: 1,
    borderTopColor: 'rgba(255,255,255,0.05)',
  },
  detailButtonText: {
    color: '#6a11cb',
    fontSize: 14,
    fontWeight: '700',
  },
  actionContainer: {
    marginTop: 20,
  },
  saveButton: {
    flexDirection: 'row',
    backgroundColor: '#6a11cb',
    height: 60,
    borderRadius: 16,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#6a11cb',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.4,
    shadowRadius: 15,
    elevation: 8,
  },
  saveButtonContent: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  buttonDisabled: {
    backgroundColor: '#333',
    elevation: 0,
  },
  saveButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  redoButton: {
    height: 55,
    borderRadius: 16,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 15,
  },
  redoButtonText: {
    color: '#888',
    fontSize: 15,
    fontWeight: '600',
  },
  leadGate: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(15, 12, 41, 0.95)',
    zIndex: 100,
    justifyContent: 'center',
    padding: 20,
  },
  leadCard: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 30,
    padding: 30,
    borderWidth: 2,
    borderColor: '#6a11cb',
    alignItems: 'center',
  },
  premiumBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFD700',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 20,
    marginBottom: 20,
  },
  premiumBadgeText: {
    color: '#333',
    fontSize: 10,
    fontWeight: '900',
    marginLeft: 5,
  },
  leadTitle: {
    color: '#fff',
    fontSize: 24,
    fontWeight: '900',
    textAlign: 'center',
    marginBottom: 10,
  },
  leadSubtitle: {
    color: '#aaa',
    fontSize: 15,
    textAlign: 'center',
    marginBottom: 30,
    lineHeight: 22,
  },
  mobileInputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.07)',
    borderRadius: 16,
    height: 60,
    paddingHorizontal: 20,
    marginBottom: 15,
    width: '100%',
  },
  mobileInput: {
    flex: 1,
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  unlockButton: {
    backgroundColor: '#6a11cb',
    height: 60,
    borderRadius: 30,
    width: '100%',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 10,
    shadowColor: '#6a11cb',
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.5,
    shadowRadius: 20,
  },
  unlockButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '800',
  },
  trustText: {
    color: '#555',
    fontSize: 12,
    marginTop: 20,
  }
});

