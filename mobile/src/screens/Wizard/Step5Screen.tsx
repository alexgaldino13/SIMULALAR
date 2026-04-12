import React, { useState } from 'react';
import { StyleSheet, Text, View, Switch, Alert, ScrollView } from 'react-native';
import { useSimulation } from '../../context/SimulationContext';
import { WizardStep } from '../../components/WizardStep';
import { SpecialistTip } from '../../components/SpecialistTip';
import { authService } from '../../api/authService';
import apiClient from '../../api/client';


export default function Step5Screen({ navigation }: any) {
  const { data, updateData } = useSimulation();
  const [localData, setLocalData] = useState(data.cenarios);
  const [loading, setLoading] = useState(false);

  const handleCalculate = async () => {
    // Final update of the context
    const finalData = { ...data, cenarios: localData };
    updateData('cenarios', localData);
    
    setLoading(true);
    try {
      // Direct call to the new API endpoint
      const response = await apiClient.post('/api/v1/wizard/calculate/', finalData);
      
      // Navigate to Results with the calculation data
      navigation.navigate('Results', { results: response.data });
    } catch (error: any) {
      console.error('Erro no cálculo:', error.response?.data || error.message);
      Alert.alert('Erro no Cálculo', 'Não foi possível processar a simulação. Verifique sua conexão.');
    } finally {
      setLoading(false);
    }
  };

  const ToggleRow = ({ label, value, onValueChange, description }: any) => (
    <View style={styles.toggleRow}>
      <View style={styles.toggleTextContainer}>
        <Text style={styles.toggleLabel}>{label}</Text>
        {description && <Text style={styles.toggleDescription}>{description}</Text>}
      </View>
      <Switch
        trackColor={{ false: '#3e3e3e', true: '#6a11cb' }}
        thumbColor={value ? '#fff' : '#f4f3f4'}
        ios_backgroundColor="#3e3e3e"
        onValueChange={onValueChange}
        value={value}
      />
    </View>
  );

  return (
    <WizardStep
      currentStep={5}
      totalSteps={5}
      title="Cenários a Comparar"
      subtitle="Quais modelos financeiros você quer que a nossa IA compare?"
      onNext={handleCalculate}
      onBack={() => navigation.goBack()}
      nextLabel="Ver Resultados"
      loading={loading}
    >
      <Text style={styles.sectionTitle}>Financiamento Bancário</Text>
      <ToggleRow
        label="Tabela SAC"
        description="Parcelas decrescentes (Economia máxima)"
        value={localData.comparar_financiamento_sac}
        onValueChange={(v: boolean) => setLocalData({ ...localData, comparar_financiamento_sac: v })}
      />
      <ToggleRow
        label="Tabela PRICE"
        description="Parcelas fixas (Previsibilidade)"
        value={localData.comparar_financiamento_price}
        onValueChange={(v: boolean) => setLocalData({ ...localData, comparar_financiamento_price: v })}
      />

      <Text style={styles.sectionTitle}>Outras Opções</Text>
      <ToggleRow
        label="Consórcio Imobiliário"
        description="Sem juros, com taxa de adm."
        value={localData.comparar_consorcio}
        onValueChange={(v: boolean) => setLocalData({ ...localData, comparar_consorcio: v })}
      />
      <ToggleRow
        label="Aluguel + Investimento"
        description="Continuar no aluguel e investir a diferença"
        value={localData.comparar_aluguel_investimento}
        onValueChange={(v: boolean) => setLocalData({ ...localData, comparar_aluguel_investimento: v })}
      />
      <ToggleRow
        label="Guardar Dinheiro"
        description="Juntar o valor total para comprar à vista"
        value={localData.comparar_guardar_dinheiro}
        onValueChange={(v: boolean) => setLocalData({ ...localData, comparar_guardar_dinheiro: v })}
      />

      <View style={styles.infoBox}>
        <Text style={styles.infoText}>
          💡 Dica: Nossa IA vai analisar todos os cenários marcados e te dar o "Ponto de Equilíbrio" ideal para o seu perfil.
        </Text>
      </View>

      <SpecialistTip 
        text="A mágica acontece aqui. Comparar SAC vs Price pode significar uma economia de mais de R$ 50 mil em juros ao final de 30 anos!"
      />
    </WizardStep>

  );
}

const styles = StyleSheet.create({
  sectionTitle: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
    marginVertical: 15,
  },
  toggleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: 'rgba(255,255,255,0.03)',
    borderRadius: 12,
    padding: 15,
    marginBottom: 10,
  },
  toggleTextContainer: {
    flex: 1,
    paddingRight: 15,
  },
  toggleLabel: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  toggleDescription: {
    color: '#888',
    fontSize: 12,
    marginTop: 2,
  },
  infoBox: {
    backgroundColor: 'rgba(106, 17, 203, 0.1)',
    padding: 15,
    borderRadius: 12,
    marginTop: 30,
    borderWidth: 1,
    borderColor: 'rgba(106, 17, 203, 0.3)',
  },
  infoText: {
    color: '#7f7fd5',
    fontSize: 13,
    lineHeight: 18,
  },
});
