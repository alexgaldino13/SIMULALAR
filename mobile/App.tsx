import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import LoginScreen from './src/screens/LoginScreen';
import { SimulationProvider } from './src/context/SimulationContext';
import { MainNavigator } from './src/navigation/MainNavigator';
import { WizardNavigator } from './src/navigation/WizardNavigator';

const Stack = createStackNavigator();

export default function App() {
  return (
    <SimulationProvider>
      <NavigationContainer>
        <Stack.Navigator screenOptions={{ headerShown: false }}>
          <Stack.Screen name="Auth" component={LoginScreen} />
          <Stack.Screen name="Main" component={MainNavigator} />
          {/* O Wizard também fica exposto para o modo "Sem Login" */}
          <Stack.Screen name="Wizard" component={WizardNavigator} />
        </Stack.Navigator>
      </NavigationContainer>
    </SimulationProvider>
  );
}
