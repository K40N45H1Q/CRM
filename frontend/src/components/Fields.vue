<script setup>
import { currentType, baseFields } from '@/state';
</script>

<template>

<div class="wrapper">

    <div class="left">
        <div class="field" v-for="key in baseFields[currentType]" :key="key">
            <label :for="key">{{ key }}</label>
            <input :id="key" type="text">
        </div>
    </div>

    <div class="right">
        <h1>2</h1>
    </div>

</div>

</template>

<style>

.wrapper {
    box-sizing: border-box;
    padding: 0;
    margin: 0;
    width: 100vw;
    height: 100vh;
    background-color: red;
}

</style>
