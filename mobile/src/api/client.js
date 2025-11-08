import AsyncStorage from '@react-native-async-storage/async-storage'
import axios from 'axios'

const API_BASE_URL = 'http://localhost:5000/api' // Change this to your server URL

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add token to requests
api.interceptors.request.use(async (config) => {
  const token = await AsyncStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      await AsyncStorage.removeItem('token')
      // Navigate to login screen
    }
    return Promise.reject(error)
  }
)

export default api
