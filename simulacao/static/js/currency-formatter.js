/**
 * Currency Formatter - Adiciona separador de milhar em tempo real
 * Formata valores monetários enquanto o usuário digita
 */

document.addEventListener('DOMContentLoaded', function() {
    // Seleciona todos os inputs de tipo "money" ou "number" com classe específica
    const moneyInputs = document.querySelectorAll('input[type="number"][data-currency="true"], .currency-input');
    
    moneyInputs.forEach(input => {
        // Formata ao digitar (em tempo real)
        input.addEventListener('input', formatCurrencyRealTime);
        // Finaliza a formatação ao sair do campo
        input.addEventListener('blur', finalizeFormat);
        // Limpa a formatação ao focar para editar
        input.addEventListener('focus', clearFormat);
    });
});

/**
 * Formata a moeda em tempo real ENQUANTO digita
 * @param {Event} event 
 */
function formatCurrencyRealTime(event) {
    let value = event.target.value;
    
    // Remove tudo que não é número
    const numericOnly = value.replace(/[^\d]/g, '');
    
    // Se vazio, deixa em branco
    if (numericOnly === '') {
        event.target.value = '';
        event.target.dataset.value = '';
        return;
    }
    
    // Armazena o valor puro numérico
    event.target.dataset.value = numericOnly;
    
    // Formata com separador de milhar e 2 decimais
    event.target.value = formatNumberRealTime(numericOnly);
}

/**
 * Formata número COM separador de milhar em tempo real
 * Exemplo: 123456 → 1.234,56
 * @param {string} numericOnly - apenas números (ex: "123456")
 * @returns {string} - formatado (ex: "1.234,56")
 */
function formatNumberRealTime(numericOnly) {
    if (!numericOnly) return '';
    
    // Garante que tem pelo menos 3 caracteres para fazer sentido
    // Se tem menos de 3, é centavos
    if (numericOnly.length <= 2) {
        return '0,' + numericOnly.padStart(2, '0');
    }
    
    // Separa reais e centavos
    const reais = numericOnly.slice(0, -2);
    const centavos = numericOnly.slice(-2);
    
    // Formata reais com separador de milhar
    const reaisFormatado = reais.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    
    return `${reaisFormatado},${centavos}`;
}

/**
 * Remove formatação ao focar (para poder editar)
 * @param {Event} event 
 */
function clearFormat(event) {
    const value = event.target.dataset.value || event.target.value;
    const numericOnly = value.replace(/[^\d]/g, '');
    event.target.value = numericOnly;
}

/**
 * Finaliza a formatação ao sair do campo
 * @param {Event} event 
 */
function finalizeFormat(event) {
    let value = event.target.value;
    const numericOnly = value.replace(/[^\d]/g, '');
    
    if (numericOnly === '') {
        event.target.value = '0,00';
    } else {
        // Se tem menos de 3 dígitos, é centavos
        if (numericOnly.length <= 2) {
            event.target.value = '0,' + numericOnly.padStart(2, '0');
        } else {
            const reais = numericOnly.slice(0, -2);
            const centavos = numericOnly.slice(-2);
            const reaisFormatado = reais.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
            event.target.value = `${reaisFormatado},${centavos}`;
        }
    }
    
    event.target.dataset.value = numericOnly;
}

/**
 * Obtém o valor numérico puro de um input de moeda
 * @param {HTMLElement} input 
 * @returns {number}
 */
function getCurrencyValue(input) {
    let value = input.dataset.value || input.value;
    const numericOnly = value.replace(/[^\d]/g, '');
    return parseFloat(numericOnly) || 0;
}

/**
 * Define o valor de um input de moeda
 * @param {HTMLElement} input 
 * @param {string} value - valor numérico puro (ex: "123456")
 */
function setCurrencyValue(input, value) {
    const numericOnly = value.toString().replace(/[^\d]/g, '');
    input.dataset.value = numericOnly;
    input.value = formatNumberRealTime(numericOnly);
}
