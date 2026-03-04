# simulacao/encryption.py
"""
Módulo de criptografia para dados sensíveis.
Utiliza Fernet (criptografia simétrica) para proteger dados como CPF, renda, etc.
"""

from cryptography.fernet import Fernet
from django.conf import settings
import base64
import hashlib


class DataEncryption:
    """
    Classe para criptografar e descriptografar dados sensíveis.
    Usa a chave secreta do Django para gerar a chave de criptografia.
    """
    
    def __init__(self):
        # Gerar chave Fernet a partir da SECRET_KEY do Django
        # Isso garante que a mesma chave seja usada em todas as instâncias
        key = self._generate_key_from_settings()
        self.cipher = Fernet(key)
    
    def _generate_key_from_settings(self):
        """
        Gera uma chave Fernet válida a partir da SECRET_KEY do Django.
        A chave Fernet deve ter exatamente 32 bytes em base64.
        """
        # Usar SHA256 para gerar um hash de 32 bytes da SECRET_KEY
        secret_key = settings.SECRET_KEY.encode('utf-8')
        key_hash = hashlib.sha256(secret_key).digest()
        # Codificar em base64 para formato Fernet
        fernet_key = base64.urlsafe_b64encode(key_hash)
        return fernet_key
    
    def encrypt(self, data):
        """
        Criptografa uma string.
        
        Args:
            data (str): Dados a serem criptografados
        
        Returns:
            str: Dados criptografados em base64
        """
        if data is None or data == '':
            return None
        
        # Converter para bytes
        data_bytes = data.encode('utf-8')
        
        # Criptografar
        encrypted_bytes = self.cipher.encrypt(data_bytes)
        
        # Retornar como string base64
        return encrypted_bytes.decode('utf-8')
    
    def decrypt(self, encrypted_data):
        """
        Descriptografa uma string.
        
        Args:
            encrypted_data (str): Dados criptografados em base64
        
        Returns:
            str: Dados descriptografados
        """
        if encrypted_data is None or encrypted_data == '':
            return None
        
        try:
            # Converter para bytes
            encrypted_bytes = encrypted_data.encode('utf-8')
            
            # Descriptografar
            decrypted_bytes = self.cipher.decrypt(encrypted_bytes)
            
            # Retornar como string
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            # Log do erro (em produção, usar logging adequado)
            print(f"Erro ao descriptografar dados: {e}")
            return None
    
    def encrypt_cpf(self, cpf):
        """
        Criptografa um CPF.
        Remove formatação antes de criptografar.
        
        Args:
            cpf (str): CPF no formato XXX.XXX.XXX-XX ou XXXXXXXXXXX
        
        Returns:
            str: CPF criptografado
        """
        if not cpf:
            return None
        
        # Remover formatação (pontos e traços)
        cpf_clean = cpf.replace('.', '').replace('-', '').strip()
        
        # Criptografar
        return self.encrypt(cpf_clean)
    
    def decrypt_cpf(self, encrypted_cpf, formatted=True):
        """
        Descriptografa um CPF.
        
        Args:
            encrypted_cpf (str): CPF criptografado
            formatted (bool): Se True, retorna formatado (XXX.XXX.XXX-XX)
        
        Returns:
            str: CPF descriptografado
        """
        cpf = self.decrypt(encrypted_cpf)
        
        if not cpf:
            return None
        
        # Formatar se solicitado
        if formatted and len(cpf) == 11:
            return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
        
        return cpf
    
    def encrypt_currency(self, value):
        """
        Criptografa um valor monetário.
        
        Args:
            value (float or Decimal): Valor a ser criptografado
        
        Returns:
            str: Valor criptografado
        """
        if value is None:
            return None
        
        # Converter para string com 2 casas decimais
        value_str = f"{float(value):.2f}"
        
        # Criptografar
        return self.encrypt(value_str)
    
    def decrypt_currency(self, encrypted_value):
        """
        Descriptografa um valor monetário.
        
        Args:
            encrypted_value (str): Valor criptografado
        
        Returns:
            float: Valor descriptografado
        """
        value_str = self.decrypt(encrypted_value)
        
        if not value_str:
            return None
        
        try:
            return float(value_str)
        except ValueError:
            return None
    
    def mask_cpf(self, cpf):
        """
        Mascara um CPF para exibição segura.
        Exemplo: 123.456.789-00 -> ***.***.***-00
        
        Args:
            cpf (str): CPF no formato XXX.XXX.XXX-XX
        
        Returns:
            str: CPF mascarado
        """
        if not cpf or len(cpf) < 14:
            return "***.***.***-**"
        
        # Manter apenas os últimos 2 dígitos
        return f"***.***.***-{cpf[-2:]}"
    
    def mask_currency(self, value, show_first_digit=True):
        """
        Mascara um valor monetário para exibição segura.
        Exemplo: 5000.00 -> R$ 5.***,**
        
        Args:
            value (float): Valor a ser mascarado
            show_first_digit (bool): Se True, mostra o primeiro dígito
        
        Returns:
            str: Valor mascarado
        """
        if value is None:
            return "R$ ***.***,**"
        
        value_str = f"{float(value):.2f}"
        
        if show_first_digit and len(value_str) > 0:
            first_digit = value_str[0]
            return f"R$ {first_digit}.***,**"
        
        return "R$ ***.***,**"


# Instância global para uso em todo o projeto
encryption = DataEncryption()


# Funções de conveniência para uso direto
def encrypt_data(data):
    """Criptografa dados."""
    return encryption.encrypt(data)


def decrypt_data(encrypted_data):
    """Descriptografa dados."""
    return encryption.decrypt(encrypted_data)


def encrypt_cpf(cpf):
    """Criptografa CPF."""
    return encryption.encrypt_cpf(cpf)


def decrypt_cpf(encrypted_cpf, formatted=True):
    """Descriptografa CPF."""
    return encryption.decrypt_cpf(encrypted_cpf, formatted)


def encrypt_currency(value):
    """Criptografa valor monetário."""
    return encryption.encrypt_currency(value)


def decrypt_currency(encrypted_value):
    """Descriptografa valor monetário."""
    return encryption.decrypt_currency(encrypted_value)


def mask_cpf(cpf):
    """Mascara CPF para exibição."""
    return encryption.mask_cpf(cpf)


def mask_currency(value, show_first_digit=True):
    """Mascara valor monetário para exibição."""
    return encryption.mask_currency(value, show_first_digit)
