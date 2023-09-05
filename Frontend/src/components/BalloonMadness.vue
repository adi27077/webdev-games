<!--suppress JSCheckFunctionSignatures -->
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
import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader';
import { MTLLoader } from 'three/examples/jsm/loaders/MTLLoader';

export default {
  name: 'BalloonMadness',
  props: ['gameName', 'user'],
  mounted() {
    this.init();
  },
  data() {
    return {
      keys: [],
      gun: [],
      mouseX: -1,
      mouseY: -1,
      bullets: [],
      balloons: [],
      time: 60,
      score: 0,
      isPaused: false,
      gameOver: false,
      scores: [],
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

      /* Create Camera */
      this.camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
      this.camera.position.y = 1.5;
      this.camera.position.z = 5;
      this.camera.lookAt(0, 1, 0);

      /* Light */
      this.ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
      this.scene.add(this.ambientLight);

      this.light = new THREE.PointLight(0xffffff, 200, 50);
      this.light.position.set(-3, 10, -3);
      this.light.castShadow = true;
      this.light.shadow.camera.near = 0.1;
      this.light.shadow.camera.far = 25;
      this.scene.add(this.light);

      /* Sky */
      const textureLoader = new THREE.TextureLoader();
      const skyTexture = textureLoader.load('./src/assets/BalloonMadness/cumulus-cloud.jpg');
      const skyMesh = new THREE.Mesh(
        new THREE.PlaneGeometry(100, 50, 1000, 1000),
        new THREE.MeshPhongMaterial({map: skyTexture})
      );
      skyMesh.geometry.computeVertexNormals();

      skyMesh.position.y = -0.5;
      skyMesh.receiveShadow = false;
      this.scene.add(skyMesh);

      /* Ground */
      const groundTexture = textureLoader.load('./src/assets/BalloonMadness/grass.jpg', () => {
        groundTexture.wrapS = groundTexture.wrapT = THREE.RepeatWrapping;
        groundTexture.offset.set(0, 0);
        groundTexture.repeat.set(100, 100);
      });
      const groundMesh = new THREE.Mesh(
        new THREE.PlaneGeometry(100, 50, 1000, 1000),
        new THREE.MeshPhongMaterial({map: groundTexture})
      );
      groundMesh.geometry.computeVertexNormals();

      groundMesh.rotation.x = -Math.PI / 2;
      groundMesh.position.y = -0.5;
      groundMesh.receiveShadow = true;
      this.scene.add(groundMesh);

      /* Walls */
      const wallTexture = textureLoader.load('./src/assets/BalloonMadness/crate0_diffuse.png');
      this.placeWall(wallTexture, 0, 0, 1, 5, 8, 1);
      this.placeWall(wallTexture, 0, 0, 4, 5, 1, 1);

      /* Gun */
      this.drawGun();

      /* Balloons */
      for (let i = 0; i < 10; i++) {
        this.drawBalloon();
      }

      /* UI Renderer */
      this.timerDiv = document.createElement('div');
      this.timerDiv.id = 'timer';
      this.timerDiv.textContent = 'Time: 0';
      this.timerDiv.style.background = 'transparent';
      this.timerDiv.style.fontSize = '30px';
      this.timerDiv.style.textAlign = 'left';
      this.timerDiv.style.position = 'absolute';
      this.timerDiv.style.top = '10%';
      this.timerDiv.style.left = '5%';
      this.timerDiv.style.zIndex = '1';
      const timerLabel = new CSS2DObject(this.timerDiv);
      timerLabel.position.set(0, 0, 0);
      this.scene.add(timerLabel);
      timerLabel.layers.set(0);

      this.scoreDiv = document.createElement('div');
      this.scoreDiv.id = 'score';
      this.scoreDiv.textContent = 'Score: 0';
      this.scoreDiv.style.background = 'transparent';
      this.scoreDiv.style.fontSize = '30px';
      this.scoreDiv.style.textAlign = 'left';
      this.scoreDiv.style.position = 'absolute';
      this.scoreDiv.style.top = '15%';
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
    placeWall(texture, x, y, z, sx, sy, sz) {
      const wallMesh = new THREE.Mesh(
        new THREE.BoxGeometry(sx, sy, sz),
        new THREE.MeshPhongMaterial({map: texture})
      );
      wallMesh.geometry.computeVertexNormals();

      wallMesh.position.set(x, y, z);
      wallMesh.castShadow = true;
      wallMesh.receiveShadow = true;
      this.scene.add(wallMesh);
    },
    drawGun() {
      const scene = this.scene;
      const camera = this.camera;
      const gun = this.gun;

      const mtlLoader = new MTLLoader();
      mtlLoader.load('./src/assets/BalloonMadness/uziGold.mtl', (materials) => {
        materials.preload();

        const objLoader = new OBJLoader();
        objLoader.setMaterials(materials);
        objLoader.load('./src/assets/BalloonMadness/uziGold.obj', (object) => {
          object.position.set(camera.position.x, camera.position.y - 0.5, camera.position.z - 0.5);
          object.scale.setScalar(10);
          object.rotation.set(camera.rotation.x, camera.rotation.y - Math.PI, camera.rotation.z);
          object.castShadow = true;
          object.receiveShadow = true;
          scene.add(object);
          gun.push(object);
        });
      });
    },
    animate() {
      requestAnimationFrame(this.animate);

      this.delta = this.clock.getDelta();

      if (this.gameOver) {
        if (this.keys['Space']) {
          console.log('reset');
          this.reset();
        } else {
          return;
        }
      }

      if (!this.isPaused) {
        /* Timer */
        this.time -= this.delta;
        if (this.time < 10) {
          this.timerDiv.style.color = 'red';
        }
        this.timerDiv.textContent = 'Time: ' + this.time.toFixed(2);

        if (this.time < 0) {
          this.timerDiv.textContent = 'Time: 0';
          this.gameOver = true;
          this.gameOverDiv.innerHTML = 'Game Over<br>Score: ' + this.score + '<br>Press Space to restart';
          this.gameOverDiv.style.display = 'block';
          this.updateScore();
          return;
        }


        /* Balloons */
        for (const balloon of this.balloons) {
          balloon.position.y += balloon.speed * this.delta;

          if (balloon.position.y > 3) {
            balloon.position.set(
                Math.random() * (1.75 + 1.75) - 1.75,
                Math.random() * 0.25 - 0.25,
                Math.random() * (3.5 - 1.5) + 1.5
            );
            balloon.scale.setScalar(Math.random() * (0.75 - 0.25) + 0.25);
            balloon.speed = Math.random() * (1 - 0.5) + 0.5;
          }
        }

        /* Bullets */
        for (const bullet of this.bullets) {
          bullet.alive -= this.delta;
          if (bullet.alive < 0) {
            bullet.material.dispose();
            bullet.geometry.dispose();
            bullet.removeFromParent();
            this.scene.remove(bullet);
            this.bullets.splice(this.bullets.indexOf(bullet), 1);
          }
        }

        /* Bullet movement */
        for (const bullet of this.bullets) {
          bullet.position.set(
              bullet.position.x + bullet.direction.x * this.delta * 4,
              bullet.position.y + bullet.direction.y * this.delta * 4,
              bullet.position.z + bullet.direction.z * this.delta * 4
          );
        }

        /* Collisions */
        for (const balloon of this.balloons) {
          this.checkCollision(balloon);
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

      if (this.mouseX === -1 && this.mouseY === -1) {
        this.mouseX = event.clientX;
        this.mouseY = event.clientY;
      }

      const vec = new THREE.Vector3(
        (event.clientX / window.innerWidth) * 2 - 1,
        -(event.clientY / window.innerHeight) * 2 + 1,
        0.5
      );

      vec.unproject(this.camera);
      vec.sub(this.camera.position).normalize();

      const distance = (-5 - this.camera.position.z) / vec.z;
      const pos = this.camera.position.clone().add(vec.multiplyScalar(distance));

      this.gun[0].lookAt(pos);
      this.direction = new THREE.Vector3(
        pos.x - this.gun[0].position.x,
        pos.y - this.gun[0].position.y,
        pos.z - this.gun[0].position.z
      );
      this.direction.normalize();
    },
    mouseClick(event) {
      event.preventDefault();

      if (this.isPaused) {
        return;
      }

      if (event.button === 0) {
        this.createBullet();
      }
    },
    createBullet() {
      const bullet = new THREE.Mesh(
        new THREE.SphereGeometry(0.025, 10, 10),
        new THREE.MeshPhongMaterial({color: 0xf7f7f7})
      );

      bullet.position.set(this.gun[0].position.x, this.gun[0].position.y + 0.15, this.gun[0].position.z);

      bullet.castShadow = true;
      bullet.receiveShadow = true;
      bullet.direction = this.direction;
      bullet.alive = 2;
      this.scene.add(bullet);
      this.bullets.push(bullet);
    },
    drawBalloon() {
      const scene = this.scene;
      const balloons = this.balloons;

      const mtlLoader = new MTLLoader();
      mtlLoader.load('./src/assets/BalloonMadness/Balloon.mtl', (materials) => {
        materials.preload();

        const objLoader = new OBJLoader();
        objLoader.setMaterials(materials);
        objLoader.load('./src/assets/BalloonMadness/Balloon.obj', (object) => {
          object.position.set(
            Math.random() * (1.75 + 1.75) - 1.75,
            Math.random() * 0.25 - 0.25,
            Math.random() * (3.5 - 1.5) + 1.5
          );
          object.scale.setScalar(Math.random() * (0.75 - 0.25) + 0.25);
          object.speed = Math.random() * (1 - 0.5) + 0.5;
          object.castShadow = true;
          object.receiveShadow = true;
          scene.add(object);
          balloons.push(object);
        });
      });
    },
    checkCollision(balloon) {
      const balloonBox = new THREE.Box3().setFromObject(balloon);

      for (const bullet of this.bullets) {
        const bulletBox = new THREE.Box3().setFromObject(bullet);

        if (bulletBox.intersectsBox(balloonBox)) {
          this.score += 1;
          this.scoreDiv.textContent = 'Score: ' + this.score;
          balloon.position.set(
            Math.random() * (1.75 + 1.75) - 1.75,
            Math.random() * 0.25 - 0.25,
            Math.random() * (3.5 - 1.5) + 1.5
          );
          balloon.scale.setScalar(Math.random() * (0.75 - 0.25) + 0.25);
          balloon.speed = Math.random() * (1 - 0.5) + 0.5;
          bullet.material.dispose();
          bullet.geometry.dispose();
          bullet.removeFromParent();
          this.scene.remove(bullet);
          this.bullets.splice(this.bullets.indexOf(bullet), 1);
        }
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

      this.bullets = [];
      this.time = 60;
      this.score = 0;
      this.gameOver = false;
      this.keys = [];
      this.gun = [];

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
