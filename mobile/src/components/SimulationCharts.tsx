import React from 'react';
import { View, Text, Dimensions, StyleSheet } from 'react-native';
import { BarChart } from 'react-native-chart-kit';

export default function SimulationCharts({ results }: any) {
  if (!results || !results.resultados) {
    return null;
  }

  const windowWidth = Dimensions.get('window').width - 40;

  // Extrair e limpar dados
  const labels: string[] = [];
  const costData: number[] = [];
  const installmentData: number[] = [];

  Object.entries(results.resultados).forEach(([key, value]: any) => {
    labels.push(value.metodo.replace('Financiamento ', ''));
    
    // Parse R$ 1.234.567,89 -> 1234567.89
    const parseValue = (val: string) => {
      if (!val) return 0;
      return parseFloat(val.replace('R$', '').replace(/\./g, '').replace(',', '.').trim());
    };

    costData.push(parseValue(value.total_custo));
    installmentData.push(parseValue(value.parcela_inicial));
  });

  const chartConfig = {
    backgroundColor: '#0f0c29',
    backgroundGradientFrom: '#0f0c29',
    backgroundGradientTo: '#1a1a2e',
    decimalPlaces: 0,
    color: (opacity = 1) => `rgba(106, 17, 203, ${opacity})`,
    labelColor: (opacity = 1) => `rgba(255, 255, 255, ${opacity})`,
    style: {
      borderRadius: 16,
    },
    propsForDots: {
      r: '6',
      strokeWidth: '2',
      stroke: '#ffa726',
    },
  };

  return (
    <View style={styles.container}>
      <Text style={styles.chartTitle}>Comparativo de Custo Total (R$)</Text>
      <BarChart
        data={{
          labels: labels,
          datasets: [{ data: costData }],
        }}
        width={windowWidth}
        height={220}
        yAxisLabel="R$"
        yAxisSuffix=""
        chartConfig={chartConfig}
        verticalLabelRotation={30}
        style={styles.chart}
        fromZero={true}
      />

      <Text style={[styles.chartTitle, { marginTop: 30 }]}>Primeira Parcela (R$)</Text>
      <BarChart
        data={{
          labels: labels,
          datasets: [{ data: installmentData }],
        }}
        width={windowWidth}
        height={220}
        yAxisLabel="R$"
        yAxisSuffix=""
        chartConfig={{
          ...chartConfig,
          color: (opacity = 1) => `rgba(255, 215, 0, ${opacity})`, // Gold for installments
        }}
        verticalLabelRotation={30}
        style={styles.chart}
        fromZero={true}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginVertical: 20,
    alignItems: 'center',
  },
  chartTitle: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 15,
    alignSelf: 'flex-start',
  },
  chart: {
    marginVertical: 8,
    borderRadius: 16,
  },
});
