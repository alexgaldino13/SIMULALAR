import React from 'react';
import { StyleSheet, Text, View, TouchableOpacity, Animated } from 'react-native';

interface OptionCardProps {
  label: string;
  value: string;
  selected: boolean;
  onSelect: (value: string) => void;
  description?: string;
  icon?: string;
}

export const OptionCard: React.FC<OptionCardProps> = ({ 
  label, 
  value, 
  selected, 
  onSelect,
  description,
  icon
}) => {
  const scaleAnim = React.useRef(new Animated.Value(selected ? 1.02 : 1)).current;

  React.useEffect(() => {
    Animated.spring(scaleAnim, {
      toValue: selected ? 1.02 : 1,
      useNativeDriver: true,
      friction: 8,
      tension: 40
    }).start();
  }, [selected]);

  return (
    <Animated.View style={{ transform: [{ scale: scaleAnim }] }}>
      <TouchableOpacity 
        style={[styles.card, selected ? styles.cardSelected : null]} 
        onPress={() => onSelect(value)}
        activeOpacity={0.8}
      >
        <View style={styles.content}>
          <View style={styles.headerRow}>
            {icon && <Text style={styles.icon}>{icon}</Text>}
            <Text style={[styles.label, selected ? styles.labelSelected : null]}>{label}</Text>
          </View>
          {description && (
            <Text style={[styles.description, selected ? styles.descriptionSelected : null]}>
              {description}
            </Text>
          )}
        </View>

        <View style={[styles.radioOuter, selected ? styles.radioOuterSelected : null]}>
          {selected && (
            <View style={styles.radioInner} />
          )}
        </View>
      </TouchableOpacity>
    </Animated.View>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 16,
    padding: 20,
    marginBottom: 12,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    borderWidth: 1.5,
    borderColor: 'rgba(255,255,255,0.08)',
  },
  cardSelected: {
    backgroundColor: 'rgba(106, 17, 203, 0.1)',
    borderColor: '#6a11cb',
  },
  content: {
    flex: 1,
    paddingRight: 10,
  },
  headerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  icon: {
    fontSize: 20,
    marginRight: 10,
  },
  label: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '700',
  },
  labelSelected: {
    color: '#fff',
  },
  description: {
    color: '#999',
    fontSize: 13,
    marginTop: 4,
    lineHeight: 18,
  },
  descriptionSelected: {
    color: 'rgba(255,255,255,0.7)',
  },
  radioOuter: {
    width: 24,
    height: 24,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: 'rgba(255,255,255,0.2)',
    alignItems: 'center',
    justifyContent: 'center',
    marginLeft: 10,
  },
  radioOuterSelected: {
    borderColor: '#6a11cb',
  },
  radioInner: {
    width: 12,
    height: 12,
    borderRadius: 6,
    backgroundColor: '#6a11cb',
  },
});
