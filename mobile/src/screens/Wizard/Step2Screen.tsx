import React, { useState } from 'react';
import { StyleSheet, Text, View, Alert, ScrollView } from 'react-native';
import { TextInputMask } from 'react-native-masked-text';
import { useSimulation } from '../../context/SimulationContext';
import { WizardStep } from '../../components/WizardStep';
import { SpecialistTip } from '../../components/SpecialistTip';
import { OptionCard } from '../../components/OptionCard';
import { HelpIcon } from '../../components/HelpIcon';

export default function Step2Screen({ navigation }: any) {
  const { data, updateData } = useSimulation();
  const [localData, setLocalData] = useState(data.trabalho_renda);

  const handleNext = () => {
    if (!localData.renda_familiar_bruta || localData.renda_familiar_bruta <= 0) {
      Alert.alert('Renda Necessária', 'Precisamos saber sua renda para calcular o limite que o banco libera para você. 🏦');
      return;
    }
    updateData('trabalho_renda', localData);
    navigation.navigate('Step3');
  };

  const CONTRACTS = [
    { value: 'clt', label: 'CLT (Carteira Assinada)', description: 'Usa FGTS e tem mais estabilidade' },
    { value: 'autonomo', label: 'Autônomo ou PJ', description: 'Profissional liberal ou MEI' },
    { value: 'empresario', label: 'Sócio de Empresa', description: 'Empresário ou pró-labore' },
    { value: 'aposentado', label: 'Aposentado/Pensionista', description: 'Renda fixa vitalícia' },
  ];

  return (
    <WizardStep
      currentStep={2}
      totalSteps={5}
      title="Sua Renda 💰"
      subtitle="Quanto mais transparente você for, mais precisa será nossa análise de crédito."
      onNext={handleNext}
      onBack={() => navigation.goBack()}
    >
      <ScrollView showsVerticalScrollIndicator={false}>
        <View style={styles.labelRow}>
          <Text style={styles.humanLabel}>Qual a renda total da sua casa?</Text>
          <HelpIcon
            title="Renda Familiar Bruta"
            description="É a soma do salário de todas as pessoas que vão participar da compra, antes dos descontos de impostos."
            example="Se você ganha R$ 4.000 e seu cônjuge R$ 3.000, sua renda total é R$ 7.000."
          />
        </View>
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
            value={localData.renda_familiar_bruta.toFixed(2).replace('.', ',')}
            includeRawValueInChangeText={true}
            onChangeText={(text, raw) => {
              setLocalData({ ...localData, renda_familiar_bruta: raw ? parseFloat(raw) : 0 });
            }}
          />
        </View>

        <Text style={styles.humanLabel}>Como você trabalha atualmente?</Text>
        {CONTRACTS.map((c) => (
          <OptionCard
            key={c.value}
            label={c.label}
            value={c.value}
            description={c.description}
            icon={c.value === 'clt' ? '✍️' : c.value === 'autonomo' ? '💼' : c.value === 'empresario' ? '🏢' : '🏦'}
            selected={localData.tipo_contrato === c.value}
            onSelect={(v) => setLocalData({ ...localData, tipo_contrato: v })}
          />
        ))}

        <OptionCard
          label="Sou Servidor Público"
          value="servidor"
          icon="🏛️"
          description="Estatutário ou concursado (taxas menores)"
          selected={localData.tipo_trabalho === 'servidor'}
          onSelect={(v) => setLocalData({ ...localData, tipo_trabalho: v })}
        />

        <SpecialistTip 
          text="Sabia? Bancos adoram funcionários públicos e CLT. Eles costumam oferecer as menores taxas de juros do mercado! 📉"
        />

        <View style={[styles.labelRow, { marginTop: 15 }]}>
          <Text style={styles.humanLabel}>Tem outras rendas extras?</Text>
          <HelpIcon
            title="Rendas Adicionais"
            description="Aqui entram aluguéis que você recebe, pensões, ou bônus recorrentes."
          />
        </View>
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
            value={localData.outras_rendas.toFixed(2).replace('.', ',')}
            includeRawValueInChangeText={true}
            onChangeText={(text, raw) => {
              setLocalData({ ...localData, outras_rendas: raw ? parseFloat(raw) : 0 });
            }}
          />
        </View>
      </ScrollView>
    </WizardStep>
  );
}

const styles = StyleSheet.create({
  labelRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
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
    borderWidth: 1.5,
    borderColor: 'rgba(255,255,255,0.1)',
    height: 62,
    paddingHorizontal: 20,
    marginBottom: 25,
  },
  input: {
    flex: 1,
    color: '#fff',
    fontSize: 20,
    fontWeight: '700',
  },
});
