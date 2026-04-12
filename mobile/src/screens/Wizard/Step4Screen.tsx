import React, { useState } from 'react';
import { StyleSheet, Text, View, Alert } from 'react-native';
import { TextInputMask } from 'react-native-masked-text';
import { useSimulation } from '../../context/SimulationContext';
import { WizardStep } from '../../components/WizardStep';
import { SpecialistTip } from '../../components/SpecialistTip';
import { OptionCard } from '../../components/OptionCard';


export default function Step4Screen({ navigation }: any) {
  const { data, updateData } = useSimulation();
  const [localData, setLocalData] = useState(data.imovel_desejado);

  const handleNext = () => {
    if (!localData.valor_imovel_desejado || localData.valor_imovel_desejado <= 0) {
      Alert.alert('Valor Inválido', 'Por favor, informe o valor do imóvel que você deseja simular.');
      return;
    }
    if (!localData.prazo_desejado_anos || localData.prazo_desejado_anos <= 0) {
      Alert.alert('Prazo Inválido', 'Informe em quantos anos você pretende pagar o imóvel.');
      return;
    }

    // Validação Regra 80 Anos
    const idade = data.perfil_objetivos.idade_comprador;
    if (idade + localData.prazo_desejado_anos > 80) {
      const prazoMax = 80 - idade;
      if (prazoMax <= 0) {
          Alert.alert('Prazo Não Permitido', `Infelizmente, pela sua idade (${idade} anos), o financiamento tradicional não é permitido (limite de 80 anos excedido).`);
      } else {
          Alert.alert('Prazo Excedido', `A soma da idade (${idade}) + o prazo (${localData.prazo_desejado_anos}) não pode ultrapassar 80 anos. Seu prazo máximo é de ${prazoMax} anos.`);
      }
      return;
    }

    updateData('imovel_desejado', localData);
    navigation.navigate('Step5');
  };

  return (
    <WizardStep
      currentStep={4}
      totalSteps={5}
      title="Imóvel Desejado"
      subtitle="O objetivo que vamos simular agora"
      onNext={handleNext}
      onBack={() => navigation.goBack()}
    >
      <Text style={styles.label}>Qual o valor do imóvel desejado?</Text>
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
          value={localData.valor_imovel_desejado.toString()}
          includeRawValueInChangeText={true}
          onChangeText={(text, raw) => {
            setLocalData({ ...localData, valor_imovel_desejado: raw ? parseFloat(raw) : 0 });
          }}
        />
      </View>

      <Text style={styles.label}>Em quantos anos quer pagar?</Text>
      <View style={styles.inputContainer}>
        <TextInputMask
          type={'only-numbers'}
          style={styles.input}
          placeholder="30"
          placeholderTextColor="#555"
          value={localData.prazo_desejado_anos.toString()}
          onChangeText={(v) => setLocalData({ ...localData, prazo_desejado_anos: parseInt(v) || 0 })}
        />
        <Text style={styles.inputSuffix}>anos</Text>
      </View>

      <SpecialistTip 
        text="A Regra dos 80 Anos é implacável: Bancos limitam o financiamento para que termine antes do comprador completar 80 anos. Fique atento ao prazo!"
      />


      <Text style={[styles.sectionTitle, { marginTop: 10 }]}>Custas de Documentação (~R$ 15k)</Text>
      <OptionCard
        label="À vista"
        value="a_vista"
        description="Pagar ITBI e Registro no ato (precisa de + entrada)"
        selected={localData.custas_documentacao_forma === 'a_vista'}
        onSelect={(v) => setLocalData({ ...localData, custas_documentacao_forma: v })}
      />
      <OptionCard
        label="Financiado"
        value="financiado"
        description="Diluir taxas nas parcelas do banco"
        selected={localData.custas_documentacao_forma === 'financiado'}
        onSelect={(v) => setLocalData({ ...localData, custas_documentacao_forma: v })}
      />
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
  inputSuffix: {
    color: '#888',
    fontSize: 16,
    marginLeft: 10,
    fontWeight: '600',
  },
  input: {
    flex: 1,
    color: '#fff',
    fontSize: 20,
    fontWeight: '700',
  },
});
