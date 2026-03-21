/**
 * Currency Input - Formatação automática de campos monetários
 * Usa Cleave.js para formatar valores em tempo real
 */

document.addEventListener('DOMContentLoaded', function() {
    // Seleciona todos os inputs com classe 'currency-input'
    const currencyInputs = document.querySelectorAll('.currency-input');
    
    currencyInputs.forEach(input => {
        new Cleave(input, {
            numeral: true,
            numeralDecimalMark: ',',
            delimiter: '.',
            prefix: 'R$ ',
            numeralPositiveOnly: true,
            rawValueTrimPrefix: true,
            numeralDecimalScale: 2
        });
    });
    
    console.log(`💰 Currency Input: ${currencyInputs.length} campos monetários formatados`);
});
