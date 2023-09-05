<script setup>

</script>

<template>
  <v-toolbar style="position: absolute; top: 0; left: 0">
    <v-btn @click="back()">
      <v-icon>mdi-arrow-left</v-icon>
    </v-btn>
    <v-app-bar-title>{{ gameName }}</v-app-bar-title>
    <v-btn @click="playGame()">
      <v-icon>mdi-play</v-icon>
      Play Game
    </v-btn>
  </v-toolbar>

  <v-table id="highScores">
    <thead>
      <tr>
        <th class="text-center">
          Username
        </th>
        <th class="text-center">
          Score
        </th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="item in sortedScores" :key="item.username">
        <td>{{ item.user }}</td>
        <td>{{ item.score }}</td>
      </tr>
    </tbody>
  </v-table>

</template>

<script>
import axios from 'axios';
export default {
  name: 'HighScores',
  props: ['gameName', 'user'],
  data () {
    return {
      scores: [],
    };
  },
  computed: {
    sortedScores() {
      return this.scores.sort((a, b) => {
        return b.score - a.score;
      });
    }
  },
  mounted() {
    this.init();
  },
  methods: {
    init() {
      const api = axios.create({
        baseURL: 'http://localhost:5000',
        headers: {
          'Content-Type': 'application/json',
        },
        timeout: 10000,
      });

      api.get('/scoresByGame/' + this.gameName).then((response) => {
        console.log(response.data);
        this.scores = response.data.result;
      }).catch((error) => {
        console.log(error);
      });

    },
    back() {
      this.$emit('changeState', 1);
    },
    playGame() {
      switch (this.gameName) {
        case 'Endless Runner':
          this.$emit('changeState', 100);
          break;
        case 'Balloon Madness':
          this.$emit('changeState', 101);
          break;
        case 'Chicken Invaders':
          this.$emit('changeState', 102);
          break;
        case 'Flappy Bird':
          this.$emit('changeState', 103);
          break;
      }
    },
  }
};
</script>

<style scoped>
#highScores {
  position: absolute;
  top: 10%;
  left: 0;
  right: 0;
  width: 100%;
}

#highScores td, #highScores th {
  border: 1px solid green;
  padding: 8px;
  text-align: center;
}

#highScores tr:nth-child(even) {
  background-color: #dddddd;
}

#highScores tr:hover {
  background-color: #ddd;
}

#highScores th {
  padding-top: 12px;
  padding-bottom: 12px;
  text-align: center;
  background-color: #4CAF50;
  color: white;
}
</style>
