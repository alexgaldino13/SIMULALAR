import React from 'react';
import { createStackNavigator } from '@react-navigation/stack';
import Step1Screen from '../screens/Wizard/Step1Screen';
import Step2Screen from '../screens/Wizard/Step2Screen';
import Step3Screen from '../screens/Wizard/Step3Screen';
import Step4Screen from '../screens/Wizard/Step4Screen';
import Step5Screen from '../screens/Wizard/Step5Screen';
import ResultsScreen from '../screens/Wizard/ResultsScreen';

const Stack = createStackNavigator();

export const WizardNavigator = () => {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="Step1" component={Step1Screen} />
      <Stack.Screen name="Step2" component={Step2Screen} />
      <Stack.Screen name="Step3" component={Step3Screen} />
      <Stack.Screen name="Step4" component={Step4Screen} />
      <Stack.Screen name="Step5" component={Step5Screen} />
      <Stack.Screen name="Results" component={ResultsScreen} />
    </Stack.Navigator>
  );
};
