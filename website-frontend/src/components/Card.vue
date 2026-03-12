<template>
  <div class="card">
    <slot />
  </div>
</template>

<style scoped>
.card {
  background: color-mix(in oklab, var(--bg-elev) 80%, transparent);
  backdrop-filter: saturate(1.1) blur(6px);
  border: 1px solid color-mix(in oklab, var(--border) 80%, transparent);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-1);
  padding: var(--space-6);
  width: 100%;
  max-width: 720px;
  box-sizing: border-box;
}
</style>
