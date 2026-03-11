<script setup>
import { ref, computed } from 'vue'
import { register } from '../services/auth.js'
import Card from '../components/Card.vue'

const username = ref('')
const password = ref('')
const loading = ref(false)
const errorText = ref('')
const statusCode = ref(null)
const responseBody = ref(null)
const copied = ref(false)

const accessToken = computed(() => {
  if (!responseBody.value || typeof responseBody.value !== 'object') return ''
  return responseBody.value.access_token || ''
})

const isSuccess = computed(() => {
  if (statusCode.value === null) return false
  return statusCode.value >= 200 && statusCode.value < 300
})

const usernameReturned = computed(() => {
  if (!responseBody.value || typeof responseBody.value !== 'object') return ''
  return responseBody.value.username || ''
})

const userIdReturned = computed(() => {
  if (!responseBody.value || typeof responseBody.value !== 'object') return ''
  return responseBody.value.user_id || ''
})

const prettyToken = computed(() => {
  const t = accessToken.value
  if (!t) return ''
  if (t.length <= 26) return t
  return `${t.slice(0, 16)}…${t.slice(-8)}`
})

const serverErrors = computed(() => {
  const b = responseBody.value
  if (!b || typeof b !== 'object') return []
  const errs = b.errors
  if (!errs || typeof errs !== 'object') return []
  return Object.entries(errs).map(([k, v]) => `${k}: ${String(v)}`)
})

const backendMessage = computed(() => {
  const b = responseBody.value
  if (!b || typeof b !== 'object') return ''
  return b.message ? String(b.message) : ''
})

async function onSubmit() {
  errorText.value = ''
  statusCode.value = null
  responseBody.value = null
  copied.value = false
  loading.value = true
  try {
    const { status, body } = await register(username.value, password.value)
    statusCode.value = status
    responseBody.value = body
    const token = accessToken.value
    if (token) {
      localStorage.setItem('access_token', token)
      localStorage.setItem('username', String(body.username || ''))
    }
  } catch (e) {
    errorText.value = e instanceof Error ? e.message : String(e)
  } finally {
    loading.value = false
  }
}

async function copyToken() {
  copied.value = false
  const token = accessToken.value
  if (!token) return
  try {
    await navigator.clipboard.writeText(token)
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 1200)
  } catch (e) {
    errorText.value = e instanceof Error ? e.message : String(e)
  }
}
</script>

<template>
  <div class="wrap">
    <Card>
      <h1 class="title">Register</h1>
      <form class="form" @submit.prevent="onSubmit">
        <label class="field">
          <span class="label">Username</span>
          <input v-model="username" class="input" placeholder="demo_user" autocomplete="username" />
        </label>
        <label class="field">
          <span class="label">Password</span>
          <input v-model="password" class="input" type="password" placeholder="TempPass123!" autocomplete="new-password" />
        </label>
        <button class="btn" :disabled="loading" type="submit">{{ loading ? 'Registering…' : 'Register' }}</button>
      </form>
      <div v-if="errorText" class="error">{{ errorText }}</div>
      <div v-if="statusCode !== null" class="result" :class="{ ok: isSuccess, bad: !isSuccess }">
        <div class="result-head">
          <div class="status">
            <span class="dot"></span>
            <span>HTTP {{ statusCode }}</span>
          </div>
          <div v-if="accessToken" class="token-actions">
            <button class="mini" type="button" @click="copyToken">{{ copied ? 'Copied' : 'Copy Token' }}</button>
          </div>
        </div>

        <div class="result-body">
          <div class="msg">
            <span v-if="backendMessage">{{ backendMessage }}</span>
            <span v-else>{{ isSuccess ? 'ok' : 'error' }}</span>
          </div>

          <div class="facts">
            <div v-if="usernameReturned" class="fact">
              <div class="k">Username</div>
              <div class="v">{{ usernameReturned }}</div>
            </div>
            <div v-if="userIdReturned" class="fact">
              <div class="k">User ID</div>
              <div class="v">{{ userIdReturned }}</div>
            </div>
            <div v-if="accessToken" class="fact">
              <div class="k">Access Token</div>
              <div class="v mono">{{ prettyToken }}</div>
            </div>
          </div>

          <div v-if="serverErrors.length" class="errs">
            <div class="errs-title">Errors</div>
            <ul class="errs-list">
              <li v-for="e in serverErrors" :key="e">{{ e }}</li>
            </ul>
          </div>

          <details class="details">
            <summary>Show raw response</summary>
            <pre class="json">{{ JSON.stringify(responseBody, null, 2) }}</pre>
          </details>
        </div>
      </div>
    </Card>
  </div>
  </template>

