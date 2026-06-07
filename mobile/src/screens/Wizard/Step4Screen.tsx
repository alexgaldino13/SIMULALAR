import React, { useState } from 'react';
import {
  StyleSheet, Text, View, Alert, ScrollView, TouchableOpacity, FlatList,
} from 'react-native';
import { TextInputMask } from 'react-native-masked-text';
import { useSimulation } from '../../context/SimulationContext';
import { WizardStep } from '../../components/WizardStep';
import { SpecialistTip } from '../../components/SpecialistTip';
import { OptionCard } from '../../components/OptionCard';
import { HelpIcon } from '../../components/HelpIcon';

const ESTADOS_BR = [
  'AC','AL','AM','AP','BA','CE','DF','ES','GO','MA',
  'MG','MS','MT','PA','PB','PE','PI','PR','RJ','RN',
  'RO','RR','RS','SC','SE','SP','TO',
];

// ITBI típico por estado (alíquota da capital)
const ITBI_ALIQUOTA: Record<string, string> = {
  AC:'2,0%', AL:'2,0%', AM:'2,0%', AP:'2,0%', BA:'2,0%',
  CE:'2,0%', DF:'3,0%', ES:'2,0%', GO:'2,0%', MA:'2,0%',
  MG:'3,0%', MS:'2,0%', MT:'2,0%', PA:'2,0%', PB:'2,0%',
  PE:'3,0%', PI:'2,0%', PR:'2,7%', RJ:'2,0%', RN:'3,0%',
  RO:'2,0%', RR:'2,0%', RS:'3,0%', SC:'2,0%', SE:'2,0%',
  SP:'3,0%', TO:'2,0%',
};

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

    const idade = data.perfil_objetivos.idade_comprador;
    if (idade + localData.prazo_desejado_anos > 80) {
      const prazoMax = 80 - idade;
      Alert.alert(
        'Ajuste de Prazo',
        `A "Regra dos 80 Anos" limita seu financiamento. Com ${idade} anos, seu prazo máximo é de ${prazoMax} anos.`,
      );
      return;
    }

    updateData('imovel_desejado', localData);
    navigation.navigate('Step5');
  };

  const itbi = ITBI_ALIQUOTA[localData.estado] || '2,5%';

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
        {/* Valor do imóvel */}
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
            options={{ precision: 2, separator: ',', delimiter: '.', unit: 'R$ ', suffixUnit: '' }}
            style={styles.input}
            placeholder="R$ 0,00"
            placeholderTextColor="#555"
            value={localData.valor_imovel_desejado.toFixed(2).replace('.', ',')}
            includeRawValueInChangeText={true}
            onChangeText={(_text, raw) => {
              setLocalData({ ...localData, valor_imovel_desejado: raw ? parseFloat(raw) : 0 });
            }}
          />
        </View>

        {/* Prazo */}
        <View style={styles.labelRow}>
          <Text style={styles.humanLabel}>Em quantos anos quer pagar?</Text>
          <HelpIcon
            title="Prazo do Financiamento"
            description="No Brasil, o prazo máximo comum é de 35 anos. Quanto maior o prazo, menor a parcela mensal, mas você paga mais juros no total."
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

        {/* Estado (UF) */}
        <View style={[styles.labelRow, { marginTop: 10 }]}>
          <Text style={styles.humanLabel}>Em qual estado fica o imóvel?</Text>
          <HelpIcon
            title="ITBI — Imposto de Transmissão"
            description={`Cada estado tem uma alíquota diferente de ITBI. Em ${localData.estado}, o ITBI típico é ${itbi} do valor do imóvel e é pago na hora da escritura.`}
          />
        </View>
        <Text style={styles.itbiHint}>ITBI em {localData.estado}: {itbi}</Text>
        <View style={styles.ufGrid}>
          {ESTADOS_BR.map((uf) => (
            <TouchableOpacity
              key={uf}
              style={[styles.ufChip, localData.estado === uf && styles.ufChipSelected]}
              onPress={() => setLocalData({ ...localData, estado: uf })}
              activeOpacity={0.7}
            >
              <Text style={[styles.ufText, localData.estado === uf && styles.ufTextSelected]}>
                {uf}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Tipo de cidade (capital vs interior — afeta teto MCMV) */}
        <View style={[styles.labelRow, { marginTop: 18 }]}>
          <Text style={styles.humanLabel}>O imóvel fica em capital ou interior?</Text>
          <HelpIcon
            title="Capital ou Interior"
            description="O Minha Casa Minha Vida tem tetos de valor diferentes para capitais e regiões metropolitanas versus cidades do interior."
          />
        </View>
        <OptionCard
          label="Capital ou Região Metropolitana"
          value="capital"
          description="São Paulo, Rio, Fortaleza, Brasília etc."
          selected={localData.cidade_tipo === 'capital'}
          onSelect={(v) => setLocalData({ ...localData, cidade_tipo: v })}
        />
        <OptionCard
          label="Interior / Outras cidades"
          value="interior"
          description="Cidades menores ou zona rural"
          selected={localData.cidade_tipo === 'interior'}
          onSelect={(v) => setLocalData({ ...localData, cidade_tipo: v })}
        />

        {/* Custas de documentação */}
        <View style={[styles.labelRow, { marginTop: 10 }]}>
          <Text style={styles.humanLabel}>Custas de Documentação</Text>
          <HelpIcon
            title="ITBI + Cartório + Escritura"
            description={`ITBI (${itbi}), registro em cartório (~1%) e escritura (~0,5%). Somados custam entre 4% e 6% do imóvel, dependendo do estado.`}
          />
        </View>
        <OptionCard
          label="Vou pagar à vista"
          value="a_vista"
          description="Pagar as taxas no ato (economiza juros)"
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
    marginBottom: 8,
    marginLeft: 5,
  },
  humanLabel: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
    flex: 1,
  },
  itbiHint: {
    color: '#6a11cb',
    fontSize: 13,
    fontWeight: '700',
    marginBottom: 10,
    marginLeft: 5,
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
  ufGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginBottom: 12,
  },
  ufChip: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 10,
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
    minWidth: 44,
    alignItems: 'center',
  },
  ufChipSelected: {
    backgroundColor: 'rgba(106,17,203,0.25)',
    borderColor: '#6a11cb',
    borderWidth: 2,
  },
  ufText: {
    color: 'rgba(255,255,255,0.5)',
    fontSize: 13,
    fontWeight: '700',
  },
  ufTextSelected: {
    color: '#fff',
  },
});
