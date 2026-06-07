import React, { useState } from 'react';
import { StyleSheet, Text, View, Switch, Alert, ScrollView, TextInput } from 'react-native';
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
      const payload = JSON.parse(JSON.stringify(finalData));
      const response = await apiClient.post('/api/v1/wizard/calculate/', payload);
      navigation.navigate('Results', { results: response.data });
    } catch (error: any) {
      let errorMessage = 'Erro desconhecido';
      if (error.response) {
        errorMessage = `Servidor (${error.response.status}): ${JSON.stringify(error.response.data)}`;
      } else if (error.request) {
        errorMessage = 'App não encontrou o servidor. Verifique sua conexão.';
      } else {
        errorMessage = error.message;
      }
      Alert.alert('Falha no Cálculo ❌', errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const ToggleRow = ({
    label, value, onValueChange, description, helpTitle, helpDesc,
  }: any) => (
    <View style={styles.toggleRow}>
      <View style={styles.toggleTextContainer}>
        <View style={{ flexDirection: 'row', alignItems: 'center' }}>
          <Text style={styles.toggleLabel}>{label}</Text>
          {!!helpTitle && <HelpIcon title={helpTitle} description={helpDesc} />}
        </View>
        {!!description && <Text style={styles.toggleDescription}>{description}</Text>}
      </View>
      <Switch
        trackColor={{ false: '#3e3e3e', true: '#6a11cb' }}
        thumbColor={value === true ? '#fff' : '#f4f3f4'}
        ios_backgroundColor="#3e3e3e"
        onValueChange={onValueChange}
        value={value === true}
      />
    </View>
  );

  return (
    <WizardStep
      currentStep={5}
      totalSteps={5}
      title="Sua Estratégia ⚖️"
      subtitle="Escolha quais cenários comparar. Quanto mais você ativar, melhor a análise."
      onNext={handleCalculate}
      onBack={() => navigation.goBack()}
      nextLabel="Ver Resultados"
      loading={loading}
    >
      <ScrollView showsVerticalScrollIndicator={false}>

        {/* FGTS */}
        <Text style={styles.sectionTitle}>Uso do FGTS</Text>
        <ToggleRow
          label="Usar meu FGTS"
          description="Abate a entrada e reduz parcelas a cada 2 anos"
          helpTitle="FGTS no Financiamento"
          helpDesc="Você pode usar o FGTS para aumentar a entrada e a cada 24 meses amortizar o saldo devedor. Só para trabalhadores CLT com saldo no fundo."
          value={localData.usar_fgts}
          onValueChange={(v: boolean) => setLocalData({ ...localData, usar_fgts: v })}
        />

        {/* Financiamento bancário */}
        <Text style={styles.sectionTitle}>Financiamento Bancário</Text>
        <ToggleRow
          label="Tabela SAC"
          description="Parcelas que diminuem todo mês"
          helpTitle="Sistema SAC"
          helpDesc="SAC = Sistema de Amortização Constante. Você paga sempre a mesma parcela de 'abatimento da dívida', mas os juros caem a cada mês. No total, é o mais barato."
          value={localData.comparar_financiamento_sac}
          onValueChange={(v: boolean) => setLocalData({ ...localData, comparar_financiamento_sac: v })}
        />
        <ToggleRow
          label="Tabela PRICE"
          description="Parcelas fixas do início ao fim"
          helpTitle="Sistema PRICE"
          helpDesc="PRICE = tabela francesa de amortização. Parcela igual todos os meses — ótimo para quem precisa de previsibilidade no orçamento. No início você paga mais juros."
          value={localData.comparar_financiamento_price}
          onValueChange={(v: boolean) => setLocalData({ ...localData, comparar_financiamento_price: v })}
        />

        {/* MCMV */}
        <ToggleRow
          label="Minha Casa Minha Vida"
          description="Taxa subsidiada se você se qualificar"
          helpTitle="Programa MCMV"
          helpDesc="MCMV tem taxas a partir de 4,75% a.a. para renda até R$ 2.850/mês e 7,66% para até R$ 8.000/mês. A simulação verifica automaticamente se você tem direito."
          value={localData.comparar_mcmv}
          onValueChange={(v: boolean) => setLocalData({ ...localData, comparar_mcmv: v })}
        />

        {/* Multi-banco */}
        <ToggleRow
          label="Comparar Bancos"
          description="CEF, BB, Bradesco, Itaú e Santander"
          helpTitle="Por que os bancos diferem?"
          helpDesc="Cada banco tem uma taxa própria para o mesmo perfil. A diferença de 0,5% a.a. pode significar mais de R$ 30 mil no total do contrato."
          value={localData.comparar_bancos}
          onValueChange={(v: boolean) => setLocalData({ ...localData, comparar_bancos: v } as any)}
        />

        <SpecialistTip
          text="Dica: SAC costuma ser 10-15% mais barato que PRICE no total. Mas a primeira parcela do SAC é maior. Ative os dois e compare! 💸"
        />

        {/* Alternativas ao financiamento */}
        <Text style={styles.sectionTitle}>Alternativas ao Financiamento</Text>
        <ToggleRow
          label="Consórcio Imobiliário"
          description="Sem juros, apenas taxa de administração"
          helpTitle="O que é Consórcio?"
          helpDesc="Um grupo de pessoas poupa junto. Você é 'contemplado' por sorteio ou lance e recebe uma carta de crédito para comprar. Não tem juros, mas você pode esperar anos."
          value={localData.comparar_consorcio}
          onValueChange={(v: boolean) => setLocalData({ ...localData, comparar_consorcio: v })}
        />
        <ToggleRow
          label="Aluguel + Investimento"
          description="Investir a diferença enquanto aluga"
          helpTitle="Por que comparar?"
          helpDesc="Em alguns casos, continuar alugando e investir o que seria a parcela rende mais do que comprar. Vale calcular antes de decidir."
          value={localData.comparar_aluguel_investimento}
          onValueChange={(v: boolean) => setLocalData({ ...localData, comparar_aluguel_investimento: v })}
        />
        <ToggleRow
          label="Guardar e Comprar à Vista"
          description="Simular quanto tempo levaria"
          helpTitle="Compra à Vista"
          helpDesc="Juntar dinheiro por anos e comprar sem banco. Você economiza todos os juros mas fica mais tempo pagando aluguel. A simulação mostra se compensa."
          value={localData.comparar_guardar_dinheiro}
          onValueChange={(v: boolean) => setLocalData({ ...localData, comparar_guardar_dinheiro: v })}
        />

        {/* Taxa de investimento (aparece quando aluguel ou guardar está ativo) */}
        {(localData.comparar_aluguel_investimento || localData.comparar_guardar_dinheiro) && (
          <>
            <Text style={[styles.sectionTitle, { marginTop: 5 }]}>Rendimento Esperado</Text>
            <View style={styles.inputRow}>
              <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 8 }}>
                <Text style={styles.inputLabel}>Taxa de investimento esperada</Text>
                <HelpIcon
                  title="Taxa de Retorno"
                  description="Use 9-11% para fundos de renda fixa atrelados ao CDI. A SELIC atual está em ~14,5%. Seja conservador para ter uma estimativa segura."
                />
              </View>
              <View style={styles.inputContainer}>
                <TextInput
                  style={styles.input}
                  value={String(localData.taxa_investimento_esperada || 9.5)}
                  onChangeText={(v) => {
                    const n = parseFloat(v.replace(',', '.')) || 9.5;
                    setLocalData({ ...localData, taxa_investimento_esperada: n });
                  }}
                  keyboardType="decimal-pad"
                  placeholder="9.5"
                  placeholderTextColor="#555"
                />
                <Text style={styles.inputSuffix}>% a.a.</Text>
              </View>
            </View>
          </>
        )}

        <SpecialistTip
          text="Cada cenário tem vantagens. Nossa IA analisa tudo e aponta o melhor para o seu perfil! 🤖"
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
    marginTop: 3,
  },
  inputRow: {
    backgroundColor: 'rgba(255,255,255,0.04)',
    borderRadius: 18,
    padding: 18,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
  },
  inputLabel: {
    color: '#fff',
    fontSize: 15,
    fontWeight: '600',
    flex: 1,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.08)',
    borderRadius: 12,
    paddingHorizontal: 15,
    height: 48,
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
  },
});
