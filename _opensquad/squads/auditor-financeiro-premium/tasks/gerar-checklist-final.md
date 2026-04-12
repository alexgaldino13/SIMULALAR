# Tarefa: Gerar Checklist Final ✅
**Agente:** Vera Veredito

## 🎯 Objetivo
Transformar a análise técnica em um checklist de refatoração pronto para ser executado, garantindo confiabilidade e monetização.

## 📋 Instruções
1. Leia o `analysis-report.md` gerado pelo Dante Dados.
2. Filtre e organize as descobertas em um Checklist Técnico estruturado.
3. Para cada item do checklist, defina:
   - **Prioridade:** (Crítico, Importante, Sugestão).
   - **Arquivo e Linha:** Onde a mudança deve ocorrer.
   - **Ação Técnica:** O que deve ser alterado (fórmula, constante, formatação).
   - **Critério de Aceitação:** Como sabemos que o erro foi corrigido (ex: 'O CET do app deve estar ±0.1% do simulador da Caixa').
4. Adicione uma seção de **"Visão Humana & Monetização"**:
   - Analise se os resultados da simulação são fáceis de entender para um leigo.
   - Sugira melhorias de nomenclatura (ex: mudar 'MIP' para 'Seguro Prestamista' na interface, se facilitar a venda).
   - Valide se os relatórios gerados justificam o valor da assinatura Premium.
5. Emita seu **Veredito Final**: O app é confiável hoje? O que falta para ser o "melhor do Brasil"?

## 📥 Input
- `analysis-report.md` (Dante).

## 📤 Output
- Arquivo: `final-checklist.md` (Documento mestre para a refatoração).

## 💡 Dicas
- Mantenha o checklist conciso. Se houver 10 erros de seguro, agrupe-os em uma tarefa "Corrigir Tabela de Seguros".
- Foque na "Paz de Espírito" do usuário: o app deve ser o porto seguro das decisões financeiras dele.
