import React from 'react'
import { View, StyleSheet } from 'react-native'
import { Text } from 'react-native-paper'

export default function NotificationsScreen() {
  return (
    <View style={styles.container}>
      <Text variant="headlineMedium">Notifications</Text>
      <Text style={styles.placeholder}>Notifications coming soon...</Text>
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    backgroundColor: '#f5f5f5',
  },
  placeholder: {
    marginTop: 20,
    textAlign: 'center',
    color: '#666',
  },
})
