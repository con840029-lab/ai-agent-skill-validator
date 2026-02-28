import { defineStore } from 'pinia'
import { authAPI } from '../api'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user')) || null,
    token: localStorage.getItem('token') || null
  }),

  actions: {
    setUser(user, token) {
      this.user = user
      this.token = token
      localStorage.setItem('user', JSON.stringify(user))
      localStorage.setItem('token', token)
    },

    async login(username, password) {
      const response = await authAPI.login({ username, password })
      this.setUser(response.data.user, response.data.access_token)
      return response
    },

    async register(username, email, password) {
      const response = await authAPI.register({ username, email, password })
      this.setUser(response.data.user, response.data.access_token)
      return response
    },

    async fetchUserInfo() {
      const response = await authAPI.me()
      this.user = response.data
      localStorage.setItem('user', JSON.stringify(response.data))
      return response
    },

    logout() {
      this.user = null
      this.token = null
      localStorage.removeItem('user')
      localStorage.removeItem('token')
    },

    isAuthenticated() {
      return !!this.token
    }
  }
})
