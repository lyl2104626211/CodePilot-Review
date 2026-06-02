<script setup lang="ts">
defineProps<{ message: string; hint?: string }>()
const emit = defineEmits<{ retry: [] }>()
</script>

<template>
  <div class="err">
    <span class="ei">!</span>
    <p class="em">{{ message }}</p>
    <p v-if="hint" class="eh">{{ hint }}</p>
    <button class="rb" @click="emit('retry')">RETRY</button>
  </div>
</template>

<style scoped>
.err {
  display: flex; flex-direction: column; align-items: center;
  padding: 36px 20px; text-align: center;
  background: var(--danger-glow); border: 1px solid rgba(248, 113, 113, 0.25);
  border-radius: var(--radius-lg); margin-bottom: 24px;
}
.ei {
  font-size: 32px; font-weight: 700; color: var(--danger);
  width: 52px; height: 52px; border: 2px solid var(--danger);
  border-radius: 50%; display: flex; align-items: center; justify-content: center;
  margin-bottom: 14px;
}
.em { font-size: 14px; color: var(--danger); margin: 0; font-weight: 600; }
.eh { font-size: 12px; color: var(--text-muted); margin: 8px 0 0; }
.rb {
  margin-top: 14px; padding: 7px 24px;
  background: transparent; border: 1px solid var(--danger); border-radius: var(--radius);
  color: var(--danger); cursor: pointer; font-family: var(--font-mono);
  font-size: 11px; font-weight: 600; letter-spacing: 1px;
}
.rb:hover { background: rgba(248, 113, 113, 0.1); }
</style>
