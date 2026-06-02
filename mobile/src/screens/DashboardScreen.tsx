import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, SafeAreaView, ScrollView, TouchableOpacity, ActivityIndicator, RefreshControl } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { authService } from '../api/authService';
import { setAuthToken } from '../api/client';
import SimulationCharts from '../components/SimulationCharts';

export default function DashboardScreen({ navigation }: any) {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [data, setData] = useState<any>(null);

  const fetchDashboardData = async () => {
    try {
      const response = await authService.getDashboardData();
      setData(response);
    } catch (error: any) {
      console.error('Falha ao carregar dashboard:', error);
      if (error.response?.status === 401) {
        setAuthToken(null);
        navigation.replace('Auth');
      }
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const onRefresh = () => {
    setRefreshing(true);
    fetchDashboardData();
  };

  if (loading) {
    return (
      <LinearGradient colors={['#0f0c29', '#302b63', '#24243e']} style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#FFD700" />
        <Text style={styles.loadingText}>Sincronizando seus dados financeiros...</Text>
      </LinearGradient>
    );
  }

  const firstName = data?.profile?.first_name || 'Investidor';
  const stats = data?.stats || { total_volume: 0, avg_property_value: 0 };

  return (
    <SafeAreaView style={styles.container}>
      <LinearGradient colors={['#0f0c29', '#302b63', '#24243e']} style={StyleSheet.absoluteFill} />
      
      <ScrollView 
        contentContainerStyle={styles.scrollContent}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#FFD700" />}
      >
        {/* Header Section */}
        <View style={styles.header}>
          <View>
            <Text style={styles.greeting}>Olá, {firstName} 👋</Text>
            <Text style={styles.subtitle}>Sua jornada para o lar começa aqui.</Text>
          </View>
          <TouchableOpacity onPress={() => navigation.navigate('Profile')} style={styles.profileButton}>
            <Ionicons name="person-circle-outline" size={40} color="#fff" />
          </TouchableOpacity>
        </View>

        {/* Main Stats Cards (Glassmorphism) */}
        <View style={styles.statsGrid}>
          <View style={styles.statCard}>
            <View style={[styles.iconCircle, { backgroundColor: 'rgba(106, 17, 203, 0.2)' }]}>
              <Ionicons name="calculator" size={24} color="#6a11cb" />
            </View>
            <Text style={styles.statLabel}>Simulações</Text>
            <Text style={styles.statValue}>{data?.total_simulations || 0}</Text>
          </View>

          <View style={styles.statCard}>
            <View style={[styles.iconCircle, { backgroundColor: 'rgba(255, 215, 0, 0.2)' }]}>
              <Ionicons name="cash-outline" size={24} color="#FFD700" />
            </View>
            <Text style={styles.statLabel}>Volume Total</Text>
            <Text style={styles.statValue}>R$ {(stats.total_volume / 1000000).toFixed(1)}M</Text>
          </View>
        </View>

        {/* Quick Action Button */}
        <TouchableOpacity 
          style={styles.mainActionButton}
          onPress={() => navigation.navigate('Wizard')}
        >
          <LinearGradient 
            colors={['#6a11cb', '#2575fc']} 
            start={{ x: 0, y: 0 }} 
            end={{ x: 1, y: 0 }} 
            style={styles.gradientButton}
          >
            <Ionicons name="add-circle-outline" size={24} color="#fff" />
            <Text style={styles.buttonText}>Nova Simulação de Compra</Text>
          </LinearGradient>
        </TouchableOpacity>

        {/* Dynamic Chart Section */}
        {data?.recent_simulations?.length > 0 ? (
          <View style={styles.sectionContainer}>
            <Text style={styles.sectionTitle}>Análise de Mercado Recente</Text>
            <View style={styles.chartWrapper}>
              {/* Passamos o primeiro resultado recente para demonstração visual */}
              <SimulationCharts results={data.recent_simulations[0]} />
            </View>
          </View>
        ) : (
          <View style={styles.emptyState}>
            <Ionicons name="analytics-outline" size={48} color="rgba(255,255,255,0.2)" />
            <Text style={styles.emptyText}>Faça sua primeira simulação para gerar gráficos de comparativo.</Text>
          </View>
        )}

        {/* Recent List */}
        <View style={styles.sectionContainer}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Simulações Recentes</Text>
            <TouchableOpacity onPress={() => navigation.navigate('SavedSimulations')}>
              <Text style={styles.seeAllText}>Ver todas</Text>
            </TouchableOpacity>
          </View>
          
          {data?.recent_simulations?.map((sim: any) => (
            <TouchableOpacity 
              key={sim.id} 
              style={styles.simulationItem}
              onPress={() => navigation.navigate('SimulationDetail', { simulation: sim })}
            >
              <View style={styles.simulationIcon}>
                <Ionicons name="home-outline" size={20} color="#6a11cb" />
              </View>
              <View style={styles.simulationInfo}>
                <Text style={styles.simulationTitle}>{sim.titulo}</Text>
                <Text style={styles.simulationDate}>{new Date(sim.criado_em).toLocaleDateString('pt-BR')}</Text>
              </View>
              <Ionicons name="chevron-forward" size={20} color="rgba(255,255,255,0.3)" />
            </TouchableOpacity>
          ))}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f0c29',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    color: '#fff',
    marginTop: 15,
    fontSize: 16,
    opacity: 0.8,
  },
  scrollContent: {
    padding: 20,
    paddingBottom: 40,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 20,
    marginBottom: 30,
  },
  greeting: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
  },
  subtitle: {
    fontSize: 14,
    color: '#aaa',
    marginTop: 4,
  },
  profileButton: {
    padding: 5,
  },
  statsGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 25,
  },
  statCard: {
    width: '48%',
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    borderRadius: 20,
    padding: 20,
    borderWidth: 0.5,
    borderColor: 'rgba(255, 255, 255, 0.1)',
  },
  iconCircle: {
    width: 44,
    height: 44,
    borderRadius: 22,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  statLabel: {
    color: '#aaa',
    fontSize: 12,
    marginBottom: 4,
  },
  statValue: {
    color: '#fff',
    fontSize: 20,
    fontWeight: 'bold',
  },
  mainActionButton: {
    marginBottom: 30,
    borderRadius: 16,
    overflow: 'hidden',
    elevation: 8,
    shadowColor: '#6a11cb',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 10,
  },
  gradientButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 18,
    gap: 10,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  sectionContainer: {
    marginBottom: 25,
  },
  sectionHeader: {
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
  seeAllText: {
    color: '#7f7fd5',
    fontSize: 14,
  },
  chartWrapper: {
    backgroundColor: 'rgba(255, 255, 255, 0.03)',
    borderRadius: 20,
    paddingTop: 10,
    overflow: 'hidden',
    alignItems: 'center',
  },
  simulationItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.03)',
    borderRadius: 16,
    padding: 15,
    marginBottom: 10,
    borderWidth: 0.5,
    borderColor: 'rgba(255, 255, 255, 0.05)',
  },
  simulationIcon: {
    width: 40,
    height: 40,
    borderRadius: 10,
    backgroundColor: 'rgba(106, 17, 203, 0.1)',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
  },
  simulationInfo: {
    flex: 1,
  },
  simulationTitle: {
    color: '#fff',
    fontSize: 15,
    fontWeight: '600',
  },
  simulationDate: {
    color: '#666',
    fontSize: 12,
    marginTop: 2,
  },
  emptyState: {
    alignItems: 'center',
    padding: 40,
    backgroundColor: 'rgba(255,255,255,0.02)',
    borderRadius: 20,
    marginBottom: 25,
  },
  emptyText: {
    color: '#666',
    fontSize: 14,
    textAlign: 'center',
    marginTop: 15,
    lineHeight: 20,
  }
});
