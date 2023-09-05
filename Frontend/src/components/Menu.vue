<script setup>

</script>

<template>
  <v-toolbar style="position: absolute; top: 0; left: 0; height: 7%">
    <v-btn @click="logOut()">
      <v-icon>mdi-logout</v-icon>
    </v-btn>
    <v-btn @click="search()">
      <v-icon>mdi-magnify</v-icon>
    </v-btn>
    <v-text-field id="search" single-line hide-details @input="search()"></v-text-field>
  </v-toolbar>

  <v-container style="position: absolute; left: 5%; right: 5%; top: 7%; background: azure;">
    <v-row>
      <v-col v-for="i in count" :key="i" cols="3" :id="'element' + i">
        <v-card class="mx-auto" id="gameCard" max-width="400px" @click="selectGame(i)">
          <v-img :src="`http://localhost:5000/images/${games[i-1].image}`" height="200px" cover=""></v-img>
          <v-card-title>{{ games[i-1].title }}</v-card-title>
          <v-card-text>{{ games[i-1].description }}</v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import axios from 'axios';

export default {
  name: 'Menu',
  data() {
    return {
      games: [],
      count: 0
    };
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

      api.get('/games').then((response) => {
        console.log(response.data);
        this.games = response.data.result;
        this.count = this.games.length;
      }).catch((error) => {
        console.log(error);
      });
    },
    search() {
      for (let i = 0; i < this.count; i++) {
        console.log(this.games[i].title.toLowerCase().includes(document.getElementById('search').value.toLowerCase()));
        if (this.games[i].title.toLowerCase().includes(document.getElementById('search').value.toLowerCase())) {
          document.getElementById('element' + (i + 1)).style.display = 'block';
        } else {
          document.getElementById('element' + (i + 1)).style.display = 'none';
        }
      }
    },
    selectGame(index) {
      this.$emit('changeState', index + 99);
      this.$emit('selectedGame', this.games[index-1].title);
    },

    logOut() {
      this.$emit('changeState', 0);
    }
  }
};
</script>

<style scoped>
#gameCard {
  box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
}

#gameCard:hover {
  cursor: pointer;
  box-shadow: 0 8px 16px 0 rgba(0, 0, 0, 0.2);
}
</style>