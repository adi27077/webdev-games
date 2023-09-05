<script setup>

</script>

<template>
  <div class="container">
    <h1> Sign in </h1>
    <label><b>Username:</b></label>
    <label>
      <input type="text" placeholder="Enter Username" id="username">
    </label>
    <br>
    <label><b>Password:</b></label>
    <label>
      <input type="password" placeholder="Enter Password" id="password">
    </label>
    <p id="error"></p>
    <br>
    <button type="submit" @click="mainMenu()">Login</button>
    <button @click="register()">Register</button>
    <button @click="forgotPassword()">Forgot Password?</button>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'Login',
  methods: {
    mainMenu() {
      const api = axios.create({
        baseURL: 'http://localhost:5000',
        headers: {
          'Content-Type': 'application/json',
        },
        timeout: 10000,
      });

      if (document.getElementById('username').value && document.getElementById('password').value) {
        const credentials = {
          username: document.getElementById('username').value,
          password: document.getElementById('password').value,
        };

        api.post('/login', credentials).then((response) => {
          console.log(response.data);
          if (response.status === 200) {
            this.$emit('changeState', 1);
            this.$emit('loggedIn', response.data.username);
          }
        }).catch((error) => {
          console.log(error);
          document.getElementById('error').textContent = error.response.data.result;

          setTimeout(() => {
            document.getElementById('error').textContent = '';
          }, 1000);
        });
      } else {
        document.getElementById('error').textContent = 'Please enter a username and password.';

        setTimeout(() => {
          document.getElementById('error').textContent = '';
        }, 1000);
      }
    },
    register() {
      this.$emit('changeState', 2);
    },
    forgotPassword() {
      this.$emit('changeState', 3);
    }
  }
};
</script>

<style scoped>
button {
  background-color: #0ed243;
  color: white;
  width: 100%;
  border: none;
  cursor: pointer;
  padding: 14px 20px;
  margin: 8px;
}

button:hover {
  opacity: 0.8;
}

input {
  width: 100%;
  padding: 12px 20px;
  margin: 8px;
  box-sizing: border-box;
  background: white;
}

#error {
  color: red;
  display: table;
  margin: auto 0;
}
</style>