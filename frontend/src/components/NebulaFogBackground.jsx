import React, { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

/**
 * NebulaFogBackground
 * Renderiza un fondo dinámico de gases cósmicos usando ruido fractal (FBM).
 */
const NebulaFogBackground = () => {
  const meshRef = useRef();

  // Definición del Shader con parámetros físicos de Nebula
  const nebulaShader = useMemo(() => ({
    uniforms: {
      uTime: { value: 0 },
      uColorNavy: { value: new THREE.Color("#0A1235") }, // Azul marino más claro
      uColorPurple: { value: new THREE.Color("#300060") }, // Púrpura más vibrante
      uColorFuchsia: { value: new THREE.Color("#ff007f") },
    },
    vertexShader: `
      varying vec2 vUv;
      void main() {
        vUv = uv;
        // Proyecta el plano directamente en el espacio de clip para cubrir la pantalla
        gl_Position = vec4(position.xy, 0.0, 1.0);
      }
    `,
    fragmentShader: `
      uniform float uTime;
      uniform vec3 uColorNavy;
      uniform vec3 uColorPurple;
      uniform vec3 uColorFuchsia;
      varying vec2 vUv;

      // Función de hash para el ruido
      float hash(vec2 p) {
        p = fract(p * vec2(123.34, 456.21));
        p += dot(p, p + 45.32);
        return fract(p.x * p.y);
      }

      // Ruido de Perlin suavizado
      float noise(vec2 p) {
        vec2 i = floor(p);
        vec2 f = fract(p);
        float a = hash(i);
        float b = hash(i + vec2(1.0, 0.0));
        float c = hash(i + vec2(0.0, 1.0));
        float d = hash(i + vec2(1.0, 1.0));
        vec2 u = f * f * (3.0 - 2.0 * f);
        return mix(a, b, u.x) + (c - a) * u.y * (1.0 - u.x) + (d - b) * u.x * u.y;
      }

      // Fractal Brownian Motion (FBM) para densidad de gas
      float fbm(vec2 p) {
        float v = 0.0;
        float a = 0.5;
        for (int i = 0; i < 6; i++) {
          v += a * noise(p);
          p *= 2.02; // Lacunarity
          a *= 0.5;  // Gain
        }
        return v;
      }

      void main() {
        vec2 uv = vUv;
        float slowTime = uTime * 0.04;

        // Generar capas de gas con movimiento contrapuesto
        float n1 = fbm(uv * 3.0 + slowTime);
        float n2 = fbm(uv * 5.0 - slowTime * 2.0 + n1);
        
        // Mezcla base entre Azul Marino y Púrpura
        vec3 cosmicGas = mix(uColorNavy, uColorPurple, n1);
        
        // Brillo más intenso y dinámico
        float highlights = pow(n2, 3.0);
        vec3 finalColor = cosmicGas + uColorFuchsia * highlights * 0.5;
        finalColor += vec3(0.01, 0.02, 0.04); // Brillo ambiental mínimo

        // Añadir brillo fucsia "nuclear" en los picos de densidad
        finalColor += uColorFuchsia * highlights * 0.2; // Brillo más general, menos concentrado

        gl_FragColor = vec4(finalColor, 0.9);
      }
    `
  }), []);

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.material.uniforms.uTime.value = state.clock.getElapsedTime();
    }
  });

  return (
    <mesh ref={meshRef} renderOrder={-500}>
      <planeGeometry args={[2, 2]} />
      <shaderMaterial 
        args={[nebulaShader]} 
        transparent={false} 
        depthWrite={false} 
        side={THREE.DoubleSide}
      />
    </mesh>
  );
};

export default NebulaFogBackground;