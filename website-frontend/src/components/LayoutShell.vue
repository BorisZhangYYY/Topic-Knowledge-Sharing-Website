<script setup>
import { ref, computed, onMounted } from 'vue'

const panelOpen = ref(false)
const blur = ref(false)
const dim = ref(0.15)
const preset = ref('violet-pink')

function loadPrefs() {
  blur.value = (localStorage.getItem('hk_bg_blur') || 'false') === 'true'
  const d = parseFloat(localStorage.getItem('hk_bg_dim') || '0.15')
  dim.value = Number.isFinite(d) ? d : 0.35
  preset.value = localStorage.getItem('hk_bg_preset') || 'violet-pink'
}

function persist() {
  localStorage.setItem('hk_bg_blur', String(blur.value))
  localStorage.setItem('hk_bg_dim', String(dim.value))
  localStorage.setItem('hk_bg_preset', preset.value)
}

function resetTheme() {
  preset.value = 'violet-pink'
  blur.value = false
  dim.value = 0.15
  persist()
}

const bgStyle = computed(() => {
  const styles = {}
  styles.backgroundImage = preset.value === 'violet-pink'
    ? 'linear-gradient(135deg, #5f2eea 0%, #a4508b 45%, #ff6ec4 100%)'
    : preset.value === 'blue-cyan'
    ? 'linear-gradient(135deg, #3a7bd5 0%, #00d2ff 100%)'
    : preset.value === 'sunset'
    ? 'linear-gradient(135deg, #f6d365 0%, #fda085 100%)'
    : 'linear-gradient(135deg, #5f2eea 0%, #a4508b 45%, #ff6ec4 100%)'
  styles.filter = blur.value ? 'blur(8px) saturate(1.05)' : 'none'
  return styles
})

const overlayStyle = computed(() => ({
  background: `linear-gradient(0deg, rgba(0,0,0,${dim.value}) 0%, rgba(0,0,0,${dim.value}) 100%)`,
  opacity: 1,
}))

onMounted(loadPrefs)
</script>

<template>
  <div class="shell">
    <div class="bg" :style="bgStyle"></div>
    <div class="bg-overlay" :style="overlayStyle"></div>
    <header class="header">
      <div class="head">
        <div class="head-card">
          <div class="brand">Hot Knowledge</div>
        </div>
      </div>
    </header>
    <main class="main">
      <slot />
    </main>
    <div class="fab-wrap">
      <button class="fab" title="Settings" @click="panelOpen = !panelOpen">
        <svg class="fab-icon" viewBox="0 0 24 24" aria-hidden="true">
          <path
            fill="currentColor"
            d="M19.14 12.94c.04-.31.06-.63.06-.94s-.02-.63-.06-.94l2.03-1.58a.5.5 0 0 0 .12-.64l-1.92-3.32a.5.5 0 0 0-.6-.22l-2.39.96a7.4 7.4 0 0 0-1.63-.94l-.36-2.54A.5.5 0 0 0 13.9 1h-3.8a.5.5 0 0 0-.49.42l-.36 2.54c-.58.23-1.13.54-1.63.94l-2.39-.96a.5.5 0 0 0-.6.22L2.71 7.48a.5.5 0 0 0 .12.64L4.86 9.7c-.04.31-.06.63-.06.94s.02.63.06.94l-2.03 1.58a.5.5 0 0 0-.12.64l1.92 3.32c.13.22.39.3.6.22l2.39-.96c.5.4 1.05.71 1.63.94l.36 2.54c.04.24.25.42.49.42h3.8c.24 0 .45-.18.49-.42l.36-2.54c.58-.23 1.13-.54 1.63-.94l2.39.96c.21.08.47 0 .6-.22l1.92-3.32a.5.5 0 0 0-.12-.64l-2.03-1.58ZM12 15.5A3.5 3.5 0 1 1 12 8.5a3.5 3.5 0 0 1 0 7Z"
          />
        </svg>
      </button>
      <div v-if="panelOpen" class="panel">
        <div class="panel-title">Settings</div>
        <div class="section-title">Background</div>
        <div class="row presets">
          <button
            class="chip"
            :class="{active: preset==='violet-pink'}"
            @click="preset='violet-pink'; persist()"
            style="--chip-bg: linear-gradient(135deg, #5f2eea 0%, #a4508b 70%);"
          >Violet</button>
          <button
            class="chip"
            :class="{active: preset==='blue-cyan'}"
            @click="preset='blue-cyan'; persist()"
            style="--chip-bg: linear-gradient(135deg, #3a7bd5 0%, #00d2ff 100%);"
          >Blue</button>
          <button
            class="chip"
            :class="{active: preset==='sunset'}"
            @click="preset='sunset'; persist()"
            style="--chip-bg: linear-gradient(135deg, #f6d365 0%, #fda085 100%);"
          >Sunset</button>
        </div>
        <div class="row">
          <label class="chk">
            <input type="checkbox" v-model="blur" @change="persist" />
            <span>Blur</span>
          </label>
        </div>
        <div class="row">
          <label>Dim: {{ dim.toFixed(2) }}</label>
          <input class="range" type="range" min="0" max="0.8" step="0.05" v-model.number="dim" @change="persist" />
        </div>
        <div class="row">
          <button class="btn danger" @click="resetTheme">Reset</button>
        </div>
      </div>
    </div>
  </div>
  </template>

