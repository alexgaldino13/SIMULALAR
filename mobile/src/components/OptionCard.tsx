import React from 'react';
import { StyleSheet, Text, View, TouchableOpacity, Animated } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';

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
  const isSelected = selected === true;

  return (
    <TouchableOpacity
      style={[
        styles.card,
        isSelected ? { borderColor: '#6a11cb', borderWidth: 2, backgroundColor: 'rgba(106,17,203,0.1)' } : {}
      ]}
      onPress={() => onSelect(value)}
      activeOpacity={0.8}
    >
      <View style={styles.content}>
        <View style={styles.headerRow}>
          {!!icon ? (
            <View style={styles.iconContainer}>
              <Text style={styles.icon}>{String(icon)}</Text>
            </View>
          ) : null}
          <View style={styles.labelContainer}>
            <Text style={styles.label}>{String(label || '')}</Text>
            {!!description ? (
              <Text style={styles.description} numberOfLines={2}>
                {String(description)}
              </Text>
            ) : null}
          </View>
        </View>
      </View>

      <View style={[styles.radioOuter, isSelected ? { borderColor: '#6a11cb' } : {}]}>
        {isSelected ? (
          <View style={{ width: 12, height: 12, borderRadius: 6, backgroundColor: '#6a11cb' }} />
        ) : null}
      </View>
    </TouchableOpacity>
  );
};

const CardContent = ({ label, description, icon, selected }: any) => {
  const isSelected = selected === true;

  const iconContainerStyle = StyleSheet.flatten([
    styles.iconContainer,
    isSelected ? styles.iconContainerSelected : {}
  ]);

  const labelStyle = StyleSheet.flatten([
    styles.label,
    isSelected ? styles.labelSelected : {}
  ]);

  const descriptionStyle = StyleSheet.flatten([
    styles.description,
    isSelected ? styles.descriptionSelected : {}
  ]);

  const radioOuterStyle = StyleSheet.flatten([
    styles.radioOuter,
    isSelected ? styles.radioOuterSelected : {}
  ]);

  return (
    <>
      <View style={styles.content}>
        <View style={styles.headerRow}>
          {icon ? (
            <View style={iconContainerStyle}>
              <Text style={styles.icon}>{String(icon)}</Text>
            </View>
          ) : null}
          <View style={styles.labelContainer}>
            <Text style={labelStyle}>{String(label || '')}</Text>
            {description ? (
              <Text style={descriptionStyle} numberOfLines={2}>
                {String(description)}
              </Text>
            ) : null}
          </View>
        </View>
      </View>

      <View style={radioOuterStyle}>
        {isSelected ? (
          <LinearGradient
            colors={['#6a11cb', '#2575fc']}
            style={styles.radioInner}
          />
        ) : null}
      </View>
    </>
  );
};

const styles = StyleSheet.create({
  cardWrapper: {
    marginBottom: 12,
    borderRadius: 20,
    overflow: 'hidden',
  },
  card: {
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.08)',
    borderRadius: 20,
  },
  cardSelected: {
    borderColor: 'rgba(106, 17, 203, 0.5)',
    borderWidth: 1.5,
  },
  content: {
    flex: 1,
    paddingRight: 10,
  },
  headerRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  iconContainer: {
    width: 44,
    height: 44,
    borderRadius: 12,
    backgroundColor: 'rgba(255,255,255,0.05)',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 15,
  },
  iconContainerSelected: {
    backgroundColor: 'rgba(106, 17, 203, 0.2)',
  },
  icon: {
    fontSize: 22,
  },
  labelContainer: {
    flex: 1,
  },
  label: {
    color: '#fff',
    fontSize: 17,
    fontWeight: 'bold',
  },
  labelSelected: {
    color: '#fff',
  },
  description: {
    color: 'rgba(255,255,255,0.4)',
    fontSize: 13,
    marginTop: 2,
    lineHeight: 18,
  },
  descriptionSelected: {
    color: 'rgba(255,255,255,0.7)',
  },
  radioOuter: {
    width: 22,
    height: 22,
    borderRadius: 11,
    borderWidth: 1.5,
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
  },
});
