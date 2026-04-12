import React, { useState } from 'react';
import { StyleSheet, Text, View, TextInput, TouchableOpacity, Alert, ScrollView, KeyboardAvoidingView, Platform } from 'react-native';
import { authService } from '../api/authService';
import { Ionicons } from '@expo/vector-icons';

export default function LoginScreen(props: any) {
  const [isSignup, setIsSignup] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [passwordConfirm, setPasswordConfirm] = useState('');
  const [firstName, setFirstName] = useState('');
  const [loading, setLoading] = useState(false);

  const handleAction = async () => {
    if (isSignup) {
      if (!username || !password || !passwordConfirm || !firstName) {
        Alert.alert('Erro', 'Por favor, preencha todos os campos obrigatórios.');
        return;
      }
      if (password !== passwordConfirm) {
        Alert.alert('Erro', 'As senhas não coincidem.');
        return;
      }
      
      setLoading(true);
      try {
        const userData = {
          email: username,
          password,
          password_confirm: passwordConfirm,
          first_name: firstName,
        };
        const data = await authService.register(userData);
        Alert.alert('Sucesso', 'Conta criada com sucesso! Bem-vindo, ' + data.first_name);
      } catch (err: any) {
        const errors = err.response?.data;
        let errorMessage = 'Erro ao criar conta.';
        if (errors) {
          errorMessage = Object.values(errors).flat().join('\n');
        }
        Alert.alert('Erro no Cadastro', errorMessage);
      } finally {
        setLoading(false);
      }
    } else {
      if (!username || !password) {
        Alert.alert('Erro', 'Por favor, preencha todos os campos.');
        return;
      }

      setLoading(true);
      try {
        const data = await authService.login(username, password);
        Alert.alert('Sucesso', 'Login realizado com sucesso!');
        console.log('Token recebido:', data.token);
      } catch (err) {
        Alert.alert('Erro de Login', 'Usuário ou senha inválidos.');
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <KeyboardAvoidingView 
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}
    >
      <ScrollView contentContainerStyle={styles.scrollContainer} showsVerticalScrollIndicator={false}>
        <View style={styles.logoContainer}>
          <View style={styles.logoCircle}>
            <Ionicons name="home" size={40} color="#FFD700" />
            <View style={styles.chartIndicator} />
          </View>
          <Text style={styles.appName}>SIMULALAR</Text>
          <Text style={styles.appTagline}>Mudar para o seu lar ficou simples</Text>
        </View>
        <Text style={styles.subtitle}>{isSignup ? 'Crie sua conta para começar' : 'Bem-vindo de volta!'}</Text>
        
        {isSignup && (
          <TextInput
            style={styles.input}
            placeholder="Nome Completo"
            placeholderTextColor="#888"
            value={firstName}
            onChangeText={setFirstName}
          />
        )}

        <TextInput
          style={styles.input}
          placeholder="E-mail"
          placeholderTextColor="#888"
          value={username}
          onChangeText={setUsername}
          autoCapitalize="none"
          keyboardType="email-address"
        />
        
        <TextInput
          style={styles.input}
          placeholder="Senha"
          placeholderTextColor="#888"
          value={password}
          onChangeText={setPassword}
          secureTextEntry
        />

        {isSignup && (
          <TextInput
            style={styles.input}
            placeholder="Confirmar Senha"
            placeholderTextColor="#888"
            value={passwordConfirm}
            onChangeText={setPasswordConfirm}
            secureTextEntry
          />
        )}

        <TouchableOpacity 
          style={[styles.button, loading && styles.buttonDisabled]} 
          onPress={handleAction}
          disabled={loading}
        >
          <Text style={styles.buttonText}>
            {loading ? 'Aguarde...' : (isSignup ? 'Criar Conta' : 'Entrar')}
          </Text>
        </TouchableOpacity>

        <TouchableOpacity onPress={() => setIsSignup(!isSignup)} style={styles.toggleContainer}>
          <Text style={styles.toggleText}>
            {isSignup ? 'Já tem uma conta? ' : 'Não tem uma conta? '}
            <Text style={styles.toggleTextBold}>{isSignup ? 'Faça Login' : 'Cadastre-se'}</Text>
          </Text>
        </TouchableOpacity>

        <TouchableOpacity 
          onPress={() => props.navigation.navigate('Wizard')} 
          style={{ marginTop: 20 }}
        >
          <Text style={{ color: '#6a11cb', fontSize: 14, textDecorationLine: 'underline' }}>
            Apenas testar simulador (Sem Login)
          </Text>
        </TouchableOpacity>

        <View style={styles.dividerContainer}>
          <View style={styles.divider} />
          <Text style={styles.dividerText}>OU</Text>
          <View style={styles.divider} />
        </View>

        <View style={styles.socialContainer}>
          <TouchableOpacity 
            style={[styles.socialButton, styles.googleButton]}
            onPress={() => Alert.alert('Google Login', 'Em breve: Integração com Google Auth.')}
          >
            <Ionicons name="logo-google" size={24} color="#fff" />
            <Text style={styles.socialButtonText}>Google</Text>
          </TouchableOpacity>

          <TouchableOpacity 
            style={[styles.socialButton, styles.appleButton]}
            onPress={() => Alert.alert('Apple Login', 'Em breve: Integração com Apple Auth.')}
          >
            <Ionicons name="logo-apple" size={24} color="#fff" />
            <Text style={styles.socialButtonText}>Apple</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f0c29',
  },
  scrollContainer: {
    flexGrow: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 30,
  },
  logoContainer: {
    alignItems: 'center',
    marginBottom: 30,
  },
  logoCircle: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: 'rgba(106, 17, 203, 0.2)',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 15,
    borderWidth: 2,
    borderColor: '#6a11cb',
  },
  chartIndicator: {
    position: 'absolute',
    bottom: 20,
    right: 20,
    width: 25,
    height: 15,
    borderBottomWidth: 3,
    borderRightWidth: 3,
    borderColor: '#FFD700',
    transform: [{ rotate: '-45deg' }],
  },
  appName: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#fff',
    letterSpacing: 2,
  },
  appTagline: {
    fontSize: 14,
    color: '#aaa',
    marginTop: 5,
  },
  subtitle: {
    fontSize: 16,
    color: '#aaa',
    marginBottom: 40,
    textAlign: 'center',
  },
  input: {
    width: '100%',
    height: 55,
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 12,
    paddingHorizontal: 15,
    marginBottom: 15,
    color: '#fff',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
  },
  button: {
    width: '100%',
    height: 55,
    backgroundColor: '#6a11cb',
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 10,
    shadowColor: '#6a11cb',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 10,
    elevation: 5,
  },
  buttonDisabled: {
    opacity: 0.7,
  },
  buttonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  toggleContainer: {
    marginTop: 25,
  },
  toggleText: {
    color: '#aaa',
    fontSize: 14,
  },
  toggleTextBold: {
    color: '#7f7fd5',
    fontWeight: 'bold',
  },
  dividerContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    width: '100%',
    marginVertical: 30,
  },
  divider: {
    flex: 1,
    height: 1,
    backgroundColor: 'rgba(255,255,255,0.1)',
  },
  dividerText: {
    color: '#555',
    paddingHorizontal: 15,
    fontSize: 12,
    fontWeight: 'bold',
  },
  socialContainer: {
    flexDirection: 'row',
    width: '100%',
    justifyContent: 'space-between',
  },
  socialButton: {
    flexDirection: 'row',
    width: '48%',
    height: 55,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  googleButton: {
    backgroundColor: '#de4b39',
  },
  appleButton: {
    backgroundColor: '#000',
  },
  socialButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    marginLeft: 10,
  },
});
