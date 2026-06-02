import React, { useState } from 'react';
import { StyleSheet, Text, View, Alert, ScrollView } from 'react-native';
import { TextInputMask } from 'react-native-masked-text';
import { useSimulation } from '../../context/SimulationContext';
import { WizardStep } from '../../components/WizardStep';
import { SpecialistTip } from '../../components/SpecialistTip';
import { OptionCard } from '../../components/OptionCard';
import { HelpIcon } from '../../components/HelpIcon';

export default function Step4Screen({ navigation }: any) {
  const { data, updateData } = useSimulation();
  const [localData, setLocalData] = useState(data.imovel_desejado);

  const handleNext = () => {
    if (!localData.valor_imovel_desejado || localData.valor_imovel_desejado <= 0) {
      Alert.alert('Valor do Sonho', 'Informe o valor aproximado do imóvel! 🏠');
      return;
    }
    if (!localData.prazo_desejado_anos || localData.prazo_desejado_anos <= 0) {
      Alert.alert('Prazo', 'Em quanto tempo você planeja pagar seu imóvel?');
      return;
    }

    // Validação Regra 80 Anos
    const idade = data.perfil_objetivos.idade_comprador;
    if (idade + localData.prazo_desejado_anos > 80) {
      const prazoMax = 80 - idade;
      Alert.alert('Ajuste de Prazo', `A "Regra dos 80 Anos" limita seu financiamento. Com ${idade} anos, seu prazo máximo é de ${prazoMax} anos.`);
      return;
    }

    updateData('imovel_desejado', localData);
    navigation.navigate('Step5');
  };

  return (
    <WizardStep
      currentStep={4}
      totalSteps={5}
      title="O Imóvel 🏠"
      subtitle="Agora vamos definir o valor e o tempo do seu projeto."
      onNext={handleNext}
      onBack={() => navigation.goBack()}
    >
      <ScrollView showsVerticalScrollIndicator={false}>
        <View style={styles.labelRow}>
          <Text style={styles.humanLabel}>Qual o valor do imóvel desejado?</Text>
          <HelpIcon
            title="Valor de Mercado"
            description="O preço de venda do imóvel que você quer comprar."
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
            value={localData.valor_imovel_desejado.toFixed(2).replace('.', ',')}
            includeRawValueInChangeText={true}
            onChangeText={(text, raw) => {
              setLocalData({ ...localData, valor_imovel_desejado: raw ? parseFloat(raw) : 0 });
            }}
          />
        </View>

        <View style={styles.labelRow}>
          <Text style={styles.humanLabel}>Em quantos anos quer pagar?</Text>
          <HelpIcon
            title="Prazo"
            description="No Brasil, o prazo máximo comum é de 35 anos. Quanto maior o prazo, menor a parcela."
          />
        </View>
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
          text="Dica: A soma da sua idade com o prazo não pode passar de 80. Fique atento a isso! ⏱️"
        />

        <View style={[styles.labelRow, { marginTop: 10 }]}>
          <Text style={styles.humanLabel}>Custas de Documentação (ITBI)</Text>
          <HelpIcon
            title="Taxas de Cartório"
            description="ITBI e Registro custam cerca de 4 a 5% do valor do bem."
          />
        </View>
        <OptionCard
          label="Vou pagar à vista"
          value="a_vista"
          description="Pagar taxas no ato (economiza juros)"
          selected={localData.custas_documentacao_forma === 'a_vista'}
          onSelect={(v) => setLocalData({ ...localData, custas_documentacao_forma: v })}
        />
        <OptionCard
          label="Quero financiar as taxas"
          value="financiado"
          description="Diluir no financiamento do banco"
          selected={localData.custas_documentacao_forma === 'financiado'}
          onSelect={(v) => setLocalData({ ...localData, custas_documentacao_forma: v })}
        />
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
    marginBottom: 20,
  },
  inputSuffix: {
    color: '#6a11cb',
    fontSize: 16,
    marginLeft: 10,
    fontWeight: '900',
  },
  input: {
    flex: 1,
    color: '#fff',
    fontSize: 20,
    fontWeight: '700',
  },
});
