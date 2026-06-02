import React, { useState } from 'react';
import { StyleSheet, Text, View, Alert, ScrollView } from 'react-native';
import { TextInputMask } from 'react-native-masked-text';
import { useSimulation } from '../../context/SimulationContext';
import { WizardStep } from '../../components/WizardStep';
import { SpecialistTip } from '../../components/SpecialistTip';
import { HelpIcon } from '../../components/HelpIcon';

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
      title="Suas Reservas 🏦"
      subtitle="O que você já conquistou até aqui conta muito para o banco."
      onNext={handleNext}
      onBack={() => navigation.goBack()}
    >
      <ScrollView showsVerticalScrollIndicator={false}>
        <View style={styles.labelRow}>
          <Text style={styles.humanLabel}>Quanto você tem guardado hoje?</Text>
          <HelpIcon
            title="Capital Próprio"
            description="Dinheiro em poupança, investimentos ou conta corrente para usar como entrada."
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
            value={localData.saldo_dinheiro_guardado.toFixed(2).replace('.', ',')}
            includeRawValueInChangeText={true}
            onChangeText={(text, raw) => {
              setLocalData({ ...localData, saldo_dinheiro_guardado: raw ? parseFloat(raw) : 0 });
            }}
          />
        </View>

        <View style={styles.labelRow}>
          <Text style={styles.humanLabel}>Qual o seu saldo de FGTS?</Text>
          <HelpIcon
            title="Uso do FGTS"
            description="O FGTS pode ser usado para abater a entrada ou amortizar parcelas."
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
            value={localData.saldo_fgts.toFixed(2).replace('.', ',')}
            includeRawValueInChangeText={true}
            onChangeText={(text, raw) => {
              setLocalData({ ...localData, saldo_fgts: raw ? parseFloat(raw) : 0 });
            }}
          />
        </View>

        <View style={styles.labelRow}>
          <Text style={styles.humanLabel}>Valor do imóvel atual (se tiver)</Text>
          <HelpIcon
            title="Imóvel Próprio"
            description="Se pretende vender seu imóvel atual para comprar o novo, informe o valor dele."
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
            value={localData.valor_imovel_proprio.toFixed(2).replace('.', ',')}
            includeRawValueInChangeText={true}
            onChangeText={(text, raw) => {
              setLocalData({ ...localData, valor_imovel_proprio: raw ? parseFloat(raw) : 0 });
            }}
          />
        </View>

        <SpecialistTip
          text="Ter um imóvel próprio aumenta muito seu score no banco, mesmo que você não pretenda vendê-lo agora! 📈"
        />

        <View style={[styles.labelRow, { marginTop: 10 }]}>
          <Text style={styles.humanLabel}>Outras despesas mensais (Fixas)</Text>
          <HelpIcon
            title="Comprometimento de Renda"
            description="Parcelas de carro, cartão ou outros empréstimos que reduzem sua capacidade de pagar a casa."
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
            value={localData.despesas_mensais_fixas.toFixed(2).replace('.', ',')}
            includeRawValueInChangeText={true}
            onChangeText={(text, raw) => {
              setLocalData({ ...localData, despesas_mensais_fixas: raw ? parseFloat(raw) : 0 });
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
