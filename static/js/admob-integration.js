/**
 * ImobCalc - Google AdMob Integration
 * Sistema de gerenciamento de anúncios com controle de assinatura
 * Data: 16/02/2026
 */

class AdMobManager {
    constructor() {
        this.isSubscriber = false;
        this.adUnits = {
            banner: 'ca-app-pub-XXXXXXXXXXXXXXXX/XXXXXXXXXX', // Substituir com ID real
            interstitial: 'ca-app-pub-XXXXXXXXXXXXXXXX/XXXXXXXXXX',
            rewarded: 'ca-app-pub-XXXXXXXXXXXXXXXX/XXXXXXXXXX'
        };
        this.adLoadAttempts = 0;
        this.maxAdLoadAttempts = 3;
        this.init();
    }

    /**
     * Inicializa o sistema de anúncios
     */
    async init() {
        try {
            // Verifica status de assinatura do usuário
            await this.checkSubscriptionStatus();
            
            if (!this.isSubscriber) {
                // Carrega o SDK do AdMob
                await this.loadAdMobSDK();
                
                // Inicializa anúncios
                this.initializeBannerAds();
                this.preloadInterstitialAd();
                
                console.log('✅ AdMob inicializado com sucesso');
            } else {
                console.log('✅ Usuário assinante - anúncios desabilitados');
            }
        } catch (error) {
            console.error('❌ Erro ao inicializar AdMob:', error);
        }
    }

    /**
     * Verifica se o usuário tem assinatura ativa
     */
    async checkSubscriptionStatus() {
        try {
            const response = await fetch('/api/assinaturas/status/', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                },
                credentials: 'same-origin'
            });
            
            if (response.ok) {
                const data = await response.json();
                this.isSubscriber = data.is_active || false;
                
                // Armazena no localStorage para cache
                localStorage.setItem('imobcalc_subscriber', this.isSubscriber);
            } else {
                // Fallback para localStorage se API falhar
                this.isSubscriber = localStorage.getItem('imobcalc_subscriber') === 'true';
            }
        } catch (error) {
            console.error('Erro ao verificar assinatura:', error);
            this.isSubscriber = false;
        }
    }

    /**
     * Carrega o SDK do Google AdMob
     */
    loadAdMobSDK() {
        return new Promise((resolve, reject) => {
            if (window.adsbygoogle) {
                resolve();
                return;
            }

            const script = document.createElement('script');
            script.src = 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js';
            script.async = true;
            script.crossOrigin = 'anonymous';
            script.setAttribute('data-ad-client', 'ca-pub-XXXXXXXXXXXXXXXX'); // Substituir
            
            script.onload = () => resolve();
            script.onerror = () => reject(new Error('Falha ao carregar SDK do AdMob'));
            
            document.head.appendChild(script);
        });
    }

    /**
     * Inicializa banners de anúncios
     */
    initializeBannerAds() {
        if (this.isSubscriber) return;

        const bannerContainers = document.querySelectorAll('.admob-banner-container');
        
        bannerContainers.forEach((container, index) => {
            const adSlot = document.createElement('ins');
            adSlot.className = 'adsbygoogle';
            adSlot.style.display = 'block';
            adSlot.setAttribute('data-ad-client', 'ca-pub-XXXXXXXXXXXXXXXX');
            adSlot.setAttribute('data-ad-slot', this.adUnits.banner);
            adSlot.setAttribute('data-ad-format', 'auto');
            adSlot.setAttribute('data-full-width-responsive', 'true');
            
            container.appendChild(adSlot);
            
            try {
                (adsbygoogle = window.adsbygoogle || []).push({});
                console.log(`✅ Banner ${index + 1} carregado`);
            } catch (error) {
                console.error(`❌ Erro ao carregar banner ${index + 1}:`, error);
            }
        });
    }

    /**
     * Pré-carrega anúncio intersticial
     */
    preloadInterstitialAd() {
        if (this.isSubscriber) return;
        
        // Implementação específica para interstitial
        // Será carregado quando necessário
        console.log('📱 Intersticial pré-carregado');
    }

    /**
     * Exibe anúncio intersticial
     * @param {string} trigger - Evento que disparou o anúncio
     */
    showInterstitialAd(trigger = 'manual') {
        if (this.isSubscriber) {
            console.log('Usuário assinante - intersticial não exibido');
            return Promise.resolve();
        }

        return new Promise((resolve) => {
            console.log(`📱 Exibindo intersticial (trigger: ${trigger})`);
            
            // Registra visualização
            this.trackAdView('interstitial', trigger);
            
            // Simula exibição (implementar lógica real do AdMob)
            setTimeout(() => {
                console.log('✅ Intersticial fechado');
                resolve();
            }, 3000);
        });
    }

    /**
     * Exibe anúncio recompensado
     * @param {Function} onReward - Callback quando usuário completar o anúncio
     */
    showRewardedAd(onReward) {
        if (this.isSubscriber) {
            console.log('Usuário assinante - recompensa concedida automaticamente');
            if (onReward) onReward();
            return Promise.resolve();
        }

        return new Promise((resolve, reject) => {
            console.log('🎁 Exibindo anúncio recompensado');
            
            // Registra visualização
            this.trackAdView('rewarded', 'user_action');
            
            // Simula anúncio recompensado
            setTimeout(() => {
                console.log('✅ Anúncio recompensado completado');
                if (onReward) onReward();
                resolve();
            }, 5000);
        });
    }

    /**
     * Registra visualização de anúncio no backend
     */
    async trackAdView(adType, trigger) {
        try {
            await fetch('/api/monetizacao/ad-view/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                },
                credentials: 'same-origin',
                body: JSON.stringify({
                    ad_type: adType,
                    trigger: trigger,
                    timestamp: new Date().toISOString()
                })
            });
        } catch (error) {
            console.error('Erro ao registrar visualização:', error);
        }
    }

    /**
     * Obtém cookie CSRF
     */
    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    /**
     * Remove todos os anúncios (para assinantes)
     */
    removeAllAds() {
        const adContainers = document.querySelectorAll('.admob-banner-container, .admob-interstitial-container');
        adContainers.forEach(container => {
            container.style.display = 'none';
            container.innerHTML = '';
        });
        console.log('✅ Todos os anúncios removidos');
    }

    /**
     * Atualiza status de assinatura
     */
    async updateSubscriptionStatus() {
        await this.checkSubscriptionStatus();
        
        if (this.isSubscriber) {
            this.removeAllAds();
        } else {
            this.initializeBannerAds();
        }
    }
}

// Inicializa o gerenciador quando o DOM estiver pronto
let adMobManager;

document.addEventListener('DOMContentLoaded', () => {
    adMobManager = new AdMobManager();
    
    // Expõe globalmente para uso em outros scripts
    window.adMobManager = adMobManager;
});

// Listener para mudanças de assinatura
window.addEventListener('subscription-changed', () => {
    if (adMobManager) {
        adMobManager.updateSubscriptionStatus();
    }
});
