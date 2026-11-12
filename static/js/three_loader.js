// ===============================
// 3D BRAIN & HEART LOADER
// ===============================

import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.150.1/build/three.module.js';
import { GLTFLoader } from 'https://cdn.jsdelivr.net/npm/three@0.150.1/examples/jsm/loaders/GLTFLoader.js';

function load3DModel(containerId, modelPath){

    const container = document.getElementById(containerId);

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75,1,0.1,1000);
    const renderer = new THREE.WebGLRenderer({alpha:true});

    renderer.setSize(300,300);
    container.appendChild(renderer.domElement);

    const light = new THREE.AmbientLight(0xffffff,1);
    scene.add(light);

    const loader = new GLTFLoader();
    loader.load(modelPath, function(gltf){

        const model = gltf.scene;
        scene.add(model);

        camera.position.z = 3;

        function animate(){
            requestAnimationFrame(animate);
            model.rotation.y += 0.01;
            renderer.render(scene,camera);
        }

        animate();
    });
}