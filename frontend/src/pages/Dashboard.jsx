import React, { useState, useEffect } from 'react'
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
} from '@mui/material'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts'
import api from '../api/client'

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042']

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const response = await api.get('/dashboard/stats')
      setStats(response.data)
    } catch (error) {
      console.error('Error fetching stats:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div>Loading...</div>
  }

  const statCards = [
    {
      title: "Today's Supply",
      value: stats?.today?.actual_supply || stats?.today?.expected_supply || 0,
      color: '#2196f3',
    },
    {
      title: "Allocated",
      value: stats?.today?.allocated || 0,
      color: '#4caf50',
    },
    {
      title: "Remaining",
      value: stats?.today?.remaining || 0,
      color: '#ff9800',
    },
    {
      title: "Waitlist",
      value: stats?.overall?.waitlist_count || 0,
      color: '#f44336',
    },
  ]

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      
      <Grid container spacing={3}>
        {statCards.map((card, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card sx={{ bgcolor: card.color, color: 'white' }}>
              <CardContent>
                <Typography variant="h6" component="div">
                  {card.title}
                </Typography>
                <Typography variant="h3" component="div">
                  {card.value}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
        
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Today's Summary
            </Typography>
            <Box sx={{ mt: 2 }}>
              <Typography variant="body1">
                Date: {stats?.today?.date}
              </Typography>
              <Typography variant="body1">
                Total Orders: {stats?.today?.total_orders}
              </Typography>
              <Typography variant="body1">
                Allocations: {stats?.today?.allocations}
              </Typography>
            </Box>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Overall Statistics
            </Typography>
            <Box sx={{ mt: 2 }}>
              <Typography variant="body1">
                Total Customers: {stats?.overall?.total_customers}
              </Typography>
              <Typography variant="body1">
                Pending Orders: {stats?.overall?.pending_orders}
              </Typography>
              <Typography variant="body1">
                Waitlist: {stats?.overall?.waitlist_count}
              </Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}
