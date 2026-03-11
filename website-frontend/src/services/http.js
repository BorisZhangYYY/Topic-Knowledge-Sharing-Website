import { BACKEND_BASE_URL } from '../config/env.js'

async function request(path, options = {}) {
  const url = (BACKEND_BASE_URL || '') + path
  const res = await fetch(url, options)
  return res
}

export const http = {
  get: (path, options = {}) => request(path, { method: 'GET', ...options }),
  post: (path, body, options = {}) =>
    request(path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
      body: JSON.stringify(body),
      ...options,
    }),
}
