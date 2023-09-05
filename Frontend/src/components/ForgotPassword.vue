<script setup>

</script>

<template>
  <div class="container">
    <h1> Reset Password </h1>
    <label><b>Username:</b></label>
    <label>
      <input type="text" placeholder="Enter Username" id="username">
    </label>
    <br>
    <label><b>New Password:</b></label>
    <label>
      <input type="password" placeholder="Enter New Password" id="password">
    </label>
    <label><b>Confirm New Password:</b></label>
    <label>
      <input type="password" placeholder="Enter Password" id="confirmPassword">
    </label>
    <p id="error"></p>
    <br>
    <button type="submit" @click="resetPassword()">Confirm</button>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'ForgotPassword',
  methods: {
    resetPassword() {
      const api = axios.create({
        baseURL: 'http://localhost:5000',
        headers: {
          'Content-Type': 'application/json',
        },
        timeout: 10000,
      });

      if (document.getElementById('username').value && document.getElementById('password').value && document.getElementById('confirmPassword').value) {
        if (document.getElementById('password').value !== document.getElementById('confirmPassword').value) {
          document.getElementById('error').textContent = 'Passwords do not match.';

          setTimeout(() => {
            document.getElementById('error').textContent = '';
          }, 1000);

          return;
        }

        const credentials = {
          username: document.getElementById('username').value,
          password: document.getElementById('password').value,
        };

        api.put('/reset_password', credentials).then((response) => {
          console.log(response.data);
          if (response.status === 200) {
            document.getElementById('error').textContent = 'Password reset successfully.';
            document.getElementById('error').style.color = 'green';

            setTimeout(() => {
              document.getElementById('error').textContent = '';
              this.$emit('changeState', 0);
            }, 1000);
          }
        }).catch((error) => {
          console.log(error);
          document.getElementById('error').textContent = error.response.data.result;

          setTimeout(() => {
            document.getElementById('error').textContent = '';
          }, 1000);
        });

      } else {
        document.getElementById('error').textContent = 'Please fill in all fields.';

        setTimeout(() => {
          document.getElementById('error').textContent = '';
        }, 1000);
      }
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