<style scoped>
.wrap {
  width: min(720px, 100%);
  text-align: center;
  margin: 0 auto;
}
.title {
  margin: 0 0 var(--space-4);
  font-size: 2.25rem;
}
.form {
  display: grid;
  gap: var(--space-4);
  margin-bottom: var(--space-4);
  max-width: 480px;
  box-sizing: border-box;
  margin-left: auto;
  margin-right: auto;
}
.field {
  display: grid;
  gap: 0.35rem;
}
.label {
  font-size: 0.9rem;
  opacity: 0.9;
}
.input {
  width: 100%;
  padding: 0.85rem 1rem;
  height: 48px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border);
  background: transparent;
  color: inherit;
  outline: none;
  box-sizing: border-box;
  font-size: 1rem;
}
.input:focus {
  border-color: var(--brand);
}
.btn {
  padding: 0.8rem 1.2rem;
  height: 48px;
  width: 100%;
  max-width: 480px;
  box-sizing: border-box;
}
.error {
  margin-top: var(--space-3);
  padding: 0.75rem 1rem;
  border-radius: var(--radius-md);
  border: 1px solid rgba(255, 0, 0, 0.35);
  color: #ff9a9a;
}
.result {
  margin-top: var(--space-3);
  border: 1px solid color-mix(in oklab, var(--border) 80%, transparent);
  border-radius: var(--radius-lg);
  overflow: hidden;
  background: color-mix(in oklab, var(--bg-elev) 60%, transparent);
  backdrop-filter: saturate(1.1) blur(10px);
  text-align: left;
}
.result.ok .dot {
  background: #1b9c3f;
}
.result.bad .dot {
  background: #c43131;
}
.result-head {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid color-mix(in oklab, var(--border) 80%, transparent);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
}
.status {
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  gap: 10px;
}
.dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  display: inline-block;
}
.mini {
  height: 36px;
  padding: 0 12px;
  border-radius: var(--radius-sm);
  border: 1px solid color-mix(in oklab, var(--border) 80%, transparent);
  background: color-mix(in oklab, var(--bg-elev) 75%, transparent);
}
.result-body {
  padding: 1rem;
  display: grid;
  gap: var(--space-4);
}
.msg {
  font-weight: 700;
  font-size: 1.05rem;
}
.facts {
  display: grid;
  gap: var(--space-3);
}
.fact {
  display: grid;
  gap: 4px;
  padding: 0.75rem 0.9rem;
  border-radius: var(--radius-md);
  border: 1px solid color-mix(in oklab, var(--border) 80%, transparent);
  background: color-mix(in oklab, var(--bg-elev) 70%, transparent);
}
.k {
  font-size: 0.85rem;
  opacity: 0.75;
}
.v {
  font-weight: 600;
}
.mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;
  overflow-wrap: anywhere;
}
.errs {
  padding: 0.75rem 0.9rem;
  border-radius: var(--radius-md);
  border: 1px solid rgba(196, 49, 49, 0.35);
  background: color-mix(in oklab, var(--bg-elev) 70%, transparent);
}
.errs-title {
  font-weight: 700;
  margin-bottom: 6px;
}
.errs-list {
  margin: 0;
  padding-left: 18px;
}
.details summary {
  cursor: pointer;
  opacity: 0.8;
}
.json {
  margin: 0;
  padding: 0.75rem 0;
  max-height: 260px;
  overflow: auto;
}
</style>
