import React, { useState } from 'react';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity, SafeAreaView, ActivityIndicator, RefreshControl } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useFocusEffect } from '@react-navigation/native';
import { authService } from '../api/authService';

export default function DashboardScreen({ navigation }: any) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchDashboardData = async () => {
    try {
      const dashboardData = await authService.getDashboardData();
      setData(dashboardData);
    } catch (error) {
      console.error('Erro ao buscar dados do dashboard:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useFocusEffect(
    React.useCallback(() => {
      fetchDashboardData();
    }, [])
  );

  const onRefresh = () => {
    setRefreshing(true);
    fetchDashboardData();
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#6a11cb" />
      </View>
    );
  }

  const SimulationItem = ({ item }: any) => (
    <TouchableOpacity 
      style={styles.simulationCard}
      onPress={() => navigation.navigate('SimulationDetail', { simulation: item })}
    >
      <View style={styles.simulationIcon}>
        <Ionicons name="document-text" size={24} color="#6a11cb" />
      </View>
      <View style={styles.simulationInfo}>
        <Text style={styles.simulationTitle}>{item.titulo}</Text>
        <Text style={styles.simulationDate}>
          {new Date(item.criado_em).toLocaleDateString('pt-BR')}
        </Text>
      </View>
      <Ionicons name="chevron-forward" size={20} color="#444" />
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView 
        contentContainerStyle={styles.scrollContent}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#6a11cb" />}
      >
        {/* HEADER PERFIL */}
        <View style={styles.header}>
          <View>
            <Text style={styles.welcomeText}>Olá, {data?.profile?.first_name || 'Usuário'}! 👋</Text>
            <Text style={styles.subtitleText}>Bem-vindo ao seu SIMULALAR</Text>
          </View>
          <TouchableOpacity 
            style={styles.avatarContainer}
            onPress={() => navigation.navigate('Profile')}
          >
            <Text style={styles.avatarText}>
              {(data?.profile?.first_name?.[0] || 'U').toUpperCase()}
            </Text>
          </TouchableOpacity>
        </View>

        {/* CARD DE PLANO */}
        <TouchableOpacity style={styles.planCard}>
          <View style={styles.planInfo}>
            <Text style={styles.planTitle}>Plano {data?.profile?.tipo_conta || 'FREE'}</Text>
            <Text style={styles.planStatus}>
              {data?.profile?.is_premium ? 'Assinatura Ativa ✅' : 'Versão Gratuita'}
            </Text>
          </View>
          {!data?.profile?.is_premium && (
            <TouchableOpacity style={styles.upgradeButton}>
              <Text style={styles.upgradeText}>Upgrade</Text>
            </TouchableOpacity>
          )}
        </TouchableOpacity>

        {/* ESTATÍSTICAS RÁPIDAS */}
        <View style={styles.statsRow}>
          <View style={styles.statBox}>
            <Text style={styles.statNumber}>{data?.total_simulations || 0}</Text>
            <Text style={styles.statLabel}>Simulações</Text>
          </View>
          <View style={styles.statBox}>
            <Text style={styles.statNumber}>0</Text>
            <Text style={styles.statLabel}>Favoritos</Text>
          </View>
        </View>

        {/* SIMULAÇÕES RECENTES */}
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Simulações Recentes</Text>
          <TouchableOpacity onPress={() => navigation.navigate('SavedSimulations')}>
            <Text style={styles.viewAllText}>Ver tudo</Text>
          </TouchableOpacity>
        </View>

        {data?.recent_simulations?.length > 0 ? (
          data.recent_simulations.map((sim: any) => (
            <SimulationItem key={sim.id} item={sim} />
          ))
        ) : (
          <View style={styles.emptyContainer}>
            <Ionicons name="analytics-outline" size={48} color="#222" />
            <Text style={styles.emptyText}>Nenhuma simulação ainda.</Text>
            <TouchableOpacity 
              style={styles.startWizardButton}
              onPress={() => navigation.navigate('Wizard')}
            >
              <Text style={styles.startWizardText}>Começar Agora</Text>
            </TouchableOpacity>
          </View>
        )}
      </ScrollView>

      {/* BOTÃO FLUTUANTE (NOVA SIMULAÇÃO) */}
      <TouchableOpacity 
        style={styles.fab} 
        onPress={() => navigation.navigate('Wizard')}
      >
        <Ionicons name="add" size={32} color="#fff" />
      </TouchableOpacity>
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
    backgroundColor: '#0f0c29',
    justifyContent: 'center',
    alignItems: 'center',
  },
  scrollContent: {
    padding: 20,
    paddingBottom: 100,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 30,
    marginTop: 10,
  },
  welcomeText: {
    color: '#fff',
    fontSize: 24,
    fontWeight: 'bold',
  },
  subtitleText: {
    color: '#aaa',
    fontSize: 14,
    marginTop: 4,
  },
  avatarContainer: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: '#6a11cb',
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 2,
    borderColor: 'rgba(255,255,255,0.1)',
  },
  avatarText: {
    color: '#fff',
    fontSize: 20,
    fontWeight: 'bold',
  },
  planCard: {
    backgroundColor: 'rgba(106, 17, 203, 0.15)',
    borderRadius: 16,
    padding: 20,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 25,
    borderWidth: 1,
    borderColor: 'rgba(106, 17, 203, 0.3)',
  },
  planInfo: {
    flex: 1,
  },
  planTitle: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  planStatus: {
    color: '#7f7fd5',
    fontSize: 13,
    marginTop: 4,
  },
  upgradeButton: {
    backgroundColor: '#FFD700',
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 8,
  },
  upgradeText: {
    color: '#000',
    fontSize: 13,
    fontWeight: 'bold',
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 30,
  },
  statBox: {
    width: '48%',
    backgroundColor: 'rgba(255,255,255,0.03)',
    borderRadius: 16,
    padding: 20,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.05)',
  },
  statNumber: {
    color: '#fff',
    fontSize: 24,
    fontWeight: 'bold',
  },
  statLabel: {
    color: '#888',
    fontSize: 12,
    marginTop: 4,
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
  viewAllText: {
    color: '#6a11cb',
    fontSize: 14,
  },
  simulationCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.03)',
    borderRadius: 16,
    padding: 15,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.05)',
  },
  simulationIcon: {
    width: 45,
    height: 45,
    borderRadius: 12,
    backgroundColor: 'rgba(106, 17, 203, 0.1)',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 15,
  },
  simulationInfo: {
    flex: 1,
  },
  simulationTitle: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  simulationDate: {
    color: '#666',
    fontSize: 12,
    marginTop: 4,
  },
  emptyContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 40,
  },
  emptyText: {
    color: '#444',
    fontSize: 16,
    marginTop: 15,
  },
  startWizardButton: {
    marginTop: 20,
    paddingHorizontal: 25,
    paddingVertical: 12,
    backgroundColor: 'rgba(106, 17, 203, 0.1)',
    borderRadius: 25,
    borderWidth: 1,
    borderColor: '#6a11cb',
  },
  startWizardText: {
    color: '#6a11cb',
    fontWeight: 'bold',
  },
  fab: {
    position: 'absolute',
    right: 20,
    bottom: 30,
    width: 65,
    height: 65,
    borderRadius: 32.5,
    backgroundColor: '#6a11cb',
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#6a11cb',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.5,
    shadowRadius: 10,
    elevation: 8,
  },
});
