import React, { useState } from 'react';
import {
  StyleSheet,
  TouchableOpacity,
  Text,
  View,
  Modal,
  TouchableWithoutFeedback
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface HelpIconProps {
  title: string;
  description: string;
  example?: string;
}

export const HelpIcon: React.FC<HelpIconProps> = ({ title, description, example }) => {
  return null; // Desativado para teste de estabilidade
};

const styles = StyleSheet.create({
  button: {
    marginLeft: 8,
  },
  modalOverlay: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0,0,0,0.8)',
    padding: 25,
  },
  modalContent: {
    width: '100%',
    backgroundColor: '#1e1b4b',
    borderRadius: 25,
    padding: 25,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
    elevation: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.5,
    shadowRadius: 20,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  title: {
    color: '#fff',
    fontSize: 20,
    fontWeight: 'bold',
  },
  description: {
    color: 'rgba(255,255,255,0.7)',
    fontSize: 16,
    lineHeight: 24,
    marginBottom: 20,
  },
  exampleContainer: {
    backgroundColor: 'rgba(106, 17, 203, 0.1)',
    padding: 15,
    borderRadius: 15,
    marginBottom: 25,
    borderLeftWidth: 4,
    borderLeftColor: '#6a11cb',
  },
  exampleTitle: {
    color: '#6a11cb',
    fontSize: 12,
    fontWeight: '900',
    marginBottom: 5,
  },
  exampleText: {
    color: '#fff',
    fontSize: 14,
    fontStyle: 'italic',
  },
  closeButton: {
    backgroundColor: '#6a11cb',
    height: 50,
    borderRadius: 15,
    alignItems: 'center',
    justifyContent: 'center',
  },
  closeButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
