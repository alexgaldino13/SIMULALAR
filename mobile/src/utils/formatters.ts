/**
 * Utilitários de formatação para o App Mobile
 */

/**
 * Converte uma string monetária (ex: "R$ 1.234,56") para um número float puro (1234.56)
 */
export const currencyToNumber = (value: string): number => {
  if (!value) return 0;
  // Remove tudo que não for dígito
  const cleanValue = value.replace(/[^\d]/g, '');
  // Divide por 100 para pegar as casas decimais (se houver)
  return parseFloat(cleanValue) / 100 || 0;
};

/**
 * Converte um número para string monetária formatada (ex: 1234.56 -> "1.234,56")
 */
export const numberToCurrency = (value: number): string => {
  if (value === undefined || value === null) return '0,00';
  return value.toLocaleString('pt-BR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
};
