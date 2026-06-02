import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity, SafeAreaView, ActivityIndicator, Alert, Image } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import apiClient from '../api/client';

import { setAuthToken } from '../api/client';

export default function ProfileScreen({ navigation }: any) {
  const [profile, setProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const fetchProfile = async () => {
    try {
      const response = await apiClient.get('/api/v1/dashboard/');
      setProfile(response.data.profile);
    } catch (error: any) {
      console.error('Erro ao buscar perfil:', error);
      if (error.response?.status === 401) {
        setAuthToken(null);
        navigation.replace('Auth');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProfile();
  }, []);

  const handleLogout = () => {
    Alert.alert(
      'Encerrar Sessão',
      'Deseja realmente sair da sua conta no SIMULALAR?',
      [
        { text: 'Cancelar', style: 'cancel' },
        { 
          text: 'Sair com Segurança', 
          style: 'destructive',
          onPress: () => {
            setAuthToken(null);
            navigation.replace('Auth');
          }
        }
      ]
    );
  };

  const InfoCard = ({ icon, label, value, color = '#6a11cb' }: any) => (
    <View style={styles.infoCard}>
      <View style={[styles.infoIconCircle, { backgroundColor: `${color}20` }]}>
        <Ionicons name={icon} size={18} color={color} />
      </View>
      <View style={styles.infoTextContainer}>
        <Text style={styles.infoLabel}>{label}</Text>
        <Text style={styles.infoValue}>{value || 'Não informado'}</Text>
      </View>
    </View>
  );

  if (loading) {
    return (
      <LinearGradient colors={['#0f0c29', '#302b63', '#24243e']} style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#FFD700" />
      </LinearGradient>
    );
  }

  const isPremium = profile?.is_premium;
  const isBroker = !!profile?.creci;

  return (
    <SafeAreaView style={styles.container}>
      <LinearGradient colors={['#0f0c29', '#302b63', '#24243e']} style={StyleSheet.absoluteFill} />
      
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
          <Ionicons name="chevron-back" size={28} color="#fff" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Minha Conta</Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
        {/* Profile Identity Section */}
        <View style={styles.avatarContainer}>
          <View style={styles.orbitalGlow}>
            <LinearGradient 
              colors={['#6a11cb', '#2575fc']} 
              style={styles.avatarBig}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 1 }}
            >
              {profile?.avatar ? (
                <Image source={{ uri: profile.avatar }} style={styles.avatarImage} />
              ) : (
                <Text style={styles.avatarTextBig}>
                  {(profile?.first_name?.[0] || 'U').toUpperCase()}
                </Text>
              )}
            </LinearGradient>
          </View>
          
          <Text style={styles.userName}>{profile?.first_name || 'Usuário'}</Text>
          <View style={[styles.badge, isPremium ? styles.premiumBadge : styles.freeBadge]}>
            <Ionicons name={isPremium ? "star" : "person"} size={12} color="#fff" />
            <Text style={styles.badgeText}>PLANO {isPremium ? 'PREMIUM' : 'FREE'}</Text>
          </View>
        </View>

        {/* Info Groups */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Dados Pessoais</Text>
          <View style={styles.glassGroup}>
            <InfoCard icon="mail-outline" label="E-mail de Acesso" value={profile?.email} />
            <View style={styles.divider} />
            <InfoCard icon="phone-portrait-outline" label="Telefone" value={profile?.telefone} />
          </View>
        </View>

        {isBroker && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Identidade Profissional</Text>
            <View style={[styles.glassGroup, { borderColor: 'rgba(255, 215, 0, 0.3)' }]}>
              <InfoCard icon="business-outline" label="Imobiliária / Empresa" value={profile?.nome_empresa} color="#FFD700" />
              <View style={styles.divider} />
              <InfoCard icon="ribbon-outline" label="Registro CRECI" value={profile?.creci} color="#FFD700" />
            </View>
          </View>
        )}

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Preferências & Segurança</Text>
          <View style={styles.glassGroup}>
            <TouchableOpacity style={styles.menuItem}>
              <View style={styles.menuItemLeft}>
                <Ionicons name="notifications-outline" size={20} color="#fff" />
                <Text style={styles.menuItemText}>Notificações</Text>
              </View>
              <Ionicons name="chevron-forward" size={18} color="#444" />
            </TouchableOpacity>
            
            <View style={styles.divider} />
            
            <TouchableOpacity style={styles.menuItem}>
              <View style={styles.menuItemLeft}>
                <Ionicons name="lock-closed-outline" size={20} color="#fff" />
                <Text style={styles.menuItemText}>Privacidade e Dados</Text>
              </View>
              <Ionicons name="chevron-forward" size={18} color="#444" />
            </TouchableOpacity>
          </View>
        </View>

        {!isPremium && (
          <TouchableOpacity style={styles.premiumCTA}>
            <LinearGradient colors={['#FFD700', '#FFA500']} style={styles.ctaGradient}>
              <Ionicons name="flash-outline" size={20} color="#24243e" />
              <Text style={styles.ctaText}>Seja Premium: PDF White-label e muito mais</Text>
            </LinearGradient>
          </TouchableOpacity>
        )}

        <TouchableOpacity 
          style={styles.logoutButton}
          onPress={handleLogout}
        >
          <Ionicons name="power-outline" size={20} color="#ff4444" />
          <Text style={styles.logoutText}>Encerrar Sessão</Text>
        </TouchableOpacity>

        <Text style={styles.versionText}>SIMULALAR v1.0.0 • 2026</Text>
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
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 15,
  },
  backButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(255,255,255,0.05)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  headerTitle: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '900',
    letterSpacing: 1,
  },
  scrollContent: {
    padding: 20,
    paddingBottom: 40,
  },
  avatarContainer: {
    alignItems: 'center',
    marginVertical: 35,
  },
  orbitalGlow: {
    padding: 6,
    borderRadius: 60,
    backgroundColor: 'rgba(106, 17, 203, 0.1)',
    borderWidth: 1,
    borderColor: 'rgba(106, 17, 203, 0.3)',
    shadowColor: '#6a11cb',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.5,
    shadowRadius: 20,
  },
  avatarBig: {
    width: 100,
    height: 100,
    borderRadius: 50,
    alignItems: 'center',
    justifyContent: 'center',
  },
  avatarImage: {
    width: 100,
    height: 100,
    borderRadius: 50,
  },
  avatarTextBig: {
    color: '#fff',
    fontSize: 42,
    fontWeight: 'bold',
  },
  userName: {
    color: '#fff',
    fontSize: 26,
    fontWeight: 'bold',
    marginTop: 15,
  },
  badge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 50,
    marginTop: 8,
  },
  premiumBadge: {
    backgroundColor: '#FFD70030',
    borderWidth: 1,
    borderColor: '#FFD700',
  },
  freeBadge: {
    backgroundColor: 'rgba(255,255,255,0.1)',
  },
  badgeText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: 'bold',
    marginLeft: 5,
    letterSpacing: 1,
  },
  section: {
    marginBottom: 25,
  },
  sectionTitle: {
    color: 'rgba(255,255,255,0.4)',
    fontSize: 12,
    fontWeight: '900',
    letterSpacing: 1,
    textTransform: 'uppercase',
    marginBottom: 12,
    marginLeft: 5,
  },
  glassGroup: {
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    borderRadius: 24,
    padding: 5,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.08)',
  },
  infoCard: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 15,
  },
  infoIconCircle: {
    width: 38,
    height: 38,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
  },
  infoTextContainer: {
    flex: 1,
  },
  infoLabel: {
    color: 'rgba(255,255,255,0.4)',
    fontSize: 11,
    textTransform: 'uppercase',
    fontWeight: 'bold',
  },
  infoValue: {
    color: '#fff',
    fontSize: 15,
    fontWeight: '600',
    marginTop: 2,
  },
  divider: {
    height: 1,
    backgroundColor: 'rgba(255,255,255,0.05)',
    marginHorizontal: 15,
  },
  menuItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 18,
  },
  menuItemLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  menuItemText: {
    color: '#fff',
    fontSize: 16,
  },
  premiumCTA: {
    borderRadius: 18,
    overflow: 'hidden',
    marginTop: 10,
    marginBottom: 20,
  },
  ctaGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 18,
    gap: 12,
  },
  ctaText: {
    color: '#24243e',
    fontWeight: 'bold',
    fontSize: 14,
  },
  logoutButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 20,
    gap: 10,
    marginTop: 10,
  },
  logoutText: {
    color: '#ff4444',
    fontSize: 15,
    fontWeight: 'bold',
  },
  versionText: {
    color: 'rgba(255,255,255,0.1)',
    fontSize: 12,
    fontWeight: 'bold',
    textAlign: 'center',
    marginTop: 30,
    letterSpacing: 1,
  },
});
