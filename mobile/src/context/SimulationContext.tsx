import React, { createContext, useContext, useState, ReactNode } from 'react';

export interface SimulationData {
  perfil_objetivos: {
    perfil_usuario: string;
    prioridade_principal: string;
    onde_mora_atualmente: string;
    aluguel_atual: number;
    tempo_mora_atualmente: string;
    idade_comprador: number;
  };
  trabalho_renda: {
    renda_familiar_bruta: number;
    tipo_contrato: string;
    renda_estavel: string;
    recebe_13_salario: boolean;
    quantos_dependentes: number;
    outras_rendas: number;
  };
  financas_atuais: {
    valor_imovel_proprio: number;
    saldo_dinheiro_guardado: number;
    saldo_fgts: number;
    despesas_mensais_fixas: number;
  };
  imovel_desejado: {
    valor_imovel_desejado: number;
    prazo_desejado_anos: number;
    custas_documentacao_forma: string;
  };
  cenarios: {
    comparar_financiamento_price: boolean;
    comparar_financiamento_sac: boolean;
    comparar_consorcio: boolean;
    prazo_consorcio: string;
    estrategia_contemplacao: string;
    valor_lance_disponivel: number;
    tempo_maximo_espera_consorcio: number;
    comparar_mcmv: boolean;
    comparar_aluguel_investimento: boolean;
    comparar_compra_a_vista: boolean;
    comparar_guardar_dinheiro: boolean;
    pagar_aluguel_com_rendimentos: boolean;
    usar_fgts: boolean;
    taxa_investimento_esperada: number;
  };
}

const initialData: SimulationData = {
  perfil_objetivos: {
    perfil_usuario: 'comprador_morar',
    prioridade_principal: 'equilibrio',
    onde_mora_atualmente: 'aluga',
    aluguel_atual: 1500,
    tempo_mora_atualmente: '1_3',
    idade_comprador: 30,
  },
  trabalho_renda: {
    renda_familiar_bruta: 8000,
    tipo_contrato: 'clt',
    renda_estavel: 'estavel',
    recebe_13_salario: true,
    quantos_dependentes: 1,
    outras_rendas: 0,
  },
  financas_atuais: {
    valor_imovel_proprio: 0,
    saldo_dinheiro_guardado: 50000,
    saldo_fgts: 0,
    despesas_mensais_fixas: 2000,
  },
  imovel_desejado: {
    valor_imovel_desejado: 500000,
    prazo_desejado_anos: 30,
    custas_documentacao_forma: 'financiado',
  },
  cenarios: {
    comparar_financiamento_price: true,
    comparar_financiamento_sac: true,
    comparar_consorcio: true,
    prazo_consorcio: '180',
    estrategia_contemplacao: 'sorteio',
    valor_lance_disponivel: 0,
    tempo_maximo_espera_consorcio: 36,
    comparar_mcmv: false,
    comparar_aluguel_investimento: true,
    comparar_compra_a_vista: false,
    comparar_guardar_dinheiro: true,
    pagar_aluguel_com_rendimentos: false,
    usar_fgts: true,
    taxa_investimento_esperada: 9.5,
  },
};

interface SimulationContextType {
  data: SimulationData;
  updateData: (stepName: keyof SimulationData, stepData: any) => void;
  resetData: () => void;
}

const SimulationContext = createContext<SimulationContextType | undefined>(undefined);

export const SimulationProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [data, setData] = useState<SimulationData>(initialData);

  const updateData = (stepName: keyof SimulationData, stepData: any) => {
    setData((prev) => ({
      ...prev,
      [stepName]: { ...prev[stepName], ...stepData },
    }));
  };

  const resetData = () => setData(initialData);

  return (
    <SimulationContext.Provider value={{ data, updateData, resetData }}>
      {children}
    </SimulationContext.Provider>
  );
};

export const useSimulation = () => {
  const context = useContext(SimulationContext);
  if (context === undefined) {
    throw new Error('useSimulation must be used within a SimulationProvider');
  }
  return context;
};
