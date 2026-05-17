import React, { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import * as THREE from 'three';

// ── DYNAMIC CONFIG HELPERS ───────────────────────────────────────────────────

function getDynamicConfig(fieldKeys) {
  const defaults = {
    engineering: {
      position: new THREE.Vector3(-1.5, 0.8, 0),
      color: new THREE.Color('#BC13FE'),
    },
    fitness: {
      position: new THREE.Vector3(1.5, 0.8, 0),
      color: new THREE.Color('#FF8C00'),
    },
    be_fluent: {
      position: new THREE.Vector3(0, -1.5, 0),
      color: new THREE.Color('#5ba8e8'),
    },
  };

  const config = {};
  const keys = fieldKeys.length > 0 ? fieldKeys : ['engineering', 'fitness', 'be_fluent'];

  keys.forEach((key, idx) => {
    if (defaults[key]) {
      config[key] = defaults[key];
    } else {
      // Distribute custom fields on a circle
      const angle = (idx / keys.length) * Math.PI * 2 + Math.PI / 4;
      const radius = 2.0;
      const x = Math.cos(angle) * radius;
      const y = Math.sin(angle) * radius;
      const z = (idx % 2 === 0 ? 1 : -1) * 0.5;

      const hue = (idx * 137.5) % 360;
      const colorStr = `hsl(${hue}, 85%, 65%)`;

      config[key] = {
        position: new THREE.Vector3(x, y, z),
        color: new THREE.Color(colorStr),
      };
    }
  });

  const pairs = [];
  for (let i = 0; i < keys.length; i++) {
    for (let j = i + 1; j < keys.length; j++) {
      pairs.push([keys[i], keys[j]]);
    }
  }

  return { config, keys, pairs };
}

function normalizeMasses(fieldMasses, keys) {
  const total = keys.reduce((s, k) => s + (fieldMasses[k] ?? 0), 0);
  if (total === 0) return Object.fromEntries(keys.map(k => [k, 1 / keys.length]));
  return Object.fromEntries(keys.map(k => [k, (fieldMasses[k] ?? 0) / total]));
}

// ── NEURAL FILAMENTS ──────────────────────────────────────────────────────────

function NeuralFilaments({ connections, fieldConfig, pairs }) {
  const matRefs = useRef([]);

  const filamentData = useMemo(() => {
    return pairs.map(([fa, fb]) => {
      const posA = fieldConfig[fa].position;
      const posB = fieldConfig[fb].position;

      const mid = new THREE.Vector3(
        (posA.x + posB.x) / 2 + (Math.random() - 0.5) * 0.4,
        (posA.y + posB.y) / 2 + (Math.random() - 0.5) * 0.4,
        (posA.z + posB.z) / 2 + 1.8
      );

      const curve = new THREE.CatmullRomCurve3([posA, mid, posB]);
      const pts   = curve.getPoints(80);
      const pos   = new Float32Array(pts.length * 3);
      pts.forEach((p, i) => {
        pos[i * 3]     = p.x;
        pos[i * 3 + 1] = p.y;
        pos[i * 3 + 2] = p.z;
      });

      const blended = fieldConfig[fa].color.clone().lerp(fieldConfig[fb].color, 0.5);
      return { key: `${fa}:${fb}`, pos, color: blended, ptCount: pts.length };
    });
  }, [pairs, fieldConfig]);

  useFrame((state) => {
    const t = state.clock.getElapsedTime();
    filamentData.forEach(({ key }, idx) => {
      const mat = matRefs.current[idx];
      if (!mat) return;
      const strength = connections?.[key] ?? 0;
      const pulse = 0.04 + strength * 0.55 + Math.sin(t * 0.7 + idx * 1.3) * 0.06 * (strength + 0.1);
      mat.opacity = Math.min(0.95, Math.max(0, pulse));
    });
  });

  return (
    <>
      {filamentData.map(({ key, pos, color, ptCount }, idx) => (
        <line key={key}>
          <bufferGeometry>
            <bufferAttribute
              attach="attributes-position"
              count={ptCount}
              array={pos}
              itemSize={3}
            />
          </bufferGeometry>
          <lineBasicMaterial
            ref={el => (matRefs.current[idx] = el)}
            color={color}
            transparent
            opacity={0.04}
            blending={THREE.AdditiveBlending}
            depthWrite={false}
          />
        </line>
      ))}
    </>
  );
}

// ── PARTICLE SWARM ────────────────────────────────────────────────────────────

const _particlePos = new THREE.Vector3();
const _corePos     = new THREE.Vector3();

function NebulaParticles({ fieldMasses, fieldConfig, keys, currentState, finalScore, driftDelta }) {
  const pointsRef  = useRef();
  const materialRef = useRef();
  const particleCount = 3000;

  const [positions, velocities, attractorWeights] = useMemo(() => {
    const pos = new Float32Array(particleCount * 3);
    const vel = new Float32Array(particleCount * 3);
    const wts = new Float32Array(particleCount * 3); 

    for (let i = 0; i < particleCount; i++) {
      const r     = 1.5 + Math.random() * 2.5;
      const theta = Math.random() * Math.PI * 2;
      const phi   = Math.acos(Math.random() * 2 - 1);
      pos[i * 3]     = r * Math.sin(phi) * Math.cos(theta);
      pos[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
      pos[i * 3 + 2] = r * Math.cos(phi);

      const dom = Math.floor(Math.random() * keys.length);
      wts[i * 3 + dom] = 0.6 + Math.random() * 0.4;
      
      const rest = Array.from({length: keys.length}, (_, k) => k).filter(x => x !== dom);
      if (rest.length > 0) {
        let remaining = 1 - wts[i * 3 + dom];
        for (let j = 0; j < rest.length - 1; j++) {
            const share = remaining * Math.random();
            wts[i * 3 + rest[j]] = share;
            remaining -= share;
        }
        wts[i * 3 + rest[rest.length-1]] = remaining;
      }
    }
    return [pos, vel, wts];
  }, [keys.length]);

  useFrame((state, delta) => {
    if (!pointsRef.current || !materialRef.current) return;

    const time = state.clock.getElapsedTime();
    const dt   = Math.min(delta, 0.05);
    const posAttr = pointsRef.current.geometry.attributes.position;
    const arr = posAttr.array;

    const isFriction  = currentState === 'Friction';
    const isBlackHole = currentState === 'Black Hole';
    const masses      = normalizeMasses(fieldMasses, keys);

    const dominantField = keys.reduce((a, b) => masses[a] > masses[b] ? a : b);
    materialRef.current.color.lerp(fieldConfig[dominantField].color, 0.03);

    const targetSize = isFriction ? 0.018 : isBlackHole ? 0.012 : 0.022;
    materialRef.current.size += (targetSize - materialRef.current.size) * 0.05;

    const turbulence = driftDelta ? Math.abs(driftDelta) * 8 : 0;

    if (isFriction) {
      pointsRef.current.rotation.y = time * 0.15;
    } else {
      pointsRef.current.rotation.y *= 0.98;
    }

    for (let i = 0; i < particleCount; i++) {
      const idx = i * 3;
      let x = arr[idx];
      let y = arr[idx + 1];
      let z = arr[idx + 2];

      _particlePos.set(x, y, z);

      for (let c = 0; c < keys.length; c++) {
        const field = keys[c];
        const cPos  = fieldConfig[field].position;
        _corePos.copy(cPos);

        const rx   = _corePos.x - x;
        const ry   = _corePos.y - y;
        const rz   = _corePos.z - z;
        const rMag = Math.sqrt(rx*rx + ry*ry + rz*rz) + 0.1;

        const coreMass = masses[field] * (attractorWeights[i * 3 + c] || 0.33);
        let massMultiplier = 1.0;
        if (isBlackHole && field === dominant_field_logic_fix && (finalScore ?? 0) < 0) {
           // We use dominantField here
        }
        
        // Simpler dominant check for logic
        const mMult = (isBlackHole && field === dominantField) ? 8.0 : 1.0;

        const F  = (coreMass * mMult) / (rMag * rMag);
        velocities[idx]     += (rx / rMag) * F * dt;
        velocities[idx + 1] += (ry / rMag) * F * dt;
        velocities[idx + 2] += (rz / rMag) * F * dt;

        if (isBlackHole) {
          const swirl = 6.0 / Math.max(rMag, 0.2);
          velocities[idx]     += -z * swirl * dt;
          velocities[idx + 2] +=  x * swirl * dt;
        }

        if (rMag < 0.12) {
          const rNew = 3.0 + Math.random() * 1.5;
          const tNew = Math.random() * Math.PI * 2;
          const pNew = Math.acos(Math.random() * 2 - 1);
          x = cPos.x + rNew * Math.sin(pNew) * Math.cos(tNew);
          y = cPos.y + rNew * Math.sin(pNew) * Math.sin(tNew);
          z = cPos.z + rNew * Math.cos(pNew);
          velocities[idx]     = -Math.sin(tNew) * 1.5;
          velocities[idx + 1] = (Math.random() - 0.5);
          velocities[idx + 2] =  Math.cos(tNew) * 1.5;
        }
      }

      if (turbulence > 0) {
        velocities[idx]     += (Math.random() - 0.5) * turbulence * dt;
        velocities[idx + 1] += (Math.random() - 0.5) * turbulence * dt;
        velocities[idx + 2] += (Math.random() - 0.5) * turbulence * dt;
      }

      velocities[idx]     *= 0.96;
      velocities[idx + 1] *= 0.96;
      velocities[idx + 2] *= 0.96;

      arr[idx]     = x + velocities[idx]     * dt;
      arr[idx + 1] = y + velocities[idx + 1] * dt;
      arr[idx + 2] = z + velocities[idx + 2] * dt;
    }

    posAttr.needsUpdate = true;
  });

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={particleCount}
          array={positions}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        ref={materialRef}
        color="#BC13FE"
        size={0.018}
        transparent
        opacity={0.85}
        sizeAttenuation
        blending={THREE.AdditiveBlending}
        depthWrite={false}
      />
    </points>
  );
}

// ── GRAVITY CORES ─────────────────────────────────────────────────────────────
// Glowing spherical star-like nodes at each attractor position.
// The radius and brightness scale dynamically with the field's mass.

function GravityCores({ fieldMasses, fieldConfig, keys }) {
  const meshRefs = useRef([]);
  const masses = useMemo(() => normalizeMasses(fieldMasses, keys), [fieldMasses, keys]);

  useFrame((state) => {
    const t = state.clock.getElapsedTime();
    keys.forEach((field, idx) => {
      const mesh = meshRefs.current[idx];
      if (!mesh) return;

      const share = masses[field] ?? 0;
      // Pulse animation: dominant cores breathe more intensely
      const pulse = Math.sin(t * 2.5 + idx * 1.5) * 0.04 * (share + 0.15);
      const targetScale = 0.12 + share * 0.65 + pulse;
      
      mesh.scale.setScalar(targetScale);
    });
  });

  return (
    <>
      {keys.map((field, idx) => {
        const { position, color } = fieldConfig[field];
        const share = masses[field] ?? 0;
        return (
          <group key={field} position={position}>
            {/* Core Energy sphere */}
            <mesh ref={(el) => (meshRefs.current[idx] = el)}>
              <sphereGeometry args={[1, 32, 32]} />
              <meshBasicMaterial
                color={color}
                transparent
                opacity={0.25 + share * 0.55}
                blending={THREE.AdditiveBlending}
                depthWrite={false}
              />
            </mesh>
            {/* Soft outer glow halo */}
            <mesh scale={[1.4, 1.4, 1.4]}>
              <sphereGeometry args={[1, 16, 16]} />
              <meshBasicMaterial
                color={color}
                transparent
                opacity={0.08 + share * 0.15}
                blending={THREE.AdditiveBlending}
                depthWrite={false}
              />
            </mesh>
          </group>
        );
      })}
    </>
  );
}

// ── EXPORT ────────────────────────────────────────────────────────────────────

export default function Nebula3DBackground({
  fieldMasses = {},
  connections = {},
  currentState,
  finalScore,
  driftDelta,
}) {
  const { config, keys, pairs } = useMemo(() => {
    return getDynamicConfig(Object.keys(fieldMasses));
  }, [Object.keys(fieldMasses).join(',')]);

  return (
    <div style={{ position: 'fixed', inset: 0, zIndex: 0, pointerEvents: 'none' }}>
      <Canvas camera={{ position: [0, 0, 6], fov: 60 }}>
        <ambientLight intensity={0.3} />
        <NeuralFilaments connections={connections} fieldConfig={config} pairs={pairs} />
        <GravityCores fieldMasses={fieldMasses} fieldConfig={config} keys={keys} />
        <NebulaParticles
          fieldMasses={fieldMasses}
          fieldConfig={config}
          keys={keys}
          currentState={currentState}
          finalScore={finalScore}
          driftDelta={driftDelta}
        />
      </Canvas>
    </div>
  );
}
