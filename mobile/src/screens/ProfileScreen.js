import React from 'react'
import { View, StyleSheet } from 'react-native'
import { Text, Button, Card } from 'react-native-paper'
import { useAuth } from '../context/AuthContext'

export default function ProfileScreen() {
  const { user, logout } = useAuth()

  return (
    <View style={styles.container}>
      <Card style={styles.card}>
        <Card.Content>
          <Text variant="headlineSmall">Profile</Text>
          <View style={styles.info}>
            <Text variant="bodyLarge">Name: {user?.username}</Text>
            <Text variant="bodyLarge">Email: {user?.email}</Text>
            <Text variant="bodyLarge">Role: {user?.role}</Text>
            {user?.customer && (
              <>
                <Text variant="bodyLarge">
                  Farm: {user.customer.farm_name}
                </Text>
                <Text variant="bodyLarge">Tier: {user.customer.tier}</Text>
              </>
            )}
          </View>
        </Card.Content>
      </Card>

      <Button
        mode="contained"
        onPress={logout}
        style={styles.logoutButton}
        buttonColor="#f44336"
      >
        Logout
      </Button>
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    backgroundColor: '#f5f5f5',
  },
  card: {
    marginBottom: 16,
  },
  info: {
    marginTop: 16,
    gap: 8,
  },
  logoutButton: {
    marginTop: 16,
  },
})
