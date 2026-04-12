import React, { useState } from 'react';
import { StyleSheet, Text, View, TextInput, Alert, ScrollView } from 'react-native';
import { useSimulation } from '../../context/SimulationContext';
import { WizardStep } from '../../components/WizardStep';
import { SpecialistTip } from '../../components/SpecialistTip';
import { OptionCard } from '../../components/OptionCard';


export default function Step1Screen({ navigation }: any) {
  const { data, updateData } = useSimulation();
  const [localData, setLocalData] = useState(data.perfil_objetivos);

  const handleNext = () => {
    updateData('perfil_objetivos', localData);
    navigation.navigate('Step2');
  };

  const PROFILES = [
    { value: 'comprador_morar', label: 'Comprador', icon: '🏠', description: 'Quero morar no imóvel' },
    { value: 'investidor', label: 'Investidor', icon: '💼', description: 'Quero alugar ou revender' },
    { value: 'corretor', label: 'Corretor', icon: '🏢', description: 'Orientar meus clientes' },
    { value: 'explorando', label: 'Explorador', icon: '📊', description: 'Só vendo possibilidades' },
  ];

  const PRIORITIES = [
    { value: 'pagar_menos', label: 'Economia Máxima', icon: '💰', description: 'Pagar o menor valor total' },
    { value: 'parcelas_suaves', label: 'Parcelas Baixas', icon: '📉', description: 'Prestações que cabem no bolso' },
    { value: 'quitar_rapido', label: 'Quitar Rápido', icon: '⏱️', description: 'Menor prazo possível' },
    { value: 'equilibrio', label: 'Equilíbrio', icon: '⚖️', description: 'Bom custo-benefício geral' },
  ];

  return (
    <WizardStep
      currentStep={1}
      totalSteps={5}
      title="Perfil & Objetivos"
      subtitle="Quem é você e o que é mais importante nessa conquista?"
      onNext={handleNext}
      onBack={() => {}}
      hideBack={true}
    >
      <Text style={styles.sectionTitle}>Qual o seu perfil?</Text>
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
        text="Definir bem o seu perfil é o primeiro passo para economizar milhares de reais. Compradores e investidores têm métricas de sucesso completamente diferentes."
      />

      <Text style={[styles.sectionTitle, { marginTop: 20 }]}>Sua prioridade principal?</Text>
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

      <Text style={[styles.sectionTitle, { marginTop: 20 }]}>Qual a sua idade?</Text>
      <View style={styles.inputContainer}>
        <TextInput
          style={styles.input}
          value={localData.idade_comprador?.toString()}
          onChangeText={(v) => setLocalData({ ...localData, idade_comprador: parseInt(v) || 0 })}
          placeholder="Ex: 30"
          placeholderTextColor="#999"
          keyboardType="numeric"
        />
        <Text style={styles.inputSuffix}>anos</Text>
      </View>
    </WizardStep>
  );
}

const styles = StyleSheet.create({
  sectionTitle: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 15,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 12,
    paddingHorizontal: 15,
    height: 56,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
  },
  input: {
    flex: 1,
    color: '#fff',
    fontSize: 18,
    fontWeight: '600',
  },
  inputSuffix: {
    color: '#6a11cb',
    fontSize: 16,
    fontWeight: 'bold',
    marginLeft: 10,
  },
});
