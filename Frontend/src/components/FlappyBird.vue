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
import axios from 'axios';
import * as THREE from 'three';
import { CSS2DRenderer, CSS2DObject } from 'three/examples/jsm/renderers/CSS2DRenderer.js';

export default {
  name: 'FlappyBird',
  props: ['gameName', 'user'],
  mounted() {
    this.init();
  },
  data() {
    return {
      keys: [],
      score: 0,
      time: 0,
      scores: [],
      pipes: [],
      gameOver: false,
      isPaused: false,
    };
  },
  methods: {
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

      /* Create Scene */
      this.scene = new THREE.Scene();

      /* Input event listeners */
      window.addEventListener('keydown', this.keyDown);
      window.addEventListener('keyup', this.keyUp);
      window.addEventListener('resize', this.resize);

      /* Get clock */
      this.clock = new THREE.Clock();

      /* Create camera */
      this.camera = new THREE.OrthographicCamera(-window.innerWidth / 2, window.innerWidth / 2, window.innerHeight / 2, -window.innerHeight / 2, 1, 1000);
      this.camera.position.set(0, 0, 10);
      this.camera.lookAt(0, 0, 0);

      /* Create background */
      const loader = new THREE.TextureLoader();
      this.scene.background = loader.load('./src/assets/FlappyBird/flappy-bird-background.jpg');
      this.scene.background.wrapS = THREE.MirroredRepeatWrapping;

      /* Create bird */
      const birdTexture = loader.load('./src/assets/FlappyBird/bird.png');
      this.birdMesh = new THREE.Mesh(
          new THREE.PlaneGeometry(1, 1),
          new THREE.MeshBasicMaterial({ map: birdTexture, transparent: true })
      );
      this.birdMesh.position.set(-window.innerWidth / 2 + 200, 0, 0);
      this.birdMesh.scale.set(120, 120, 1);
      this.scene.add(this.birdMesh);

      /* Physics */
      this.gravity = 1000;
      this.birdFallSpeed = 0;
      this.birdForce = 0;

      /* Pipes */
      this.pipeSpeed = 200;
      this.pipeSpawnX = window.innerWidth / 2 + 100;
      this.pipeSpawnTimer = 0;
      this.pipeSpawnTimerMax = 2.5;
      this.pipeGap = 300;
      this.pipeWidth = 100;
      this.pipeHeight = 900;
      this.pipeUpTexture = loader.load('./src/assets/FlappyBird/pipe.png');
      this.pipeDownTexture = loader.load('./src/assets/FlappyBird/pipe.png');
      this.pipeDownTexture.flipY = false;
      const pipeUpMesh = new THREE.Mesh(
          new THREE.PlaneGeometry(1, 1),
          new THREE.MeshBasicMaterial({ map: this.pipeUpTexture, transparent: true })
      );
      pipeUpMesh.scale.set(this.pipeWidth, this.pipeHeight, 1);
      pipeUpMesh.position.set(this.pipeSpawnX, -window.innerHeight / 2, 0);
      const pipeDownMesh = new THREE.Mesh(
          new THREE.PlaneGeometry(1, 1),
          new THREE.MeshBasicMaterial({ map: this.pipeDownTexture, transparent: true })
      );
      pipeDownMesh.scale.set(this.pipeWidth, this.pipeHeight, 1);
      pipeDownMesh.position.set(this.pipeSpawnX, -window.innerHeight / 2 + this.pipeGap + this.pipeHeight, 0);
      const betweenPipesMesh = new THREE.Mesh(
          new THREE.PlaneGeometry(1, 1),
          new THREE.MeshBasicMaterial({ color: 0x000000, transparent: true, opacity: 0 })
      );
      betweenPipesMesh.scale.set(this.pipeWidth, this.pipeGap, 1);
      betweenPipesMesh.position.set(this.pipeSpawnX, -window.innerHeight / 2 + this.pipeGap * 2, 0);
      this.pipes.push({
        up: pipeUpMesh,
        between: betweenPipesMesh,
        down: pipeDownMesh,
      });
      this.scene.add(pipeUpMesh);
      this.scene.add(pipeDownMesh);
      this.scene.add(betweenPipesMesh);


      /* UI Renderer */
      this.scoreDiv = document.createElement('div');
      this.scoreDiv.id = 'score';
      this.scoreDiv.textContent = 'Score: 0';
      this.scoreDiv.style.background = 'transparent';
      this.scoreDiv.style.fontSize = '30px';
      this.scoreDiv.style.color = 'black';
      this.scoreDiv.style.textAlign = 'left';
      this.scoreDiv.style.position = 'absolute';
      this.scoreDiv.style.top = '10%';
      this.scoreDiv.style.left = '5%';
      this.scoreDiv.style.zIndex = '1';
      const scoreLabel = new CSS2DObject(this.scoreDiv);
      scoreLabel.position.set(0, 0, 0);
      this.scene.add(scoreLabel);
      scoreLabel.layers.set(0);

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
      this.labelRenderer.domElement.id = 'labelRenderer';
      document.body.appendChild(this.labelRenderer.domElement);

      /* Renderer Setup */
      this.renderer = new THREE.WebGLRenderer({ antialias: true });
      this.renderer.setSize(window.innerWidth * 0.9, window.innerHeight * 0.9);
      document.body.appendChild(this.renderer.domElement);

      this.renderer.domElement.id = 'canvas';
      this.renderer.domElement.style.position = 'absolute';
      this.renderer.domElement.style.top = '10%';
      this.renderer.domElement.style.left = '5%';
      this.renderer.domElement.style.right = '5%';
      this.renderer.domElement.style.zIndex = '0';

      /* Mouse */
      this.renderer.domElement.addEventListener('mousemove', this.mouseMove);
      this.renderer.domElement.addEventListener('click', this.mouseClick);

      this.animate();
    },
    animate() {
      requestAnimationFrame(this.animate);

      this.delta = this.clock.getDelta();
      this.time += this.delta;

      /* Game over */
      if (this.gameOver) {
        if (this.keys['Space']) {
          console.log('reset');
          this.reset();
        } else {
          return;
        }
      }

      if (!this.isPaused) {
        /* Background */
        this.scene.background.offset.x += 0.04 * this.delta;

        /* Bird */
        this.birdFallSpeed += (this.gravity - this.birdForce) * this.delta;
        this.birdMesh.position.y -= this.birdFallSpeed  * this.delta;

        /* Speed */
        this.time += this.delta;
        if (this.time > 10) {
          this.pipeSpeed += 10;
          this.time = 0;
        }

        /* Pipes */
        for (const pipe of this.pipes) {
          for (const mesh in pipe) {
            if(pipe[mesh]) {
              pipe[mesh].position.x -= this.pipeSpeed * this.delta;
            }
          }

          if (pipe.up.position.x < -window.innerWidth / 2 - this.pipeWidth) {
            pipe.up.geometry.dispose();
            pipe.up.material.dispose();
            this.scene.remove(pipe.up);
            pipe.down.geometry.dispose();
            pipe.down.material.dispose();
            this.scene.remove(pipe.down);
            this.pipes.splice(this.pipes.indexOf(pipe), 1);
          }
        }

        /* Pipe spawn */
        this.pipeSpawnTimer += this.delta;
        if (this.pipeSpawnTimer > this.pipeSpawnTimerMax) {
          this.pipeSpawnTimer = 0;
          this.pipeSpawnTimerMax = (Math.random() / 2 + 2) / (this.pipeSpeed / 200);

          const pipeYOffset = Math.random() * (200 + 300) - 300;

          const pipeUpMesh = new THREE.Mesh(
              new THREE.PlaneGeometry(1, 1),
              new THREE.MeshBasicMaterial({ map: this.pipeUpTexture, transparent: true })
          );
          pipeUpMesh.scale.set(this.pipeWidth, this.pipeHeight, 1);
          pipeUpMesh.position.set(this.pipeSpawnX, -window.innerHeight / 2 + pipeYOffset, 0);
          const pipeDownMesh = new THREE.Mesh(
              new THREE.PlaneGeometry(1, 1),
              new THREE.MeshBasicMaterial({ map: this.pipeDownTexture, transparent: true })
          );
          pipeDownMesh.scale.set(this.pipeWidth, this.pipeHeight, 1);
          pipeDownMesh.position.set(this.pipeSpawnX, -window.innerHeight / 2 + this.pipeGap + this.pipeHeight + pipeYOffset, 0);
          const betweenPipesMesh = new THREE.Mesh(
              new THREE.PlaneGeometry(1, 1),
              new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0 })
          );
          betweenPipesMesh.scale.set(this.pipeWidth, this.pipeGap, 1);
          betweenPipesMesh.position.set(this.pipeSpawnX, -window.innerHeight / 2 + this.pipeGap * 2 + pipeYOffset, 0);
          this.pipes.push({
            up: pipeUpMesh,
            between: betweenPipesMesh,
            down: pipeDownMesh,
          });
          this.scene.add(pipeUpMesh);
          this.scene.add(pipeDownMesh);
          this.scene.add(betweenPipesMesh);
        }

        /* Gap collision */
        const birdBox = new THREE.Box3().setFromObject(this.birdMesh);
        birdBox.expandByVector(new THREE.Vector3(-50, -50, 0));
        for (const pipe of this.pipes) {
          if (!pipe.between) {
            continue;
          }
          const pipeBox = new THREE.Box3().setFromObject(pipe.between);
          if (birdBox.intersectsBox(pipeBox)) {
            this.score++;
            this.scoreDiv.textContent = 'Score: ' + this.score;
            pipe.between.geometry.dispose();
            pipe.between.material.dispose();
            pipe.between.removeFromParent();
            pipe.between = null;
            delete pipe.between;
            this.scene.remove(pipe.between);
            break;
          }
        }

        /* Pipe collision */
        for (const pipe of this.pipes) {
          for (const mesh in pipe) {
            if(pipe[mesh]) {
              const pipeBox = new THREE.Box3().setFromObject(pipe[mesh]);
              if (birdBox.intersectsBox(pipeBox)) {
                this.gameOver = true;
                this.gameOverDiv.innerHTML = 'Game Over<br>Press Space to restart';
                this.gameOverDiv.style.display = 'block';
                this.updateScore();
                break;
              }
            }
          }
        }

        /* Ground collision */
        if (this.birdMesh.position.y < -window.innerHeight / 2) {
          this.gameOver = true;
          this.gameOverDiv.innerHTML = 'Game Over<br>Press Space to restart';
          this.gameOverDiv.style.display = 'block';
          this.updateScore();
        }

        /* Input */
        if (this.keys['Space'] && this.birdMesh.position.y < window.innerHeight / 2) {
          this.birdFallSpeed = 0;
          this.birdForce = 75000;
        } else {
          if (this.birdForce > 0) {
            this.birdForce = 0;
          }
        }

        /* Pause */
        if (this.keys['KeyP']) {
          setTimeout(() => {
            this.isPaused = true;
            this.gameOverDiv.innerHTML = 'Paused<br>Press Space to resume';
            this.gameOverDiv.style.display = 'block';
          }, 50);
        }
      } else {
        if (this.keys['Space']) {
          setTimeout(() => {
            this.isPaused = false;
            this.gameOverDiv.innerHTML = '';
            this.gameOverDiv.style.display = 'none';
          }, 50);
        }
      }

      this.renderer.render(this.scene, this.camera);
      this.labelRenderer.render(this.scene, this.camera);
    },
    keyDown(event) {
      this.keys[event.code] = true;
    },
    keyUp(event) {
      this.keys[event.code] = false;
    },
    resize() {
      this.camera.aspect = window.innerWidth / window.innerHeight;
      this.camera.updateProjectionMatrix();

      this.renderer.setSize(window.innerWidth * 0.9, window.innerHeight * 0.9);
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
    reset() {
      cancelAnimationFrame(this.animate);

      this.keys = [];
      this.score = 0;
      this.pipes = [];
      this.isPaused = false;
      this.gameOver = false;

      document.body.removeChild(this.renderer.domElement);
      document.body.removeChild(this.labelRenderer.domElement);
      this.renderer.dispose();

      this.init();
    },
    back() {
      this.$emit('changeState', 1);
      this.renderer.dispose();
      document.body.removeChild(this.renderer.domElement);
      document.body.removeChild(this.labelRenderer.domElement);
    },
    highScores() {
      this.$emit('changeState', 10);
      this.renderer.dispose();
      document.body.removeChild(this.renderer.domElement);
      document.body.removeChild(this.labelRenderer.domElement);
    },
  }
};

</script>

<style scoped>

</style>