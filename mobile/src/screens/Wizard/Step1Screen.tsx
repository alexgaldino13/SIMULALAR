import React, { useState } from 'react';
import { StyleSheet, Text, View, TextInput, Alert, ScrollView, TouchableOpacity } from 'react-native';
import { useSimulation } from '../../context/SimulationContext';
import { WizardStep } from '../../components/WizardStep';
import { SpecialistTip } from '../../components/SpecialistTip';
import { OptionCard } from '../../components/OptionCard';
import { HelpIcon } from '../../components/HelpIcon';
import apiClient from '../../api/client';

export default function Step1Screen({ navigation }: any) {
  const { data, updateData } = useSimulation();
  const [localData, setLocalData] = useState(data.perfil_objetivos);

  const handleNext = () => {
    if (!localData.idade_comprador || localData.idade_comprador < 18) {
      Alert.alert('Quase lá!', 'Você precisa ter pelo menos 18 anos para realizar uma simulação habitacional. 🔞');
      return;
    }
    updateData('perfil_objetivos', localData);
    navigation.navigate('Step2');
  };

  const testConnection = async () => {
    try {
      const response = await apiClient.get('/api/v1/wizard/calculate/');
      Alert.alert('Conexão OK! ✅', response.data.message);
    } catch (error: any) {
      Alert.alert('Erro de Conexão ❌', 'O App não achou o servidor no IP 192.168.0.15. Verifique o Firewall do Windows.');
    }
  };

  const PROFILES = [
    { value: 'comprador_morar', label: 'Quero Morar', icon: '🏠', description: 'Busco minha casa própria' },
    { value: 'investidor', label: 'Quero Investir', icon: '📈', description: 'Foco em aluguel ou revenda' },
    { value: 'corretor', label: 'Sou Corretor', icon: '🤝', description: 'Simular para meus clientes' },
    { value: 'explorando', label: 'Estou Curioso', icon: '🔍', description: 'Apenas vendo as opções' },
  ];

  const PRIORITIES = [
    { value: 'pagar_menos', label: 'Pagar Menos Juros', icon: '💰', description: 'Economia total no contrato' },
    { value: 'parcelas_suaves', label: 'Parcelas Baixas', icon: '📉', description: 'Prestações leves todo mês' },
    { value: 'quitar_rapido', label: 'Quitar no Menor Prazo', icon: '⏱️', description: 'Acabar com a dívida logo' },
    { value: 'equilibrio', label: 'Custo-Benefício', icon: '⚖️', description: 'Equilíbrio entre taxa e prazo' },
  ];

  return (
    <WizardStep
      currentStep={1}
      totalSteps={5}
      title="Bem-vindo! 👋"
      subtitle="Vamos começar entendendo quem você é e o que busca hoje."
      onNext={handleNext}
      onBack={() => {}}
      hideBack={true}
    >
      <ScrollView showsVerticalScrollIndicator={false}>
        <TouchableOpacity onPress={testConnection} style={{ marginBottom: 25, padding: 10, borderRadius: 10, backgroundColor: 'rgba(106, 17, 203, 0.1)' }}>
          <Text style={{ color: '#6a11cb', textAlign: 'center', textDecorationLine: 'underline', fontWeight: 'bold' }}>
            📡 Testar conexão com o servidor
          </Text>
        </TouchableOpacity>

        <View style={styles.labelRow}>
          <Text style={styles.humanLabel}>Qual o seu objetivo principal?</Text>
        </View>
        {PROFILES.map((p) => (
          <OptionCard
            key={p.value}
            label={p.label}
            value={p.value}
            icon={p.icon}
            description={p.description}
            selected={localData.perfil_usuario === p.value}
            onSelect={(v) => setLocalData({ ...localData, perfil_usuario: v })}
          />
        ))}

        <SpecialistTip
          text="Dica: Compradores e Investidores têm caminhos diferentes. Saber seu perfil ajuda nossa IA a escolher o melhor banco para você! 🤖"
        />

        <View style={[styles.labelRow, { marginTop: 15 }]}>
          <Text style={styles.humanLabel}>O que é mais importante para você?</Text>
        </View>
        {PRIORITIES.map((p) => (
          <OptionCard
            key={p.value}
            label={p.label}
            value={p.value}
            icon={p.icon}
            description={p.description}
            selected={localData.prioridade_principal === p.value}
            onSelect={(v) => setLocalData({ ...localData, prioridade_principal: v })}
          />
        ))}

        <View style={[styles.labelRow, { marginTop: 15 }]}>
          <Text style={styles.humanLabel}>Quantos anos você tem?</Text>
          <HelpIcon
            title="Por que a idade?"
            description="A idade influencia no valor do seguro obrigatório (MIP) e no prazo máximo que o banco libera para você."
          />
        </View>
        <View style={styles.inputContainer}>
          <TextInput
            style={styles.input}
            value={String(localData.idade_comprador || '')}
            onChangeText={(v) => {
                const numeric = v.replace(/[^0-9]/g, '');
                setLocalData({ ...localData, idade_comprador: numeric ? parseInt(numeric) : 0 });
            }}
            placeholder="Ex: 30"
            placeholderTextColor="#555"
            keyboardType="numeric"
          />
          <Text style={styles.inputSuffix}>anos</Text>
        </View>
      </ScrollView>
    </WizardStep>
  );
}

const styles = StyleSheet.create({
  labelRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
    marginLeft: 5,
  },
  humanLabel: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 18,
    paddingHorizontal: 20,
    height: 62,
    borderWidth: 1.5,
    borderColor: 'rgba(255,255,255,0.1)',
    marginBottom: 20,
  },
  input: {
    flex: 1,
    color: '#fff',
    fontSize: 18,
    fontWeight: '700',
  },
  inputSuffix: {
    color: '#6a11cb',
    fontSize: 14,
    fontWeight: '900',
    marginLeft: 10,
    textTransform: 'uppercase',
  },
});
