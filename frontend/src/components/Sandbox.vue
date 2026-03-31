<script setup>
import Header from './Header.vue';

</script>

<template>

<div class="wrapper">
    
    <div class="message">

        <h2><\></h2>
        <p>WAKE THE F*CK UP, DEV. WE HAVE A CODE TO BURN.</p>

    </div>

</div>

</template>

<style scoped>

.wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
}

.wrapper h2{
    padding: 15px;
    font-size: 150px;
    text-shadow: 0 0 15px var(--cyan);
}

.message {
    position: absolute;
    bottom: calc(50% - 50px);
    text-align: center;
}

</style>