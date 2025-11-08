import React, { useState, useEffect } from 'react'
import { View, ScrollView, StyleSheet, RefreshControl } from 'react-native'
import { Card, Text, Button, FAB } from 'react-native-paper'
import { useAuth } from '../context/AuthContext'
import api from '../api/client'

export default function HomeScreen({ navigation }) {
  const { user } = useAuth()
  const [stats, setStats] = useState(null)
  const [refreshing, setRefreshing] = useState(false)

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const response = await api.get('/dashboard/stats')
      setStats(response.data)
    } catch (error) {
      console.error('Error fetching stats:', error)
    }
  }

  const onRefresh = async () => {
    setRefreshing(true)
    await fetchStats()
    setRefreshing(false)
  }

  return (
    <View style={styles.container}>
      <ScrollView
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        <Card style={styles.welcomeCard}>
          <Card.Content>
            <Text variant="headlineSmall">
              Welcome, {user?.customer?.farm_name || user?.username}!
            </Text>
            <Text variant="bodyMedium" style={styles.subtitle}>
              {new Date().toLocaleDateString('en-US', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric',
              })}
            </Text>
          </Card.Content>
        </Card>

        <View style={styles.statsGrid}>
          <Card style={styles.statCard}>
            <Card.Content>
              <Text variant="titleLarge" style={styles.statValue}>
                {stats?.today?.allocated || 0}
              </Text>
              <Text variant="bodyMedium">Allocated Today</Text>
            </Card.Content>
          </Card>

          <Card style={styles.statCard}>
            <Card.Content>
              <Text variant="titleLarge" style={styles.statValue}>
                {stats?.overall?.pending_orders || 0}
              </Text>
              <Text variant="bodyMedium">Pending Orders</Text>
            </Card.Content>
          </Card>
        </View>

        <Card style={styles.card}>
          <Card.Title title="Quick Actions" />
          <Card.Content>
            <Button
              mode="contained"
              onPress={() => navigation.navigate('CreateOrder')}
              style={styles.actionButton}
              icon="plus"
            >
              Place New Order
            </Button>
            <Button
              mode="outlined"
              onPress={() => navigation.navigate('Orders')}
              style={styles.actionButton}
              icon="cart"
            >
              View My Orders
            </Button>
          </Card.Content>
        </Card>
      </ScrollView>

      <FAB
        icon="plus"
        style={styles.fab}
        onPress={() => navigation.navigate('CreateOrder')}
      />
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  welcomeCard: {
    margin: 16,
    marginBottom: 8,
  },
  subtitle: {
    marginTop: 8,
    color: '#666',
  },
  statsGrid: {
    flexDirection: 'row',
    padding: 16,
    gap: 16,
  },
  statCard: {
    flex: 1,
    backgroundColor: '#2196f3',
  },
  statValue: {
    color: 'white',
    fontWeight: 'bold',
  },
  card: {
    margin: 16,
  },
  actionButton: {
    marginBottom: 12,
  },
  fab: {
    position: 'absolute',
    margin: 16,
    right: 0,
    bottom: 0,
    backgroundColor: '#2196f3',
  },
})
