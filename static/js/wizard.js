/**
 * wizard.js
 * Lógica para inicializar "Poll Cards" para campos de escolha única no wizard.
 * Transforma radio buttons em cards clicáveis.
 */

document.addEventListener('DOMContentLoaded', function() {
    /**
     * Inicializa os "Poll Cards" para um determinado grupo de radio buttons.
     * @param {HTMLElement} container - O elemento que contém os cards e os radios.
     */
    function initializePollCards(container) {
        const cards = container.querySelectorAll('.poll-card');
        const radios = container.querySelectorAll('input[type="radio"]');

        // Função para atualizar o estado visual dos cards com base no radio checado
        const updateSelectedCard = () => {
            radios.forEach(radio => {
                const card = radio.closest('.poll-card');
                if (card) {
                    if (radio.checked) {
                        card.classList.add('selected');
                    } else {
                        card.classList.remove('selected');
                    }
                }
            });
        };

        // Adiciona evento de clique a cada card
        cards.forEach(card => {
            const radio = card.querySelector('input[type="radio"]');
            if (radio) {
                // Remove radio da navegação por TAB para evitar "dupla tab"
                // O foco será controlado pelo .poll-card (tabindex="0")
                radio.setAttribute('tabindex', '-1');
            }

            card.addEventListener('click', () => {
                if (radio && !radio.checked) {
                    // 1. Marca o radio button correspondente
                    radio.checked = true;

                    // 2. Atualiza o estado visual de todos os cards no grupo
                    updateSelectedCard();

                    // 3. Dispara um evento 'change' para compatibilidade com outras lógicas
                    const changeEvent = new Event('change', { bubbles: true });
                    radio.dispatchEvent(changeEvent);
                }
            });
        });

        // Garante que o estado visual inicial (ao carregar a página) esteja correto
        updateSelectedCard();
    }

    // Encontra todos os containers de poll cards na página e os inicializa
    document.querySelectorAll('.poll-cards-container').forEach(initializePollCards);

    // ========================================
    // Feedback Progressivo e Animações - 5.5
    // ========================================

    // Validação em tempo real nos inputs
    function initializeInputValidation() {
        const inputs = document.querySelectorAll('input[type="text"], input[type="number"], select');
        
        inputs.forEach(input => {
            // Wrapper para ícone de validação
            const wrapper = document.createElement('div');
            wrapper.style.position = 'relative';
            if (input.parentNode) {
                input.parentNode.insertBefore(wrapper, input);
                wrapper.appendChild(input);
            }
            
            const validationIcon = document.createElement('span');
            validationIcon.className = 'validation-icon';
            wrapper.appendChild(validationIcon);
            
            input.addEventListener('input', function() {
                if (this.value.trim() !== '') {
                    this.classList.remove('input-invalid');
                    this.classList.add('input-valid');
                } else {
                    this.classList.remove('input-valid');
                }
            });
            
            input.addEventListener('blur', function() {
                if (this.required && this.value.trim() === '') {
                    this.classList.add('input-invalid');
                }
            });
        });
    }

    // Efeito ripple nos botões
    function initializeRippleEffect() {
        const buttons = document.querySelectorAll('.btn');
        
        buttons.forEach(button => {
            button.addEventListener('click', function(e) {
                const ripple = document.createElement('span');
                ripple.className = 'ripple';
                
                const rect = this.getBoundingClientRect();
                const size = Math.max(rect.width, rect.height);
                
                ripple.style.width = ripple.style.height = size + 'px';
                ripple.style.left = (e.clientX - rect.left - size / 2) + 'px';
                ripple.style.top = (e.clientY - rect.top - size / 2) + 'px';
                
                this.appendChild(ripple);
                
                setTimeout(() => ripple.remove(), 600);
            });
        });
    }

    // Inicializar todas as animações
    initializeInputValidation();
    initializeRippleEffect();

        // ========================================
    // Formatação monetária com Cleave.js - Bug Fix
    // ========================================
    
    function initializeCurrencyInputs() {
        if (typeof Cleave === 'undefined') {
            console.warn('Cleave.js não está carregado.');
            return;
        }
        
        const currencyInputs = document.querySelectorAll('.currency-input');
        
        currencyInputs.forEach(input => {
            // Inicializa Cleave para cada input de moeda
            new Cleave(input, {
                numeral: true,
                numeralDecimalMark: ',',
                delimiter: '.',
                numeralDecimalScale: 2,
                numeralPositiveOnly: true,
                onValueChanged: function(e) {
                    // Armazena o valor bruto (sem formatação) para envio ao servidor
                    input.dataset.rawValue = e.target.rawValue;
                }
            });

            // Se o input já tem valor inicial (ex: vindo do Django), formata
            if (input.value) {
                // Se o valor contiver apenas dígitos e ponto (formato americano/django), converte para virgula
                if (input.value.includes('.') && !input.value.includes(',')) {
                    input.value = input.value.replace('.', ',');
                }
            }
        });

        const percentInputs = document.querySelectorAll('.percent-input');
        percentInputs.forEach(input => {
            new Cleave(input, {
                numeral: true,
                numeralDecimalMark: ',',
                delimiter: '.',
                numeralDecimalScale: 2,
                numeralPositiveOnly: true,
                suffix: '%',
                onValueChanged: function(e) {
                    input.dataset.rawValue = e.target.rawValue;
                }
            });
        });
        
        // Form Global Submit Handler to restore raw values
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            if (!form.dataset.cleaveHandlerAdded) {
                form.dataset.cleaveHandlerAdded = 'true';
                form.addEventListener('submit', function() {
                    const maskedInputs = form.querySelectorAll('.currency-input, .percent-input');
                    maskedInputs.forEach(inp => {
                        // Se o Cleave capturou um rawValue, usa ele para o POST
                        if (inp.dataset.rawValue !== undefined && inp.dataset.rawValue !== "") {
                            inp.value = inp.dataset.rawValue;
                        } else {
                            // Fallback para campos preenchidos mas não alterados
                            inp.value = inp.value.replace(/\./g, '').replace(',', '.').replace(/[^\d.-]/g, '');
                        }
                    });
                });
            }
        });
    }


    // Inicializar formatação monetária

    // ==========================================================================
    // Navegação por teclado - Item 5.10 Acessibilidade
    // ==========================================================================
    
    // Enter para avançar no formulário
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && e.target.tagName !== 'TEXTAREA') {
                e.preventDefault();
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn) submitBtn.click();
            }
        });
    }
    
    // Esc para voltar
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const backBtn = document.querySelector('.btn-voltar');
            if (backBtn) backBtn.click();
        }
    });
    
    // Tornar poll-cards navegáveis por teclado
    const pollCards = document.querySelectorAll('.poll-card');
    pollCards.forEach(card => {
        // Tornar focável
        card.setAttribute('tabindex', '0');
        
        // Ativar com Enter ou Space
        card.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                card.click();
            }
        });
    });

    initializeCurrencyInputs();
});