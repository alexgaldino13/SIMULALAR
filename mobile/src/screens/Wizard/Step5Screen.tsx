import React, { useState } from 'react';
import { StyleSheet, Text, View, Switch, Alert, ScrollView } from 'react-native';
import { useSimulation } from '../../context/SimulationContext';
import { WizardStep } from '../../components/WizardStep';
import { SpecialistTip } from '../../components/SpecialistTip';
import apiClient from '../../api/client';
import { HelpIcon } from '../../components/HelpIcon';

export default function Step5Screen({ navigation }: any) {
  const { data, updateData } = useSimulation();
  const [localData, setLocalData] = useState(data.cenarios);
  const [loading, setLoading] = useState(false);

  const handleCalculate = async () => {
    const finalData = { ...data, cenarios: localData };
    updateData('cenarios', localData);
    
    setLoading(true);
    try {
      // Forçar barra no final para garantir que dados de dinheiro sejam números limpos
      const payload = JSON.parse(JSON.stringify(finalData));

      const response = await apiClient.post('/api/v1/wizard/calculate/', payload);
      navigation.navigate('Results', { results: response.data });
    } catch (error: any) {
      let errorMessage = 'Erro desconhecido';
      if (error.response) {
        errorMessage = `Servidor (${error.response.status}): ${JSON.stringify(error.response.data)}`;
      } else if (error.request) {
        errorMessage = 'O App não achou o servidor. Verifique se o IP 192.168.0.15 está correto no arquivo config.ts.';
      } else {
        errorMessage = error.message;
      }
      Alert.alert('Falha no Cálculo ❌', errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const ToggleRow = ({ label, value, onValueChange, description, helpTitle, helpDesc }: any) => (
    <View style={styles.toggleRow}>
      <View style={styles.toggleTextContainer}>
        <View style={{ flexDirection: 'row', alignItems: 'center' }}>
          <Text style={styles.toggleLabel}>{label}</Text>
          {!!helpTitle ? <HelpIcon title={helpTitle} description={helpDesc} /> : null}
        </View>
        {description ? <Text style={styles.toggleDescription}>{description}</Text> : null}
      </View>
      <Switch
        trackColor={{ false: '#3e3e3e', true: '#6a11cb' }}
        thumbColor={(value === true) ? '#fff' : '#f4f3f4'}
        ios_backgroundColor="#3e3e3e"
        onValueChange={onValueChange}
        value={(value === true)}
      />
    </View>
  );

  return (
    <WizardStep
      currentStep={5}
      totalSteps={5}
      title="Sua Estratégia ⚖️"
      subtitle="Escolha quais modelos você quer que nossa inteligência compare agora."
      onNext={handleCalculate}
      onBack={() => navigation.goBack()}
      nextLabel="Ver Resultados"
      loading={loading}
    >
      <ScrollView showsVerticalScrollIndicator={false}>
        <Text style={styles.sectionTitle}>Financiamento Bancário</Text>
        <ToggleRow
            label="Tabela SAC"
            description="Parcelas que diminuem todo mês"
            helpTitle="Sistema SAC"
            helpDesc="Você paga juros apenas sobre o que resta da dívida. É o mais econômico no longo prazo."
            value={localData.comparar_financiamento_sac}
            onValueChange={(v: boolean) => setLocalData({ ...localData, comparar_financiamento_sac: v })}
        />
        <ToggleRow
            label="Tabela PRICE"
            description="Parcelas fixas do início ao fim"
            helpTitle="Sistema PRICE"
            helpDesc="Bom para quem precisa de parcelas iniciais menores e previsibilidade total."
            value={localData.comparar_financiamento_price}
            onValueChange={(v: boolean) => setLocalData({ ...localData, comparar_financiamento_price: v })}
        />

        <Text style={styles.sectionTitle}>Opções Inteligentes</Text>
        <ToggleRow
            label="Consórcio Imobiliário"
            description="Sem juros, apenas taxas de adm."
            value={localData.comparar_consorcio}
            onValueChange={(v: boolean) => setLocalData({ ...localData, comparar_consorcio: v })}
        />
        <ToggleRow
            label="Aluguel + Investimento"
            description="Investir a diferença da parcela"
            value={localData.comparar_aluguel_investimento}
            onValueChange={(v: boolean) => setLocalData({ ...localData, comparar_aluguel_investimento: v })}
        />
        <ToggleRow
            label="Guardar Dinheiro"
            description="Simular compra 100% à vista"
            value={localData.comparar_guardar_dinheiro}
            onValueChange={(v: boolean) => setLocalData({ ...localData, comparar_guardar_dinheiro: v })}
        />

        <SpecialistTip
            text="Dica: Comparar SAC vs Price pode revelar uma economia de mais de R$ 70 mil em juros! 💸"
        />
      </ScrollView>
    </WizardStep>
  );
}

const styles = StyleSheet.create({
  sectionTitle: {
    color: 'rgba(255,255,255,0.4)',
    fontSize: 11,
    fontWeight: '900',
    letterSpacing: 1.5,
    textTransform: 'uppercase',
    marginVertical: 15,
    marginLeft: 5,
  },
  toggleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: 'rgba(255,255,255,0.04)',
    borderRadius: 18,
    padding: 18,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
  },
  toggleTextContainer: {
    flex: 1,
    paddingRight: 10,
  },
  toggleLabel: {
    color: '#fff',
    fontSize: 17,
    fontWeight: 'bold',
  },
  toggleDescription: {
    color: 'rgba(255,255,255,0.5)',
    fontSize: 12,
    marginTop: 2,
  },
});
