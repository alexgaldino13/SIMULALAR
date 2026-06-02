import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { NavigationContainer } from '@react-navigation/native';
import { SimulationProvider } from './src/context/SimulationContext';
import { MainNavigator } from './src/navigation/MainNavigator';

export default function App() {
  return (
    <SafeAreaProvider>
      <SimulationProvider>
        <NavigationContainer>
          <StatusBar style="light" />
          <MainNavigator />
        </NavigationContainer>
      </SimulationProvider>
    </SafeAreaProvider>
  );
}
