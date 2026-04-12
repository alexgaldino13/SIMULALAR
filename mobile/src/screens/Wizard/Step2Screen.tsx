import React, { useState } from 'react';
import { StyleSheet, Text, View, Alert, ScrollView } from 'react-native';
import { TextInputMask } from 'react-native-masked-text';
import { useSimulation } from '../../context/SimulationContext';
import { WizardStep } from '../../components/WizardStep';
import { SpecialistTip } from '../../components/SpecialistTip';
import { OptionCard } from '../../components/OptionCard';

import { currencyToNumber } from '../../utils/formatters';

export default function Step2Screen({ navigation }: any) {
  const { data, updateData } = useSimulation();
  const [localData, setLocalData] = useState(data.trabalho_renda);

  const handleNext = () => {
    if (!localData.renda_familiar_bruta || localData.renda_familiar_bruta <= 0) {
      Alert.alert('Campo Obrigatório', 'Por favor, informe a renda familiar bruta para calcularmos sua capacidade de crédito.');
      return;
    }
    updateData('trabalho_renda', localData);
    navigation.navigate('Step3');
  };

  const CONTRACTS = [
    { value: 'clt', label: 'CLT', description: 'Carteira assinada + FGTS' },
    { value: 'autonomo', label: 'Autônomo / PJ', description: 'Profissional liberal' },
    { value: 'empresario', label: 'Empresário', description: 'Dono de empresa' },
    { value: 'aposentado', label: 'Aposentado', description: 'Renda fixa INSS/Prev' },
  ];

  return (
    <WizardStep
      currentStep={2}
      totalSteps={5}
      title="Trabalho & Renda"
      subtitle="Sua base financeira para o financiamento"
      onNext={handleNext}
      onBack={() => navigation.goBack()}
    >
      <ScrollView>
        <Text style={styles.label}>Renda Familiar Bruta (Mensal)</Text>
        <View style={styles.inputContainer}>
          <TextInputMask
            type={'money'}
            options={{
              precision: 2,
              separator: ',',
              delimiter: '.',
              unit: 'R$ ',
              suffixUnit: ''
            }}
            style={styles.input}
            placeholder="R$ 0,00"
            placeholderTextColor="#555"
            value={localData.renda_familiar_bruta.toString()}
            includeRawValueInChangeText={true}
            onChangeText={(text, raw) => {
              setLocalData({ ...localData, renda_familiar_bruta: raw ? parseFloat(raw) : 0 });
            }}
          />
        </View>

        <Text style={[styles.sectionTitle, { marginTop: 10 }]}>Tipo de Contrato</Text>
        {CONTRACTS.map((c) => (
          <OptionCard
            key={c.value}
            label={c.label}
            value={c.value}
            description={c.description}
            selected={localData.tipo_contrato === c.value}
            onSelect={(v) => setLocalData({ ...localData, tipo_contrato: v })}
          />
        ))}

        <OptionCard
          title="Sou Servidor Público"
          icon="🏛️"
          selected={localData.tipo_trabalho === 'servidor'}
          onSelect={() => setLocalData({ ...localData, tipo_trabalho: 'servidor' })}
        />

        <SpecialistTip 
          text="Sua renda formal (CLT/Servidor) é o que o banco mais valoriza. Sabia que outras rendas podem ter um 'desconto' de até 25% na análise de crédito bancária?"
        />

        <Text style={[styles.label, { marginTop: 25 }]}>Outras Rendas (Aluguéis, Pensão, etc.)</Text>
        <View style={styles.inputContainer}>
          <TextInputMask
            type={'money'}
            options={{
              precision: 2,
              separator: ',',
              delimiter: '.',
              unit: 'R$ ',
              suffixUnit: ''
            }}
            style={styles.input}
            placeholder="R$ 0,00"
            placeholderTextColor="#555"
            value={localData.outras_rendas.toString()}
            includeRawValueInChangeText={true}
            onChangeText={(text, raw) => {
              setLocalData({ ...localData, despesas_mensais_fixas: raw ? parseFloat(raw) : 0 });
            }}
          />
        </View>

        <SpecialistTip 
          text="O capital que você já tem é o que define o seu poder de negociação. Se você já tem um imóvel, ele pode ser a chave para um 'upgrade' estratégico."
        />
      </ScrollView>
    </WizardStep>
  );
}

const styles = StyleSheet.create({
  label: {
    color: '#aaa',
    fontSize: 14,
    marginBottom: 10,
    fontWeight: '600',
  },
  sectionTitle: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
    marginVertical: 15,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 14,
    borderWidth: 1.5,
    borderColor: 'rgba(255,255,255,0.1)',
    height: 60,
    paddingHorizontal: 20,
    marginBottom: 20,
  },
  input: {
    flex: 1,
    color: '#fff',
    fontSize: 20,
    fontWeight: '700',
  },
});
