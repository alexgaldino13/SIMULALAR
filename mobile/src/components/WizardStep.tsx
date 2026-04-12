import React from 'react';
import { 
  StyleSheet, 
  Text, 
  View, 
  TouchableOpacity, 
  SafeAreaView, 
  KeyboardAvoidingView, 
  Platform, 
  ScrollView 
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { StatusBar } from 'expo-status-bar';

interface WizardStepProps {
  currentStep: number;
  totalSteps: number;
  title: string;
  subtitle?: string;
  onNext: () => void;
  onBack: () => void;
  children: React.ReactNode;
  nextLabel?: string;
  hideBack?: boolean;
}

export const WizardStep: React.FC<WizardStepProps> = ({
  currentStep,
  totalSteps,
  title,
  subtitle,
  onNext,
  onBack,
  children,
  nextLabel = 'Continuar',
  hideBack = false,
}) => {
  const progress = currentStep / totalSteps;

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="light" />
      <KeyboardAvoidingView 
        behavior={Platform.OS === 'ios' ? 'padding' : undefined} 
        style={styles.keyboardView}
      >
        {/* HEADER & PROGRESS */}
        <View style={styles.header}>
          <View style={styles.progressContainer}>
            <View style={styles.progressBarBackground}>
              <View 
                style={[
                  styles.progressBarFill, 
                  { width: `${progress * 100}%` }
                ]} 
              />
            </View>
            <Text style={styles.progressText}>Passo {currentStep} de {totalSteps}</Text>
          </View>

          <View style={styles.titleContainer}>
            <Text style={styles.title}>{title}</Text>
            {subtitle && <Text style={styles.subtitle}>{subtitle}</Text>}
          </View>
        </View>

        {/* CONTENT */}
        <ScrollView 
          style={styles.content} 
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
          keyboardShouldPersistTaps="handled"
        >
          {children}
        </ScrollView>

        {/* FOOTER */}
        <View style={styles.footer}>
          {!hideBack && (
            <TouchableOpacity 
              style={styles.backButton} 
              onPress={onBack}
              activeOpacity={0.7}
            >
              <Ionicons name="arrow-back" size={24} color="#fff" />
            </TouchableOpacity>
          )}
          
          <TouchableOpacity 
            style={[styles.nextButton, hideBack && styles.nextButtonFull]} 
            onPress={onNext}
            activeOpacity={0.8}
          >
            <Text style={styles.nextButtonText}>{nextLabel}</Text>
            <Ionicons name="arrow-forward" size={20} color="#fff" style={{ marginLeft: 8 }} />
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f0c29', // Dark premium background
  },
  keyboardView: {
    flex: 1,
  },
  header: {
    paddingHorizontal: 25,
    paddingTop: 20,
    paddingBottom: 10,
  },
  progressContainer: {
    marginBottom: 20,
  },
  progressBarBackground: {
    height: 6,
    backgroundColor: 'rgba(255,255,255,0.1)',
    borderRadius: 3,
    overflow: 'hidden',
    marginBottom: 8,
  },
  progressBarFill: {
    height: '100%',
    backgroundColor: '#6a11cb',
    borderRadius: 3,
  },
  progressText: {
    color: '#888',
    fontSize: 12,
    fontWeight: '600',
    textTransform: 'uppercase',
    letterSpacing: 1,
  },
  titleContainer: {
    marginTop: 5,
  },
  title: {
    color: '#fff',
    fontSize: 28,
    fontWeight: '800',
    marginBottom: 6,
  },
  subtitle: {
    color: '#aaa',
    fontSize: 16,
    lineHeight: 22,
  },
  content: {
    flex: 1,
  },
  scrollContent: {
    paddingHorizontal: 25,
    paddingTop: 10,
    paddingBottom: 30,
  },
  footer: {
    flexDirection: 'row',
    paddingHorizontal: 25,
    paddingVertical: 20,
    borderTopWidth: 1,
    borderTopColor: 'rgba(255,255,255,0.05)',
    backgroundColor: '#0f0c29',
  },
  backButton: {
    width: 56,
    height: 56,
    borderRadius: 16,
    backgroundColor: 'rgba(255,255,255,0.05)',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 15,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
  },
  nextButton: {
    flex: 1,
    height: 56,
    backgroundColor: '#6a11cb',
    borderRadius: 16,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    elevation: 4,
    shadowColor: '#6a11cb',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
  },
  nextButtonFull: {
    marginLeft: 0,
  },
  nextButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
    letterSpacing: 0.5,
  },
});
