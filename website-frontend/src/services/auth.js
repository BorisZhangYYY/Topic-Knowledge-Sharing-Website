import { http } from './http.js'

export async function register(username, password) {
  const res = await http.post('/api/auth/register', { username, password })
  const text = await res.text()
  return { status: res.status, body: text ? JSON.parse(text) : null }
}
