import { useState } from 'react';
import { StyleSheet, Text, View, Alert, ScrollView } from 'react-native';
import { TextInputMask } from 'react-native-masked-text';
import { useSimulation } from '../../context/SimulationContext';
import { WizardStep } from '../../components/WizardStep';
import { SpecialistTip } from '../../components/SpecialistTip';


export default function Step3Screen({ navigation }: any) {
  const { data, updateData } = useSimulation();
  const [localData, setLocalData] = useState(data.financas_atuais);

  const handleNext = () => {
    updateData('financas_atuais', localData);
    navigation.navigate('Step4');
  };

  return (
    <WizardStep
      currentStep={3}
      totalSteps={5}
      title="Finanças Atuais"
      subtitle="O que você já tem conquistado até agora"
      onNext={handleNext}
      onBack={() => navigation.goBack()}
    >
      <ScrollView>
        <Text style={styles.label}>Quanto você tem guardado?</Text>
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
            value={localData.saldo_dinheiro_guardado.toString()}
            includeRawValueInChangeText={true}
            onChangeText={(text, raw) => {
              setLocalData({ ...localData, saldo_dinheiro_guardado: raw ? parseFloat(raw) : 0 });
            }}
          />
        </View>

        <Text style={styles.label}>Saldo de FGTS disponível</Text>
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
            value={localData.saldo_fgts.toString()}
            includeRawValueInChangeText={true}
            onChangeText={(text, raw) => {
              setLocalData({ ...localData, saldo_fgts: raw ? parseFloat(raw) : 0 });
            }}
          />
        </View>

        <Text style={styles.label}>Valor do seu imóvel próprio (se tiver)</Text>
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
            value={localData.valor_imovel_proprio.toString()}
            includeRawValueInChangeText={true}
            onChangeText={(text, raw) => {
              setLocalData({ ...localData, valor_imovel_proprio: raw ? parseFloat(raw) : 0 });
            }}
          />
        </View>

        <Text style={styles.label}>Outras despesas mensais (Fixas)</Text>
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
            value={localData.despesas_mensais_fixas.toString()}
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
