import * as THREE from 'https://unpkg.com/three@0.160.0/build/three.module.js';
import { FontLoader } from 'https://unpkg.com/three@0.160.0/examples/jsm/loaders/FontLoader.js';
import { TextGeometry } from 'https://unpkg.com/three@0.160.0/examples/jsm/geometries/TextGeometry.js';

// --- Scene Setup ---
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.getElementById('intro-canvas-container').appendChild(renderer.domElement);

// --- 1. Space Background (Stars) ---
const starGeometry = new THREE.BufferGeometry();
const starCount = 5000;
const posArray = new Float32Array(starCount * 3);
for(let i = 0; i < starCount * 3; i++) {
    posArray[i] = (Math.random() - 0.5) * 100;
}
starGeometry.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
const starMaterial = new THREE.PointsMaterial({ size: 0.05, color: 0xffffff });
const stars = new THREE.Points(starGeometry, starMaterial);
scene.add(stars);

// --- 2. The Globe ---
const globeGeo = new THREE.SphereGeometry(5, 64, 64);
const globeMat = new THREE.MeshStandardMaterial({
    color: 0x111111,
    emissive: 0x00ff00,
    emissiveIntensity: 0.1,
    wireframe: false
});
const globe = new THREE.Mesh(globeGeo, globeMat);
scene.add(globe);

// --- 3. The 3D Text "GEM INDIA" ---
const loader = new FontLoader();
loader.load('https://unpkg.com/three@0.160.0/examples/fonts/helvetiker_bold.typeface.json', (font) => {
    const textGeo = new TextGeometry('GEM INDIA', {
        font: font,
        size: 1.2,
        height: 0.4,
        curveSegments: 12,
        bevelEnabled: true,
        bevelThickness: 0.03,
        bevelSize: 0.02,
    });
    textGeo.center(); // Centers the text
    const materials = [
        new THREE.MeshStandardMaterial({ color: 0x00ff00 }), // Front (Green)
        new THREE.MeshStandardMaterial({ color: 0xffffff })  // Side (White)
    ];
    const textMesh = new THREE.Mesh(textGeo, materials);
    textMesh.position.set(0, 0, 12); // Puts text in front of the globe
    scene.add(textMesh);
});

// --- 4. The Orbiting Rocket ---
const rocketGroup = new THREE.Group();
const rocketBody = new THREE.Mesh(new THREE.ConeGeometry(0.2, 0.8, 32), new THREE.MeshStandardMaterial({color: 0xffffff}));
rocketBody.rotation.x = Math.PI / 2;
rocketGroup.add(rocketBody);
scene.add(rocketGroup);

// --- 5. Lighting ---
const mainLight = new THREE.PointLight(0xffffff, 200);
mainLight.position.set(10, 10, 10);
scene.add(mainLight);
scene.add(new THREE.AmbientLight(0xffffff, 0.3));

camera.position.z = 20;

// --- 6. Animation ---
let angle = 0;
function animate() {
    requestAnimationFrame(animate);

    angle += 0.015;
    globe.rotation.y += 0.002;

    // Rocket Path
    rocketGroup.position.x = Math.cos(angle) * 8;
    rocketGroup.position.z = Math.sin(angle) * 8;
    rocketGroup.rotation.y = -angle;

    renderer.render(scene, camera);
}
animate();

// --- 7. Auto-Transition to Website ---
setTimeout(() => {
    const overlay = document.getElementById('intro-overlay');
    overlay.style.opacity = '0';
    setTimeout(() => { overlay.style.display = 'none'; }, 1000);
}, 6000); // Intro lasts 6 seconds