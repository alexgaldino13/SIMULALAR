import React, { useState } from 'react';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity, SafeAreaView, Alert, ActivityIndicator, Linking } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { authService } from '../api/authService';
import SimulationCharts from '../components/SimulationCharts';
import { API_CONFIG, BASE_URL } from '../api/config';

export default function SimulationDetailScreen({ route, navigation }: any) {
  const { simulation } = route.params;
  const [deleting, setDeleting] = useState(false);

  const results = simulation.resultados;

  const handleExportPDF = () => {
    // URL do relatório no backend centralizada em config.ts
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
              navigation.goBack();
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

  const ResultCard = ({ title, data, type }: any) => (
    <View style={styles.card}>
      <View style={styles.cardHeader}>
        <Text style={styles.cardTitle}>{title}</Text>
        <Ionicons name={type === 'consorcio' ? 'dice-outline' : 'trending-down'} size={20} color="#6a11cb" />
      </View>
      
      <View style={styles.detailRow}>
        <Text style={styles.detailLabel}>Parcela Inicial</Text>
        <Text style={styles.detailValue}>{data.parcela_inicial || 'N/A'}</Text>
      </View>

      <View style={styles.detailRow}>
        <Text style={styles.detailLabel}>Custo Total</Text>
        <Text style={styles.detailValue}>{data.total_custo || 'N/A'}</Text>
      </View>

      <View style={styles.detailRow}>
        <Text style={styles.detailLabel}>Prazo Final</Text>
        <Text style={styles.detailValue}>{data.prazo_final_anos} anos</Text>
      </View>
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Ionicons name="arrow-back" size={24} color="#fff" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Detalhes</Text>
        <TouchableOpacity onPress={handleDelete} disabled={deleting}>
          {deleting ? (
            <ActivityIndicator color="#ff4444" />
          ) : (
            <Ionicons name="trash-outline" size={24} color="#ff4444" />
          )}
        </TouchableOpacity>
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent}>
        <Text style={styles.simTitle}>{simulation.titulo}</Text>
        <Text style={styles.simDate}>Criado em {new Date(simulation.criado_em).toLocaleDateString('pt-BR')}</Text>

        {/* RECOMENDAÇÃO INTELIGENTE (BANNER) */}
        <View style={styles.recommendationBanner}>
          <View style={styles.bannerHeader}>
            <Ionicons name="sparkles" size={24} color="#FFD700" />
            <Text style={styles.bannerTitle}>RECOMENDAÇÃO SIMULALAR</Text>
          </View>
          <Text style={styles.recommendationText}>
            {results.analise?.texto_principal || 'Análise indisponível para esta simulação.'}
          </Text>
        </View>

        <SimulationCharts results={results} />

        <View style={styles.actionRow}>
          <TouchableOpacity style={styles.pdfButton} onPress={handleExportPDF}>
            <Ionicons name="download-outline" size={20} color="#fff" style={{ marginRight: 8 }} />
            <Text style={styles.pdfButtonText}>Exportar PDF</Text>
          </TouchableOpacity>
        </View>

        <Text style={styles.sectionTitle}>Comparativo Salvo</Text>
        
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
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,255,255,0.05)',
  },
  headerTitle: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  scrollContent: {
    padding: 20,
    paddingBottom: 40,
  },
  simTitle: {
    color: '#fff',
    fontSize: 22,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  simDate: {
    color: '#666',
    fontSize: 14,
    marginBottom: 25,
  },
  recommendationBanner: {
    backgroundColor: 'rgba(106, 17, 203, 0.2)',
    borderRadius: 20,
    padding: 20,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: '#6a11cb',
  },
  bannerHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  bannerTitle: {
    color: '#FFD700',
    fontSize: 14,
    fontWeight: 'bold',
    marginLeft: 10,
  },
  recommendationText: {
    color: '#fff',
    fontSize: 16,
    lineHeight: 24,
  },
  actionRow: {
    flexDirection: 'row',
    marginBottom: 30,
  },
  pdfButton: {
    flexDirection: 'row',
    backgroundColor: '#2e7d32',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 12,
    alignItems: 'center',
  },
  pdfButtonText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  sectionTitle: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 15,
  },
  card: {
    backgroundColor: 'rgba(255,255,255,0.03)',
    borderRadius: 16,
    padding: 20,
    marginBottom: 15,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.05)',
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  cardTitle: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  detailLabel: {
    color: '#888',
    fontSize: 14,
  },
  detailValue: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
  },
  backButton: {
    height: 55,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 20,
  },
  backButtonText: {
    color: '#6a11cb',
    fontSize: 15,
    fontWeight: 'bold',
  },
});
