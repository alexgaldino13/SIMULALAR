import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, FlatList, TouchableOpacity, SafeAreaView, ActivityIndicator, RefreshControl } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { authService } from '../api/authService';
import apiClient from '../api/client';

export default function SavedSimulationsScreen({ navigation }: any) {
  const [simulations, setSimulations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchAllSimulations = async () => {
    try {
      const response = await apiClient.get('/api/v1/simulations/');
      setSimulations(response.data.simulations);
    } catch (error) {
      console.error('Erro ao buscar simulações:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchAllSimulations();
  }, []);

  const onRefresh = () => {
    setRefreshing(true);
    fetchAllSimulations();
  };

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

  if (loading && !refreshing) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#6a11cb" />
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color="#fff" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Minhas Simulações</Text>
        <View style={{ width: 24 }} />
      </View>

      <FlatList
        data={simulations}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item }) => <SimulationItem item={item} />}
        contentContainerStyle={styles.listContent}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#6a11cb" />
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Ionicons name="analytics-outline" size={64} color="#333" />
            <Text style={styles.emptyText}>Você ainda não salvou simulações.</Text>
          </View>
        }
      />
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
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 15,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,255,255,0.05)',
  },
  backButton: {
    padding: 5,
  },
  headerTitle: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  listContent: {
    padding: 20,
    paddingBottom: 40,
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
    marginTop: 100,
  },
  emptyText: {
    color: '#666',
    fontSize: 16,
    marginTop: 20,
    textAlign: 'center',
  },
});
