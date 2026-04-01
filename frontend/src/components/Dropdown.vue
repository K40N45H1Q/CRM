<script setup>
import { ref, computed, defineProps, defineEmits } from 'vue'

const props = defineProps({
  options: Array,
  modelValue: String
})

const emit = defineEmits(['update:modelValue'])

const selected = ref(props.modelValue)
const open = ref(false)

const toggle = () => open.value = !open.value

const select = (o) => {
  selected.value = o
  emit('update:modelValue', o)
  open.value = false
}

const label = computed(() => selected.value)
</script>

<template>
  <div class="dropdown">
    <button @click="toggle" class="dropdown-button">{{ label }}</button>

    <ul class="dropdown-menu" :class="{ open }">
      <li
      v-for="(value, index) in options"
      :key="index"
      @click="select(value)"
      :class="{ selected: value === selected.value }"
      >
      {{ value }}
    </li>
  </ul>
</div>
</template>

<style scoped>
.dropdown {
  width: 180px;
  position: relative;
  font-family: sans-serif;
  font-size: 12px;
}
.dropdown-button {
  width: 100%;
  padding: 10px;
  font-size: 12px;
  background: black;
  color: var(--cyan);
  border: 2px solid var(--cyan);
  cursor: pointer;
  font-weight: bold;
  display: flex;
  justify-content: center;
  align-items: center;
  transition: .3s;
  text-transform: uppercase;
}
.dropdown-button:hover {
  background: var(--cyan);
  color: black;
}
.dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  width: 100%;
  margin-top: 15px;
  padding: 0;
  list-style: none;
  background: black;
  border: 2px solid var(--cyan);
  opacity: 0;
  visibility: hidden;
  transform: translateY(-10px);
  transition: .3s;
  z-index: 100;
}
.dropdown-menu.open {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}
.dropdown-menu li {
  padding: 10px;
  cursor: pointer;
  font-weight: bold;
  text-transform: uppercase;
  transition: .2s;
}
.dropdown-menu li:hover,
.dropdown-menu li.selected {
  background: var(--cyan);
  color: black;
}
.dropdown-button, .dropdown-menu {
box-shadow: 0 0 20px rgba(0, 255, 255, 0.2);
}
</style>