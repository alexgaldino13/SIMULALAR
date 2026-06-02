import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';

interface SpecialistTipProps {
  text: string;
}

export const SpecialistTip: React.FC<SpecialistTipProps> = ({ text }) => {
  return (
    <View style={styles.container}>
      <View style={styles.gradient}>
        <View style={styles.header}>
          <View style={styles.iconCircle}>
            <Ionicons name="sparkles" size={16} color="#FFD700" />
          </View>
          <Text style={styles.title}>DICA DO ESPECIALISTA</Text>
        </View>
        <Text style={styles.text}>{text || ''}</Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginVertical: 20,
    borderRadius: 20,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: 'rgba(106, 17, 203, 0.3)',
  },
  gradient: {
    padding: 18,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  iconCircle: {
    width: 30, 
    height: 30,
    borderRadius: 15,
    backgroundColor: 'rgba(255, 215, 0, 0.15)',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 10,
  },
  title: {
    color: '#FFD700',
    fontSize: 11,
    fontWeight: '900',
    letterSpacing: 1.5,
  },
  text: {
    color: '#fff',
    fontSize: 14,
    lineHeight: 22,
    opacity: 0.8,
    fontStyle: 'italic',
  },
});
