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
  name: 'ChickenInvaders',
  props: ['gameName', 'user'],
  mounted() {
    this.init();
  },
  data() {
    return {
      keys: [],
      mouseX: -1,
      mouseY: -1,
      score: 0,
      level: 0,
      difficulty: 1,
      chickens: [],
      bullets: [],
      eggs: [],
      pickups: [],
      time: 0,
      isPaused: false,
      gameOver: false,
      scores: [],
    }
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

      /* Create Camera */
      this.camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
      this.camera.position.y = 1.5;
      this.camera.position.z = 5;
      this.camera.lookAt(0, 1, 0);

      /* Background */
      const loader = new THREE.TextureLoader();
      this.scene.background = loader.load('./src/assets/ChickenInvaders/space.jpg');
      this.scene.background.wrapT = THREE.MirroredRepeatWrapping;

      /* Spaceship */
      const spaceshipTexture = loader.load('./src/assets/ChickenInvaders/spaceship.png');
      this.spaceship = new THREE.Mesh(
          new THREE.PlaneGeometry(1, 1),
          new THREE.MeshBasicMaterial({ map: spaceshipTexture, transparent: true })
      );
      this.spaceship.position.y = -2;
      this.spaceship.position.z = 0.1;
      this.spaceship.scale.set(2, 2, 2);
      this.scene.add(this.spaceship);

      /* Chickens */
      this.spawnChickens();

      /* UI Renderer */
      this.scoreDiv = document.createElement('div');
      this.scoreDiv.id = 'score';
      this.scoreDiv.textContent = 'Score: 0';
      this.scoreDiv.style.background = 'transparent';
      this.scoreDiv.style.fontSize = '30px';
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
    spawnChickens() {
      this.loader = new THREE.TextureLoader();
      const chickenTexture = this.loader.load('./src/assets/ChickenInvaders/chicken.png');
      const chickenGeometry = new THREE.PlaneGeometry(1, 1);
      const chickenMaterial = new THREE.MeshBasicMaterial({ map: chickenTexture, transparent: true });

      for (let i = 0; i < 10; i++) {
        const chicken = new THREE.Mesh(chickenGeometry, chickenMaterial);
        chicken.position.x = -5 + (i * 1.2);
        chicken.position.y = 4;
        chicken.position.z = 0.1;
        chicken.scale.set(0.6, 0.6, 0.6);
        chicken.hp = (this.difficulty * 2 + this.difficulty * this.level) / 2;
        this.chickens.push(chicken);
        this.scene.add(chicken);
      }

      for (let i = 0; i < 10; i++) {
        const chicken = new THREE.Mesh(chickenGeometry, chickenMaterial);
        chicken.position.x = -5 + (i * 1.2);
        chicken.position.y = 3;
        chicken.position.z = 0.1;
        chicken.scale.set(0.6, 0.6, 0.6);
        chicken.hp = (this.difficulty * 2 + this.difficulty * this.level) / 2;
        this.chickens.push(chicken);
        this.scene.add(chicken);
      }

      for (let i = 0; i < 10; i++) {
        const chicken = new THREE.Mesh(chickenGeometry, chickenMaterial);
        chicken.position.x = -5 + (i * 1.2);
        chicken.position.y = 2;
        chicken.position.z = 0.1;
        chicken.scale.set(0.6, 0.6, 0.6);
        chicken.hp = (this.difficulty * 2 + this.difficulty * this.level) / 2;
        this.chickens.push(chicken);
        this.scene.add(chicken);
      }

      /* Clear bullets */
      for (const bullet of this.bullets) {
        bullet.geometry.dispose();
        bullet.material.dispose();
        bullet.removeFromParent();
        this.scene.remove(bullet);
      }
      this.bullets = [];
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
        if (this.level < 0) {
          this.gameOver = true;
          this.gameOverDiv.innerHTML = 'Game Over<br>Score: ' + this.score + '<br>Press Space to restart';
          this.gameOverDiv.style.display = 'block';
          this.updateScore();
          return;
        }

        /* Background */
        this.scene.background.offset.y += 0.02 * this.delta;

        /* Bullets movement */
        for (const bullet of this.bullets) {
          bullet.alive -= this.delta;
          if (bullet.alive <= 0) {
            bullet.geometry.dispose();
            bullet.material.dispose();
            bullet.removeFromParent();
            this.scene.remove(bullet);
            this.bullets.splice(this.bullets.indexOf(bullet), 1);
          } else {
            bullet.position.y += 1.5 * this.delta;
          }
        }

        /* Chickens */
        if (this.chickens.length === 0) {
          this.difficulty *= 2;
          this.spawnChickens();
        }
        for (const chicken of this.chickens) {
          if (chicken.hp <= 0) {
            chicken.geometry.dispose();
            chicken.material.dispose();
            chicken.removeFromParent();
            this.scene.remove(chicken);
            this.chickens.splice(this.chickens.indexOf(chicken), 1);
            this.score += Math.log2(this.difficulty) + 1;
            this.scoreDiv.textContent = `Score: ${this.score}`;

            /* Chance to drop pickup */
            if (this.level < 3 && Math.random() * (this.level + 1) < 0.1) {
              const pickupTexture = this.loader.load('./src/assets/ChickenInvaders/atom.png');
              const pickup = new THREE.Mesh(
                  new THREE.PlaneGeometry(1, 1),
                  new THREE.MeshBasicMaterial({ map: pickupTexture, transparent: true })
              );
              pickup.position.x = chicken.position.x;
              pickup.position.y = chicken.position.y;
              pickup.position.z = 0.1;
              pickup.scale.set(0.6, 0.6, 0.6);
              this.pickups.push(pickup);
              this.scene.add(pickup);
            }
          } else {

          }
        }

        /* Chickens movement */
        for (const chicken of this.chickens) {
          if (Math.floor(this.time / 2) % 2 === 0) {
            chicken.position.x += 0.4 * this.delta;
          } else {
            chicken.position.x -= 0.4 * this.delta;
          }
        }

        /* Pickups */
        for (const pickup of this.pickups) {
          pickup.position.y -= 1 * this.delta;
          if (pickup.position.y < -4) {
            pickup.geometry.dispose();
            pickup.material.dispose();
            pickup.removeFromParent();
            this.scene.remove(pickup);
            this.pickups.splice(this.pickups.indexOf(pickup), 1);
          }
        }

        /* Eggs */
        if (Math.random() < 0.003 * this.difficulty * this.chickens.length / 30) {
          const eggTexture = this.loader.load('./src/assets/ChickenInvaders/Egg.png');
          const egg = new THREE.Mesh(
              new THREE.PlaneGeometry(1, 1),
              new THREE.MeshBasicMaterial({ map: eggTexture, transparent: true })
          );
          const chickenIndex = Math.floor(Math.random() * this.chickens.length);
          egg.position.x = this.chickens[chickenIndex].position.x;
          egg.position.y = this.chickens[chickenIndex].position.y;
          egg.position.z = 0.1;
          egg.scale.set(0.2, 0.25, 1);
          this.eggs.push(egg);
          this.scene.add(egg);
        }

        /* Eggs movement */
        for (const egg of this.eggs) {
          egg.position.y -= 1 * this.delta;
          if (egg.position.y < -4) {
            egg.geometry.dispose();
            egg.material.dispose();
            egg.removeFromParent();
            this.scene.remove(egg);
            this.eggs.splice(this.eggs.indexOf(egg), 1);
          }
        }

        /* Bullet collision */
        for (const bullet of this.bullets) {
          this.bulletCollision(bullet);
        }

        /* Pickup collision */
        for (const pickup of this.pickups) {
          const pickupBox = new THREE.Box3().setFromObject(pickup);
          const spaceshipBox = new THREE.Box3().setFromObject(this.spaceship);
          spaceshipBox.expandByVector(new THREE.Vector3(-0.4, -0.4, 0));
          if (pickupBox.intersectsBox(spaceshipBox)) {
            pickup.geometry.dispose();
            pickup.material.dispose();
            pickup.removeFromParent();
            this.scene.remove(pickup);
            this.pickups.splice(this.pickups.indexOf(pickup), 1);
            if (this.level < 3) {
              this.level++;
            }
          }
        }

        /* Egg collision */
        const spaceshipBox = new THREE.Box3().setFromObject(this.spaceship);
        spaceshipBox.expandByVector(new THREE.Vector3(-0.4, -0.4, 0));
        for (const egg of this.eggs) {
          const eggBox = new THREE.Box3().setFromObject(egg);
          if (eggBox.intersectsBox(spaceshipBox)) {
            egg.geometry.dispose();
            egg.material.dispose();
            egg.removeFromParent();
            this.scene.remove(egg);
            this.eggs.splice(this.eggs.indexOf(egg), 1);
            this.level--;
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
    bulletCollision(bullet) {
      let removed = false;
      const bulletBox = new THREE.Box3().setFromObject(bullet);
      for (const chicken of this.chickens) {
        const chickenBox = new THREE.Box3().setFromObject(chicken);
        if (bulletBox.intersectsBox(chickenBox)) {
          chicken.hp -= 2 ** bullet.level;
          if (!removed) {
            bullet.geometry.dispose();
            bullet.material.dispose();
            bullet.removeFromParent();
            this.scene.remove(bullet);
            this.bullets.splice(this.bullets.indexOf(bullet), 1);
            removed = true;
          }
        }
      }
    },
    shoot() {
      const loader = new THREE.TextureLoader();
      const bulletTexture = loader.load(`./src/assets/ChickenInvaders/ionlv${this.level + 1}.png`);
      const bullet = new THREE.Mesh(
          new THREE.PlaneGeometry(1, 1),
          new THREE.MeshBasicMaterial({ map: bulletTexture, transparent: true })
      );

      bullet.position.x = this.spaceship.position.x;
      bullet.position.y = this.spaceship.position.y + 1;
      bullet.position.z = 0.1;
      if (this.level === 0) {
        bullet.scale.set(0.3, 1, 0.3);
      } else if (this.level === 1) {
        bullet.scale.set(0.6, 1, 0.6);
      } else if (this.level === 2) {
        bullet.scale.set(0.9, 1, 0.9);
      } else if (this.level === 3) {
        bullet.scale.set(1.2, 1, 1.2);
      }

      bullet.level = this.level;
      bullet.alive = 4;

      this.bullets.push(bullet);
      this.scene.add(bullet);
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
    mouseMove(event) {
      event.preventDefault();

      if (this.isPaused) {
        return;
      }

      this.mouseX = (event.clientX / window.innerWidth) * 2 - 1;
      this.mouseY = -(event.clientY / window.innerHeight) * 2 + 1;

      const vector = new THREE.Vector3(this.mouseX, this.mouseY, 0.1);
      vector.unproject(this.camera);

      this.spaceship.position.x = vector.x * 25;
    },
    mouseClick(event) {
      event.preventDefault();

      if (this.isPaused) {
        return;
      }

      if (event.button === 0) {
        this.shoot();
      }
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
      this.mouseX = -1;
      this.mouseY = -1;
      this.score = 0;
      this.level = 0;
      this.difficulty = 1;
      this.chickens = [];
      this.bullets = [];
      this.eggs = [];
      this.pickups = [];
      this.time = 0;
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
  },
};

</script>

<style scoped>

</style>