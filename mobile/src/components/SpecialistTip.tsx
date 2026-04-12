import React from 'react';
import { StyleSheet, Text, View } from 'react-native';

interface SpecialistTipProps {
  text: string;
}

export const SpecialistTip: React.FC<SpecialistTipProps> = ({ text }) => {
  return (
    <View style={styles.container}>
      <View style={styles.iconContainer}>
        <Text style={styles.icon}>💡</Text>
      </View>
      <View style={styles.textContainer}>
        <Text style={styles.title}>Visão do Especialista</Text>
        <Text style={styles.text}>{text}</Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    backgroundColor: 'rgba(106, 17, 203, 0.08)',
    borderRadius: 14,
    padding: 18,
    marginTop: 25,
    marginBottom: 10,
    borderLeftWidth: 4,
    borderLeftColor: '#6a11cb',
  },
  iconContainer: {
    marginRight: 15,
  },
  icon: {
    fontSize: 24,
  },
  textContainer: {
    flex: 1,
  },
  title: {
    color: '#a29bfe',
    fontSize: 14,
    fontWeight: '800',
    marginBottom: 4,
    textTransform: 'uppercase',
    letterSpacing: 1,
  },
  text: {
    color: '#ddd',
    fontSize: 13,
    lineHeight: 18,
  },
});
