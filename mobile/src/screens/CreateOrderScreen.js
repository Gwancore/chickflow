import React from 'react'
import { View, StyleSheet } from 'react-native'
import { Text } from 'react-native-paper'

export default function CreateOrderScreen() {
  return (
    <View style={styles.container}>
      <Text variant="headlineMedium">Create New Order</Text>
      <Text style={styles.placeholder}>Order form coming soon...</Text>
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
