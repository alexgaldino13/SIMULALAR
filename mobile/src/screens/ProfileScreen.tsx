import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity, SafeAreaView, ActivityIndicator, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import apiClient from '../api/client';
import { authService } from '../api/authService';

export default function ProfileScreen({ navigation }: any) {
  const [profile, setProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const fetchProfile = async () => {
    try {
      const response = await apiClient.get('/api/v1/dashboard/');
      setProfile(response.data.profile);
    } catch (error) {
      console.error('Erro ao buscar perfil:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProfile();
  }, []);

  const handleLogout = () => {
    Alert.alert(
      'Sair',
      'Deseja realmente sair da sua conta?',
      [
        { text: 'Cancelar', style: 'cancel' },
        { 
          text: 'Sair', 
          onPress: () => {
            // No mobile, apenas voltamos para a tela de Login e limpamos o estado se necessário
            // Idealmente limparíamos o token do storage aqui.
            navigation.replace('Auth');
          }
        }
      ]
    );
  };

  if (loading) {
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
        <Text style={styles.headerTitle}>Meu Perfil</Text>
        <View style={{ width: 24 }} />
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.avatarSection}>
          <View style={styles.avatarBig}>
            <Text style={styles.avatarTextBig}>
              {(profile?.first_name?.[0] || 'U').toUpperCase()}
            </Text>
          </View>
          <Text style={styles.userName}>{profile?.first_name || 'Usuário'}</Text>
          <Text style={styles.userEmail}>{profile?.email || 'email@exemplo.com'}</Text>
        </View>

        <View style={styles.infoSection}>
          <View style={styles.infoRow}>
            <View style={styles.infoIcon}>
              <Ionicons name="card-outline" size={20} color="#6a11cb" />
            </View>
            <View style={styles.infoText}>
              <Text style={styles.infoLabel}>Plano Atual</Text>
              <Text style={styles.infoValue}>
                Plano {profile?.tipo_conta || 'FREE'} {profile?.is_premium ? '✅' : ''}
              </Text>
            </View>
          </View>

          <View style={styles.divider} />

          <View style={styles.infoRow}>
            <View style={styles.infoIcon}>
              <Ionicons name="shield-checkmark-outline" size={20} color="#6a11cb" />
            </View>
            <View style={styles.infoText}>
              <Text style={styles.infoLabel}>Privacidade</Text>
              <Text style={styles.infoValue}>Dados protegidos (LGPD)</Text>
            </View>
          </View>
        </View>

        <TouchableOpacity 
          style={styles.logoutButton}
          onPress={handleLogout}
        >
          <Ionicons name="log-out-outline" size={20} color="#ff4444" style={{ marginRight: 10 }} />
          <Text style={styles.logoutText}>Sair da Conta</Text>
        </TouchableOpacity>

        <Text style={styles.versionText}>ImobCalc v1.0.0</Text>
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
  scrollContent: {
    padding: 20,
    alignItems: 'center',
  },
  avatarSection: {
    alignItems: 'center',
    marginVertical: 40,
  },
  avatarBig: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: '#6a11cb',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 20,
    borderWidth: 3,
    borderColor: 'rgba(255,255,255,0.1)',
  },
  avatarTextBig: {
    color: '#fff',
    fontSize: 40,
    fontWeight: 'bold',
  },
  userName: {
    color: '#fff',
    fontSize: 24,
    fontWeight: 'bold',
  },
  userEmail: {
    color: '#666',
    fontSize: 16,
    marginTop: 5,
  },
  infoSection: {
    width: '100%',
    backgroundColor: 'rgba(255,255,255,0.03)',
    borderRadius: 20,
    padding: 20,
    marginBottom: 40,
  },
  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  infoIcon: {
    width: 40,
    height: 40,
    borderRadius: 10,
    backgroundColor: 'rgba(106, 17, 203, 0.1)',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 15,
  },
  infoText: {
    flex: 1,
  },
  infoLabel: {
    color: '#888',
    fontSize: 12,
  },
  infoValue: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
    marginTop: 2,
  },
  divider: {
    height: 1,
    backgroundColor: 'rgba(255,255,255,0.05)',
    marginVertical: 15,
  },
  logoutButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 15,
  },
  logoutText: {
    color: '#ff4444',
    fontSize: 16,
    fontWeight: 'bold',
  },
  versionText: {
    color: '#333',
    fontSize: 12,
    marginTop: 40,
  },
});
