import React from 'react';
import { 
  StyleSheet, 
  Text, 
  View, 
  TouchableOpacity, 
  ScrollView,
  Platform,
  ActivityIndicator
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

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
  loading?: boolean;
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
  loading = false,
}) => {
  const progress = currentStep / (totalSteps || 5);

  return (
    <View style={styles.container}>
      <View style={[StyleSheet.absoluteFill, { backgroundColor: '#0f0c29' }]} />
      
      <View style={styles.keyboardView}>
        {/* HEADER & PROGRESS */}
        <View style={styles.header}>
          <View style={styles.progressHeader}>
            <View style={styles.progressContainer}>
              <View style={styles.progressBarBackground}>
                <View
                  style={{
                    height: '100%',
                    backgroundColor: '#6a11cb',
                    width: `${Math.min(Math.max(progress, 0), 1) * 100}%` as any
                  }}
                />
              </View>
              <Text style={styles.progressText}>ETAPA {String(currentStep)} de {String(totalSteps)}</Text>
            </View>
          </View>

          <View style={styles.titleContainer}>
            <Text style={styles.title}>{String(title)}</Text>
            {subtitle ? <Text style={styles.subtitle}>{String(subtitle)}</Text> : null}
          </View>
        </View>

        {/* CONTENT */}
        <ScrollView 
          style={styles.content} 
          contentContainerStyle={styles.scrollContent}
        >
          {children}
        </ScrollView>

        {/* FOOTER */}
        <View style={styles.footer}>
          {hideBack === false ? (
            <TouchableOpacity 
              style={styles.backButton} 
              onPress={onBack}
              disabled={loading === true}
            >
              <Ionicons name="chevron-back" size={24} color={loading ? "#444" : "#fff"} />
            </TouchableOpacity>
          ) : null}
          
          <TouchableOpacity 
            style={[
                hideBack === true ? [styles.nextButton, styles.nextButtonFull] : styles.nextButton,
                loading === true ? { opacity: 0.7 } : {}
            ]}
            onPress={onNext}
            disabled={loading === true}
          >
            <View style={[styles.nextButtonGradient, { backgroundColor: '#6a11cb' }]}>
              {loading === true ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <>
                  <Text style={styles.nextButtonText}>{String(nextLabel)}</Text>
                  <Ionicons name="chevron-forward" size={20} color="#fff" />
                </>
              )}
            </View>
          </TouchableOpacity>
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f0c29',
  },
  keyboardView: {
    flex: 1,
  },
  header: {
    paddingHorizontal: 25,
    paddingTop: 50,
    paddingBottom: 10,
  },
  progressHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
  },
  progressContainer: {
    flex: 1,
  },
  progressBarBackground: {
    height: 6,
    backgroundColor: 'rgba(255,255,255,0.08)',
    borderRadius: 3,
    overflow: 'hidden',
    marginBottom: 8,
  },
  progressText: {
    color: 'rgba(255,255,255,0.4)',
    fontSize: 10,
    fontWeight: '900',
    letterSpacing: 1.5,
  },
  titleContainer: {
    marginBottom: 10,
  },
  title: {
    color: '#fff',
    fontSize: 26,
    fontWeight: 'bold',
    marginBottom: 6,
    letterSpacing: 0.5,
  },
  subtitle: {
    color: 'rgba(255,255,255,0.6)',
    fontSize: 15,
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
    backgroundColor: 'transparent',
    borderTopWidth: 1,
    borderTopColor: 'rgba(255,255,255,0.05)',
  },
  backButton: {
    width: 60,
    height: 60,
    borderRadius: 18,
    backgroundColor: 'rgba(255,255,255,0.05)',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 15,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
  },
  nextButton: {
    flex: 1,
    height: 60,
    borderRadius: 18,
    overflow: 'hidden',
  },
  nextButtonGradient: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: 18,
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
