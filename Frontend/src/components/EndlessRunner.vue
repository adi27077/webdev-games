<script setup>

</script>

<template>
  <v-toolbar style="position: absolute; top: 0; left: 0">
    <v-btn @click="back()">
      <v-icon>mdi-arrow-left</v-icon>
    </v-btn>
    <v-app-bar-title>{{ gameName }}</v-app-bar-title>
    <v-btn @click="highScores()">
      <v-icon>mdi-trophy</v-icon>
      High Scores
    </v-btn>
  </v-toolbar>

</template>

<script>
import * as THREE from 'three';
import { CSS2DObject, CSS2DRenderer } from 'three/examples/jsm/renderers/CSS2DRenderer.js';
import axios from "axios";

export default {
  name: 'EndlessRunner',
  props: ['gameName', 'user'],
  mounted() {
    this.init();
  },
  data () {
    return {
      scores: [],
      playerSpeed: 0.1,
      spawnPoint: new THREE.Vector3(8, -2, 0.1),
      keys: [],
      time: 0,
      sprites: [],
      obstacles: [],
      playerState: 0,
      playerCounter: 0,
      isJumping: false,
      airTime: 0,
      obstacleSpawnTime: 0,
      gameOver: false,
      score: 0,
      isPaused: false,
    };
  },
  methods: {
    back() {
      this.$emit('changeState', 1);
      document.body.removeChild(this.renderer.domElement);
      document.body.removeChild(this.labelRenderer.domElement);
    },
    highScores() {
      this.$emit('changeState', 10);
      document.body.removeChild(this.renderer.domElement);
      document.body.removeChild(this.labelRenderer.domElement);
    },
    init() {
      /* Get scores */
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

      /* Input event listeners */
      window.addEventListener('keydown', this.keyDown);
      window.addEventListener('keyup', this.keyUp);

      /* Get clock */
      this.clock = new THREE.Clock();

      /* Create Scene */
      this.scene = new THREE.Scene();

      /* Create Camera */
      this.camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
      this.camera.position.y = 1.5;
      this.camera.position.z = 5;
      this.camera.lookAt(0, 1, 0);

      /* Background */
      const loader = new THREE.TextureLoader();
      const bgTexture = loader.load('./src/assets/EndlessRunner/background2d.jpg');
      bgTexture.wrapS = THREE.RepeatWrapping;

      this.bgMesh = new THREE.Mesh(
          new THREE.PlaneGeometry(20, 10, 100, 100),
          new THREE.MeshBasicMaterial({ map: bgTexture })
      )

      this.bgMesh.position.y = 1;
      this.scene.add(this.bgMesh);

      /* Player */
      this.sprites.push(loader.load('./src/assets/EndlessRunner/1.png'));
      this.sprites.push(loader.load('./src/assets/EndlessRunner/2.png'));
      this.sprites.push(loader.load('./src/assets/EndlessRunner/3.png'));
      this.sprites.push(loader.load('./src/assets/EndlessRunner/4.png'));

      this.playerMesh = new THREE.Mesh(
          new THREE.PlaneGeometry(1, 1, 50, 50),
          new THREE.MeshBasicMaterial({ map: this.sprites[this.playerState], transparent: true })
      )

      this.playerMesh.position.x = -7;
      this.playerMesh.position.y = -2;
      this.playerMesh.position.z = 0.1;
      this.scene.add(this.playerMesh);

      /* Obstacles */
      this.rockTexture = loader.load('./src/assets/EndlessRunner/rock.png');
      this.treeTexture = loader.load('./src/assets/EndlessRunner/tree.png');

      const obstacleMesh = new THREE.Mesh(
          new THREE.PlaneGeometry(1, 1, 50, 50),
          new THREE.MeshBasicMaterial({ map: this.rockTexture, transparent: true })
      );

      obstacleMesh.position.x = this.spawnPoint.x;
      obstacleMesh.position.y = this.spawnPoint.y;
      obstacleMesh.position.z = this.spawnPoint.z;

      this.scene.add(obstacleMesh);
      this.obstacles.push(obstacleMesh);


      /* Text */
      this.timerDiv = document.createElement('div');
      this.timerDiv.id = 'timer';
      this.timerDiv.textContent = 'Time: 0';
      this.timerDiv.style.backgroundColor = 'transparent';
      this.timerDiv.style.fontSize = '30px';
      this.timerDiv.style.color = 'black';
      this.timerDiv.style.position = 'absolute';
      this.timerDiv.style.top = '10%';
      this.timerDiv.style.left = '5%';
      this.timerDiv.style.zIndex = '1';

      const timerLabel = new CSS2DObject(this.timerDiv);
      timerLabel.position.set(0, 0, 0);
      this.scene.add(timerLabel);
      timerLabel.layers.set(0);

      this.gameOverDiv = document.createElement('div');
      this.gameOverDiv.innerHTML = '';
      this.gameOverDiv.id = 'gameOver';
      this.gameOverDiv.style.display = 'none';
      this.gameOverDiv.style.backgroundColor = 'transparent';
      this.gameOverDiv.style.fontSize = '50px';
      this.gameOverDiv.style.color = 'black';
      this.gameOverDiv.style.textAlign = 'center';
      this.gameOverDiv.style.position = 'absolute';
      this.gameOverDiv.style.top = '50%';
      this.gameOverDiv.style.left = '40%';
      this.gameOverDiv.style.zIndex = '1';

      const gameOverLabel = new CSS2DObject(this.gameOverDiv);
      gameOverLabel.position.set(0, 0, 0);
      this.scene.add(gameOverLabel);
      gameOverLabel.layers.set(0);

      this.labelRenderer = new CSS2DRenderer();
      this.labelRenderer.setSize(window.innerWidth * 0.15, window.innerHeight * 0.1);
      this.labelRenderer.domElement.id = 'label';
      document.body.appendChild(this.labelRenderer.domElement);

      /* Setup */
      this.renderer = new THREE.WebGLRenderer({ antialias: true });
      this.renderer.setSize(window.innerWidth * 0.9, window.innerHeight * 0.9);
      document.body.appendChild(this.renderer.domElement);

      this.renderer.domElement.id = 'canvas';
      this.renderer.domElement.style.position = 'absolute';
      this.renderer.domElement.style.left = '5%';
      this.renderer.domElement.style.right = '5%';
      this.renderer.domElement.style.top = '10%';

      this.animate();
    },
    animate() {
      requestAnimationFrame(this.animate);

      this.deltaTime = this.clock.getDelta();

      if (this.gameOver) {
        this.playerSpeed = 0;

        if (this.keys['Space']) {
          this.gameOver = false;
          this.obstacles.forEach((obstacle) => {
            obstacle.material.dispose();
            obstacle.geometry.dispose();
            obstacle.removeFromParent();
          });

          cancelAnimationFrame(this.animate);

          this.playerSpeed = 0.1;
          this.spawnPoint = new THREE.Vector3(7, -2, 0.1);
          this.keys = [];
          this.time = 0;
          this.sprites = [];
          this.obstacles = [];
          this.playerState = 0;
          this.playerCounter = 0;
          this.isJumping = false;
          this.airTime = 0;
          this.obstacleSpawnTime = 0;
          this.gameOver = false;
          this.score = 0;

          document.body.removeChild(this.renderer.domElement);
          document.body.removeChild(this.labelRenderer.domElement);

          this.init();

        } else {
          return;
        }
      }

      if (!this.isPaused) {
        /* Background */
        this.bgMesh.material.map.offset.x += this.playerSpeed * this.deltaTime;

        /* Timer */
        this.time += this.deltaTime;
        this.timerDiv.textContent = 'Time: ' + this.time.toFixed(1);

        /* Player animation */
        this.playerCounter += this.deltaTime;
        if (this.playerCounter >= 0.5) {
          this.playerCounter = 0;
          this.playerState++;
          this.playerState %= 4;
          this.playerMesh.material.map = this.sprites[this.playerState];
        }

        /* Player movement */
        if (this.keys['KeyD']) {
          if (this.playerSpeed < 0.3) {
            this.playerSpeed += 5 * this.deltaTime;
          }
        } else {
          if (this.playerSpeed > 0.1) {
            this.playerSpeed -= 5 * this.deltaTime;
          }
        }

        if (this.keys['KeyW']) {
          if (this.playerMesh.position.y <= -2.0) {
            this.playerMesh.position.y += this.deltaTime * 12;
            this.isJumping = true;
          }
        }
        if (this.isJumping) {
          this.playerMesh.position.y += this.deltaTime * 12;
          if (this.playerMesh.position.y >= 1.0) {
            this.isJumping = false;
            this.airTime += this.deltaTime;
          }
        }
        if (this.airTime > 0) {
          this.airTime += this.deltaTime;
        }
        if (this.airTime > 0.5) {
          this.airTime = 0;
        }
        if (!this.isJumping && this.playerMesh.position.y > -2.0 && !this.airTime) {
          this.playerMesh.position.y -= this.deltaTime * 12;
          this.airTime = 0;
        }

        /* Obstacles */
        this.obstacleSpawnTime += this.deltaTime * this.playerSpeed * 10;
        if (this.obstacleSpawnTime > Math.random() * 2 + 3) {
          this.obstacleSpawnTime = 0;

          // Spawn a random obstacle
          const obstacleType = Math.floor(Math.random() * 2);
          let obstacleMesh;
          switch (obstacleType) {
            case 0:
              obstacleMesh = new THREE.Mesh(
                  new THREE.PlaneGeometry(1, 1, 50, 50),
                  new THREE.MeshBasicMaterial({ map: this.rockTexture, transparent: true })
              );
              obstacleMesh.position.y = 0;
              break;
            case 1:
              obstacleMesh = new THREE.Mesh(
                  new THREE.PlaneGeometry(1, 2, 50, 100),
                  new THREE.MeshBasicMaterial({ map: this.treeTexture, transparent: true })
              );
              obstacleMesh.position.y = 0.5;
              break;
          }

          obstacleMesh.position.x = this.spawnPoint.x;
          obstacleMesh.position.y += this.spawnPoint.y;
          obstacleMesh.position.z = this.spawnPoint.z;
          this.scene.add(obstacleMesh);
          this.obstacles.push(obstacleMesh);
        }

        for (const obstacle of this.obstacles) {
          obstacle.position.x -= this.playerSpeed * this.deltaTime * 15;
          if (obstacle.position.x < -7) {
            obstacle.material.dispose();
            obstacle.geometry.dispose();
            obstacle.removeFromParent();
            this.obstacles.shift();
          }
        }

        /* Collision */
        const playerBox = new THREE.Box3().setFromObject(this.playerMesh);
        for (const obstacle of this.obstacles) {
          const obstacleBox = new THREE.Box3().setFromObject(obstacle);
          if (playerBox.intersectsBox(obstacleBox)) {
            console.log('Collision');
            this.gameOver = true;
            this.gameOverDiv.innerHTML = `Game Over<br>Score: ${this.time.toFixed(1)}<br>Press Space to restart`;
            this.gameOverDiv.style.display = 'block';
            this.score = this.time.toFixed(1);
            this.updateScore();
          }
        }

        /* Pause */
        if (this.keys['Space']) {
          setTimeout(() => {
            this.isPaused = true;
            this.playerSpeed = 0;
            this.gameOverDiv.innerHTML = 'Paused<br>Press Space to resume';
            this.gameOverDiv.style.display = 'block';
          }, 50);

        }
      } else {
        if (this.keys['Space']) {
          setTimeout(() => {
            this.isPaused = false;
            this.playerSpeed = 0.1;
            this.gameOverDiv.innerHTML = '';
            this.gameOverDiv.style.display = 'none';
          }, 50);
        }
      }

      this.renderer.render(this.scene, this.camera);
      this.labelRenderer.render(this.scene, this.camera);
    },
    updateScore() {
      const api = axios.create({
        baseURL: 'http://localhost:5000',
        headers: {
          'Content-Type': 'application/json',
        },
        timeout: 10000,
      });

      let pos = -1;
      for (let i = 0; i < this.scores.length; i++) {
        if (this.scores[i].user === this.user && this.scores[i].game === this.gameName) {
          if (this.scores[i].score < this.score) {
            pos = i;
            break;
          } else {
            return;
          }
        }
      }

      if (pos === -1) {
        //POST
        api.post('/scores', {
          user: this.user,
          game: this.gameName,
          score: this.score,
        }).then((response) => {
          console.log(response.data);
          this.scores.push({
            user: this.user,
            game: this.gameName,
            score: this.score,
          });
        }).catch((error) => {
          console.log(error);
        });
      } else {
        //PUT
        api.put('/scores', {
          user: this.user,
          game: this.gameName,
          score: this.score,
        }).then((response) => {
          console.log(response.data);
          this.scores[pos].score = this.score;
        }).catch((error) => {
          console.log(error);
        });
      }

    },
    keyDown(event) {
      this.keys[event.code] = true;
    },
    keyUp(event) {
      this.keys[event.code] = false;
    }
  }
};

</script>

<style scoped>

</style>