import React, { useState } from 'react';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity, SafeAreaView, Alert, ActivityIndicator, Linking } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { authService } from '../api/authService';
import SimulationCharts from '../components/SimulationCharts';
import { API_CONFIG, BASE_URL } from '../api/config';

export default function SimulationDetailScreen({ route, navigation }: any) {
  const { simulation } = route.params;
  const [deleting, setDeleting] = useState(false);

  const results = simulation.resultados;

  const handleExportPDF = () => {
    const pdfUrl = `${BASE_URL}${API_CONFIG.ENDPOINTS.EXPORT_PDF(simulation.id)}`; 
    Linking.openURL(pdfUrl).catch(err => {
      console.error('Erro ao abrir link:', err);
      Alert.alert('Erro', 'Não foi possível abrir o link do PDF.');
    });
  };

  const handleDelete = () => {
    Alert.alert(
      'Excluir Simulação',
      'Tem certeza que deseja apagar esta simulação permanentemente?',
      [
        { text: 'Cancelar', style: 'cancel' },
        { 
          text: 'Excluir', 
          style: 'destructive',
          onPress: async () => {
            setDeleting(true);
            try {
              await authService.deleteSimulation(simulation.id);
              navigation.navigate('Dashboard'); // Voltar para dashboard após exclusão
            } catch (error) {
              Alert.alert('Erro', 'Não foi possível excluir a simulação.');
            } finally {
              setDeleting(false);
            }
          }
        }
      ]
    );
  };

  const ResultCard = ({ title, data, type }: any) => {
    const isConsorcio = type === 'consorcio';
    const accentColor = isConsorcio ? '#FFD700' : '#6a11cb';
    
    return (
      <View style={styles.card}>
        <View style={styles.cardHeader}>
          <Text style={styles.cardTitle}>{title}</Text>
          <View style={[styles.cardIconCircle, { backgroundColor: `${accentColor}20` }]}>
            <Ionicons 
              name={isConsorcio ? 'dice-outline' : 'trending-down'} 
              size={18} 
              color={accentColor} 
            />
          </View>
        </View>
        
        <View style={styles.cardContent}>
          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Parcela Inicial</Text>
            <Text style={styles.detailValue}>{data.parcela_inicial || 'N/A'}</Text>
          </View>

          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Custo Total</Text>
            <Text style={[styles.detailValue, { color: '#fff' }]}>{data.total_custo || 'N/A'}</Text>
          </View>

          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Prazo Final</Text>
            <Text style={styles.detailValue}>{data.prazo_final_anos} anos</Text>
          </View>
        </View>
      </View>
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      <LinearGradient colors={['#0f0c29', '#302b63', '#24243e']} style={StyleSheet.absoluteFill} />
      
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backIconButton}>
          <Ionicons name="arrow-back" size={24} color="#fff" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Detalhes da Simulação</Text>
        <TouchableOpacity onPress={handleDelete} disabled={deleting} style={styles.deleteButton}>
          {deleting ? (
            <ActivityIndicator size="small" color="#ff4444" />
          ) : (
            <Ionicons name="trash-outline" size={22} color="#ff4444" />
          )}
        </TouchableOpacity>
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
        <View style={styles.titleSection}>
          <Text style={styles.simTitle}>{simulation.titulo}</Text>
          <Text style={styles.simDate}>
            <Ionicons name="calendar-outline" size={14} color="#666" /> Criado em {new Date(simulation.criado_em).toLocaleDateString('pt-BR')}
          </Text>
        </View>

        {/* RECOMENDAÇÃO INTELIGENTE (GLASS CARD) */}
        <View style={styles.recommendationBanner}>
          <LinearGradient 
            colors={['rgba(106, 17, 203, 0.3)', 'rgba(37, 117, 252, 0.1)']}
            style={styles.recommendationGradient}
          >
            <View style={styles.bannerHeader}>
              <View style={styles.sparkleCircle}>
                <Ionicons name="sparkles" size={18} color="#FFD700" />
              </View>
              <Text style={styles.bannerTitle}>RECOMENDAÇÃO SIMULALAR</Text>
            </View>
            <Text style={styles.recommendationText}>
              {results.analise?.texto_principal || 'Análise indisponível para esta simulação.'}
            </Text>
          </LinearGradient>
        </View>

        <View style={styles.sectionTitleRow}>
          <Text style={styles.sectionTitle}>Análise Visual</Text>
        </View>
        <View style={styles.chartContainer}>
          <SimulationCharts results={results} />
        </View>

        <View style={styles.actionRow}>
          <TouchableOpacity style={styles.pdfButton} onPress={handleExportPDF}>
            <LinearGradient 
              colors={['#2e7d32', '#1b5e20']} 
              style={styles.pdfGradient}
            >
              <Ionicons name="download-outline" size={20} color="#fff" style={{ marginRight: 8 }} />
              <Text style={styles.pdfButtonText}>Exportar para PDF</Text>
            </LinearGradient>
          </TouchableOpacity>
        </View>

        <View style={styles.sectionTitleRow}>
          <Text style={styles.sectionTitle}>Comparativo de Cenários</Text>
          <Ionicons name="layers-outline" size={20} color="rgba(255,255,255,0.4)" />
        </View>
        
        {results.resultados && Object.entries(results.resultados).map(([key, value]: any) => (
          <ResultCard key={key} title={value.metodo} data={value} type={key} />
        ))}

        <TouchableOpacity 
          style={styles.backButton}
          onPress={() => navigation.goBack()}
        >
          <Text style={styles.backButtonText}>Voltar ao Dashboard</Text>
        </TouchableOpacity>
      </ScrollView>
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
    paddingHorizontal: 20,
    paddingVertical: 15,
  },
  backIconButton: {
    padding: 5,
  },
  headerTitle: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
    letterSpacing: 0.5,
  },
  deleteButton: {
    padding: 5,
  },
  scrollContent: {
    padding: 20,
    paddingBottom: 40,
  },
  titleSection: {
    marginBottom: 25,
  },
  simTitle: {
    color: '#fff',
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 6,
  },
  simDate: {
    color: '#888',
    fontSize: 14,
    flexDirection: 'row',
    alignItems: 'center',
  },
  recommendationBanner: {
    borderRadius: 24,
    overflow: 'hidden',
    marginBottom: 30,
    borderWidth: 1,
    borderColor: 'rgba(106, 17, 203, 0.4)',
    elevation: 5,
    shadowColor: '#6a11cb',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 10,
  },
  recommendationGradient: {
    padding: 20,
  },
  bannerHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  sparkleCircle: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: 'rgba(255, 215, 0, 0.15)',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 10,
  },
  bannerTitle: {
    color: '#FFD700',
    fontSize: 13,
    fontWeight: '900',
    letterSpacing: 1,
  },
  recommendationText: {
    color: '#fff',
    fontSize: 16,
    lineHeight: 24,
    opacity: 0.9,
  },
  sectionTitleRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  sectionTitle: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  chartContainer: {
    backgroundColor: 'rgba(255, 255, 255, 0.03)',
    borderRadius: 24,
    padding: 10,
    marginBottom: 30,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.05)',
  },
  actionRow: {
    flexDirection: 'row',
    marginBottom: 35,
  },
  pdfButton: {
    flex: 1,
    borderRadius: 16,
    overflow: 'hidden',
    elevation: 4,
  },
  pdfGradient: {
    flexDirection: 'row',
    height: 55,
    alignItems: 'center',
    justifyContent: 'center',
  },
  pdfButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  card: {
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    borderRadius: 20,
    padding: 20,
    marginBottom: 15,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 18,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255, 255, 255, 0.05)',
    paddingBottom: 12,
  },
  cardTitle: {
    color: '#fff',
    fontSize: 17,
    fontWeight: 'bold',
  },
  cardIconCircle: {
    width: 32,
    height: 32,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
  },
  cardContent: {
    gap: 12,
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  detailLabel: {
    color: '#aaa',
    fontSize: 14,
  },
  detailValue: {
    color: '#7f7fd5',
    fontSize: 15,
    fontWeight: 'bold',
  },
  backButton: {
    height: 60,
    borderRadius: 16,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 25,
    borderWidth: 1,
    borderColor: 'rgba(106, 17, 203, 0.3)',
  },
  backButtonText: {
    color: '#6a11cb',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
