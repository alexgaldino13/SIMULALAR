import React from 'react';
import { createStackNavigator } from '@react-navigation/stack';
import DashboardScreen from '../screens/DashboardScreen';
import SimulationDetailScreen from '../screens/SimulationDetailScreen';
import SavedSimulationsScreen from '../screens/SavedSimulationsScreen';
import ProfileScreen from '../screens/ProfileScreen';
import { WizardNavigator } from './WizardNavigator';

const Stack = createStackNavigator();

export const MainNavigator = () => {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="Dashboard" component={DashboardScreen} />
      <Stack.Screen name="Wizard" component={WizardNavigator} />
      <Stack.Screen name="SimulationDetail" component={SimulationDetailScreen} />
      <Stack.Screen name="SavedSimulations" component={SavedSimulationsScreen} />
      <Stack.Screen name="Profile" component={ProfileScreen} />
    </Stack.Navigator>
  );
};