<style scoped>
.shell {
  min-height: 100vh;
  display: grid;
  grid-template-rows: auto 1fr;
  position: relative;
}
.header {
  position: sticky;
  top: 0;
  z-index: 10;
  background: transparent;
}
.head {
  max-width: var(--container-w);
  margin: 0 auto;
  padding: var(--space-4) var(--space-6);
  display: grid;
  place-items: center;
}
.head-card {
  width: 100%;
  max-width: 720px;
  box-sizing: border-box;
  padding: var(--space-3) var(--space-5);
  border-radius: 999px;
  border: 1px solid color-mix(in oklab, var(--border) 80%, transparent);
  background: color-mix(in oklab, var(--bg-elev) 75%, transparent);
  backdrop-filter: saturate(1.1) blur(8px);
  box-shadow: var(--shadow-1);
  display: grid;
  place-items: center;
}
.brand {
  font-weight: 700;
  text-align: center;
}
.main {
  display: grid;
  min-height: calc(100vh - 64px);
  place-items: center;
  padding: var(--space-6);
}
.bg {
  position: fixed;
  inset: 0;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  z-index: -2;
  transition: filter 200ms ease;
}
.bg-overlay {
  position: fixed;
  inset: 0;
  z-index: -1;
  pointer-events: none;
  transition: opacity 200ms ease;
}
.btn {
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--bg-elev);
}
.btn.danger {
  color: #b61d1d;
  border-color: rgba(182, 29, 29, 0.35);
}
.fab-wrap {
  position: fixed;
  right: 20px;
  bottom: 20px;
  z-index: 20;
  width: 48px;
  display: grid;
  place-items: center;
}
.fab {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  border: 1px solid var(--border);
  background: color-mix(in oklab, var(--bg-elev) 78%, transparent);
  backdrop-filter: saturate(1.1) blur(8px);
  box-shadow: var(--shadow-1);
  cursor: pointer;
  display: grid;
  place-items: center;
  padding: 0;
  color: var(--text);
}
.fab-icon {
  width: 20px;
  height: 20px;
  display: block;
}
.panel {
  position: absolute;
  right: 0;
  bottom: 64px;
  transform: none;
  padding: var(--space-4);
  background: color-mix(in oklab, var(--bg-elev) 86%, transparent);
  backdrop-filter: saturate(1.1) blur(10px);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-1);
  display: grid;
  gap: var(--space-3);
  width: min(340px, calc(100vw - 40px));
  box-sizing: border-box;
  max-height: calc(100vh - 140px);
  overflow: auto;
  overscroll-behavior: contain;
}
.panel-title {
  font-weight: 700;
}
.section-title {
  font-size: 0.9rem;
  opacity: 0.8;
}
.presets {
  grid-auto-flow: column;
  gap: var(--space-2);
}
.chip {
  min-width: 64px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  background: var(--bg-elev);
  padding: 6px 10px;
  cursor: pointer;
  position: relative;
}
.chip::before {
  content: '';
  position: absolute;
  inset: 2px;
  border-radius: calc(var(--radius-sm) - 2px);
  background: var(--chip-bg, transparent);
  z-index: -1;
}
.chip.active {
  outline: 2px solid var(--brand);
}
.row {
  display: grid;
  gap: var(--space-2);
}
.range {
  width: 240px;
}
.chk {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
}
</style>
