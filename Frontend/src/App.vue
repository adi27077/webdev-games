<script setup>

</script>

<template>
  <div v-if="state === 0">
    <Login @changeState="state = $event" @loggedIn="user = $event"/>
  </div>
  <div v-else-if="state === 1">
    <Menu @changeState="state = $event" @selectedGame="game = $event"/>
  </div>
  <div v-else-if="state === 2">
    <Register @changeState="state = $event"/>
  </div>
  <div v-else-if="state === 3">
    <ForgotPassword @changeState="state = $event"/>
  </div>
  <div v-else-if="state === 10">
    <HighScores :user="user" :gameName="game" @changeState="state = $event"/>
  </div>
  <div v-else-if="state === 100">
    <EndlessRunner :user="user" :gameName="game" @changeState="state = $event"/>
  </div>
  <div v-else-if="state === 101">
    <BalloonMadness :user="user" :gameName="game" @changeState="state = $event"/>
  </div>
  <div v-else-if="state === 102">
    <ChickenInvaders :user="user" :gameName="game" @changeState="state = $event"/>
  </div>
  <div v-else-if="state === 103">
    <FlappyBird :user="user" :gameName="game" @changeState="state = $event"/>
  </div>
</template>

<script>
import Login from './components/Login.vue';
import Menu from './components/Menu.vue';
import Register from './components/Register.vue';
import ForgotPassword from './components/ForgotPassword.vue';
import HighScores from './components/HighScores.vue';
import EndlessRunner from './components/EndlessRunner.vue';
import BalloonMadness from './components/BalloonMadness.vue';
import ChickenInvaders from './components/ChickenInvaders.vue';
import FlappyBird from './components/FlappyBird.vue';

export default {
  components: {
    Login,
    Menu,
    Register,
    ForgotPassword,
    HighScores,
    EndlessRunner,
    BalloonMadness,
    ChickenInvaders,
    FlappyBird,
  },
  data () {
    return {
      state: 0,
      game: '',
      user: '',
    };
  }
};
</script>

<style scoped>
header {
  line-height: 1.5;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

}
</style>
