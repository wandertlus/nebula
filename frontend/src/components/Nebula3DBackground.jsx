import React, { forwardRef, useImperativeHandle, useRef, useMemo, useState, useEffect } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Line } from '@react-three/drei';
import * as THREE from 'three';
import NebulaFogBackground from './NebulaFogBackground';
import EventSparkEmitter from './EventSparkEmitter';

// ── DYNAMIC CONFIG HELPERS ───────────────────────────────────────────────────

function getDynamicConfig(fieldKeys) {
  const defaults = {
    engineering: {
      position: new THREE.Vector3(-1.6, 0.8, -0.8),
      color: new THREE.Color('#BC13FE'),
    },
    fitness: {
      position: new THREE.Vector3(1.6, 0.8, 0.8),
      color: new THREE.Color('#FF8C00'),
    },
    be_fluent: {
      position: new THREE.Vector3(0, -1.4, 0.2),
      color: new THREE.Color('#5ba8e8'),
    },
  };

  const config = {};
  const keys = fieldKeys.length > 0 ? fieldKeys : ['engineering', 'fitness', 'be_fluent'];

  keys.forEach((key, idx) => {
    if (defaults[key]) {
      config[key] = defaults[key];
    } else {
      // Distribute custom fields on a 3D circle with varied Z depth
      const angle = (idx / keys.length) * Math.PI * 2 + Math.PI / 4;
      const radius = 2.0;
      const x = Math.cos(angle) * radius;
      const y = Math.sin(angle) * radius;
      const z = (idx % 2 === 0 ? 0.8 : -0.8);

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

// ── CINEMATIC CORRELATION LINES & PHOTON PULSES ─────────────────────────────────

function CinematicCorrelationLine({
  startPos,
  endPos,
  correlationScore,
  connectionDensity,
  colorStart,
  colorEnd,
}) {
  const lineRefs = useRef([]);
  const impulseRefs = useRef([]);
  const photonRef = useRef();

  // 1. Quadratic Bézier Curve for elegant catenary gravitational arches
  const curve = useMemo(() => {
    const pStart = startPos.clone();
    const pEnd = endPos.clone();
    
    // Elevate the midpoint perpendicular to create majestic arches
    const midPoint = new THREE.Vector3().addVectors(pStart, pEnd).multiplyScalar(0.5);
    midPoint.y += 1.1 + Math.sin(pStart.x * 1.5) * 0.3; // Gravity pull aesthetic
    midPoint.z += 0.4;

    return new THREE.QuadraticBezierCurve3(pStart, midPoint, pEnd);
  }, [startPos, endPos]);

  const fiberBundle = useMemo(() => {
    const fiberCount = Math.max(
      2,
      Math.min(12, Math.round(2 + correlationScore * 5 + connectionDensity * 1.5))
    );
    const basePoints = curve.getPoints(64);
    const axis = new THREE.Vector3().subVectors(endPos, startPos).normalize();
    const normalA = new THREE.Vector3().crossVectors(axis, new THREE.Vector3(0, 1, 0));
    if (normalA.lengthSq() < 0.001) {
      normalA.crossVectors(axis, new THREE.Vector3(1, 0, 0));
    }
    normalA.normalize();
    const normalB = new THREE.Vector3().crossVectors(axis, normalA).normalize();

    return Array.from({ length: fiberCount }, (_, idx) => {
      const angle = (idx / fiberCount) * Math.PI * 2;
      const radius = 0.018 + correlationScore * 0.045 + connectionDensity * 0.006 + (idx % 2) * 0.012;
      const phase = idx * 1.37 + startPos.x * 0.5;
      const offsetA = Math.cos(angle) * radius;
      const offsetB = Math.sin(angle) * radius;

      const points = basePoints.map((point, pointIdx) => {
        const u = pointIdx / (basePoints.length - 1);
        const braid = Math.sin(u * Math.PI * 4 + phase) * 0.035;
        const taper = Math.sin(u * Math.PI);
        return point.clone()
          .addScaledVector(normalA, (offsetA + braid) * taper)
          .addScaledVector(normalB, (offsetB + Math.cos(u * Math.PI * 3 + phase) * 0.025) * taper);
      });

      return { points, phase };
    });
  }, [curve, startPos, endPos, correlationScore, connectionDensity]);

  // 2. Real-time life pulsation (breathing) and traveling photon node animation
  useFrame((state) => {
    const time = state.clock.getElapsedTime();
    
    lineRefs.current.forEach((line, idx) => {
      if (!line) return;
      const pulse = Math.sin(time * 3.2 + fiberBundle[idx].phase) * 0.06;
      const baseOpacity = 0.04 + correlationScore * 0.58 + connectionDensity * 0.025;
      line.material.opacity = Math.min(0.9, Math.max(0.025, baseOpacity + pulse));
    });

    impulseRefs.current.forEach((line, idx) => {
      if (!line?.material) return;
      const speed = 0.14 + correlationScore * 0.34 + connectionDensity * 0.025;
      line.material.dashOffset = -(time * speed + fiberBundle[idx].phase * 0.08);
      line.material.opacity = Math.min(1, 0.18 + correlationScore * 0.7 + connectionDensity * 0.04);
    });

    // Traveling energy photon
    if (photonRef.current) {
      const speed = 0.4 + correlationScore * 0.6; // Faster speed for higher correlation
      const u = (time * speed) % 1.0;
      const pos = curve.getPointAt(u);
      photonRef.current.position.copy(pos);
    }
  });

  const blendedColor = useMemo(() => {
    return colorStart.clone().lerp(colorEnd, 0.5);
  }, [colorStart, colorEnd]);

  return (
    <group>
      {fiberBundle.map((fiber, idx) => (
        <React.Fragment key={idx}>
          <Line
            ref={(el) => (lineRefs.current[idx] = el)}
            points={fiber.points}
            color={blendedColor}
            lineWidth={0.75 + correlationScore * 0.55 + connectionDensity * 0.06}
            transparent
            opacity={0.04 + correlationScore * 0.58 + connectionDensity * 0.025}
            blending={THREE.AdditiveBlending}
            depthWrite={false}
          />
          <Line
            ref={(el) => (impulseRefs.current[idx] = el)}
            points={fiber.points}
            color={idx % 2 === 0 ? '#ffffff' : '#ff4fd8'}
            lineWidth={0.95 + correlationScore * 0.75 + connectionDensity * 0.08}
            transparent
            opacity={Math.min(1, 0.18 + correlationScore * 0.7 + connectionDensity * 0.04)}
            blending={THREE.AdditiveBlending}
            depthWrite={false}
            dashed
            dashArray={0.08}
            dashRatio={0.22}
            dashScale={8 + correlationScore * 12 + connectionDensity * 1.5}
          />
        </React.Fragment>
      ))}
      
      {/* Traveling light photon showing data transfer */}
      <mesh ref={photonRef}>
        <sphereGeometry args={[0.045, 8, 8]} />
        <meshBasicMaterial
          color={blendedColor}
          transparent
          opacity={Math.min(1, 0.25 + correlationScore * 0.6 + connectionDensity * 0.05)}
          blending={THREE.AdditiveBlending}
          depthWrite={false}
        />
      </mesh>
    </group>
  );
}

function NeuralFilaments({ connections, fieldConfig, pairs }) {
  const activeConnectionCounts = useMemo(() => {
    return pairs.reduce((counts, [fa, fb]) => {
      const score = connections[`${fa}:${fb}`] ?? connections[`${fb}:${fa}`] ?? 0.0;
      if (score <= 0) return counts;

      counts[fa] = (counts[fa] ?? 0) + 1;
      counts[fb] = (counts[fb] ?? 0) + 1;
      return counts;
    }, {});
  }, [connections, pairs]);

  return (
    <>
      {pairs.map(([fa, fb]) => {
        const configA = fieldConfig[fa];
        const configB = fieldConfig[fb];
        if (!configA || !configB) return null;

        const correlationScore = connections[`${fa}:${fb}`] ?? connections[`${fb}:${fa}`] ?? 0.0;

        // CRITICAL: Do not show visual connection lines if no data is entered / correlation score is zero.
        if (correlationScore <= 0.0) return null;

        const connectionDensity = ((activeConnectionCounts[fa] ?? 0) + (activeConnectionCounts[fb] ?? 0)) / 2;

        return (
          <CinematicCorrelationLine
            key={`${fa}:${fb}`}
            startPos={configA.position}
            endPos={configB.position}
            colorStart={configA.color}
            colorEnd={configB.color}
            correlationScore={correlationScore}
            connectionDensity={connectionDensity}
          />
        );
      })}
    </>
  );
}


// ── PARTICLE SWARM ────────────────────────────────────────────────────────────
// Quantum particle field flowing, swirling, and being captured by attractors.

const _particlePos = new THREE.Vector3();
const _corePos     = new THREE.Vector3();

function NebulaParticles({ fieldMasses, fieldConfig, keys, currentState, finalScore, driftDelta, isOrbiting }) {
  const meshRef = useRef();
  const [count] = useState(2000); // Cinematic vortex fragments

  const [positions, velocities, attractorWeights] = useMemo(() => {
    const pos = new Float32Array(count * 3);
    const vel = new Float32Array(count * 3);
    const wts = new Float32Array(count * 3); 

    for (let i = 0; i < count; i++) {
      const r     = 1.8 + Math.random() * 2.8;
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

  const tempObject = useMemo(() => new THREE.Object3D(), []);

  useFrame((state, delta) => {
    if (!meshRef.current) return;

    const time = state.clock.getElapsedTime();
    const dt   = Math.min(delta, 0.05);
    
    if (!isOrbiting) {
      state.camera.position.x += (Math.sin(time * 0.12) * 2.2 - state.camera.position.x) * 0.05;
      state.camera.position.y += (Math.cos(time * 0.1) * 1.2 - state.camera.position.y) * 0.05;
      state.camera.position.z += ((6.4 + Math.sin(time * 0.06) * 0.6) - state.camera.position.z) * 0.05;
      state.camera.lookAt(0, 0.1, 0);
    }

    const isFriction  = currentState === 'Friction';
    const isBlackHole = currentState === 'Black Hole';
    const masses      = normalizeMasses(fieldMasses, keys);

    const dominantField = keys.reduce((a, b) => masses[a] > masses[b] ? a : b);
    
    // Cinematic fragment color: Blue for standard nebula, Gold for Black Hole vortex
    const targetColor = new THREE.Color(isBlackHole ? "#ffaa00" : "#5ba8e8");
    meshRef.current.material.color.lerp(targetColor, 0.05);

    const turbulence = driftDelta ? Math.abs(driftDelta) * 10 : 0;

    for (let i = 0; i < count; i++) {
      const idx = i * 3;
      let x = positions[idx];
      let y = positions[idx + 1];
      let z = positions[idx + 2];

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
        const mMult = (isBlackHole && field === dominantField) ? 9.0 : 1.0;

        const F  = (coreMass * mMult) / (rMag * rMag);
        velocities[idx]     += (rx / rMag) * F * dt;
        velocities[idx + 1] += (ry / rMag) * F * dt;
        velocities[idx + 2] += (rz / rMag) * F * dt;

        const swirl = (isBlackHole ? 8.0 : 2.5) / Math.max(rMag, 0.25);
        velocities[idx]     += -rz * swirl * dt;
        velocities[idx + 2] +=  rx * swirl * dt;

        if (rMag < 0.15) {
          const rNew = 3.2 + Math.random() * 1.8;
          const tNew = Math.random() * Math.PI * 2;
          const pNew = Math.acos(Math.random() * 2 - 1);
          x = cPos.x + rNew * Math.sin(pNew) * Math.cos(tNew);
          y = cPos.y + rNew * Math.sin(pNew) * Math.sin(tNew);
          z = cPos.z + rNew * Math.cos(pNew);
          velocities[idx]     = -Math.sin(tNew) * 1.8;
          velocities[idx + 1] = (Math.random() - 0.5) * 2.0;
          velocities[idx + 2] =  Math.cos(tNew) * 1.8;
        }
      }

      if (turbulence > 0) {
        velocities[idx]     += (Math.random() - 0.5) * turbulence * dt;
        velocities[idx + 1] += (Math.random() - 0.5) * turbulence * dt;
        velocities[idx + 2] += (Math.random() - 0.5) * turbulence * dt;
      }

      velocities[idx]     *= 0.95;
      velocities[idx + 1] *= 0.95;
      velocities[idx + 2] *= 0.95;

      positions[idx]     = x + velocities[idx]     * dt;
      positions[idx + 1] = y + velocities[idx + 1] * dt;
      positions[idx + 2] = z + velocities[idx + 2] * dt;

      tempObject.position.set(positions[idx], positions[idx + 1], positions[idx + 2]);
      tempObject.rotation.set(time * 0.8, time * 0.5 + i, 0);
      const scale = isBlackHole ? 0.05 : 0.02;
      tempObject.scale.setScalar(scale);
      tempObject.updateMatrix();
      meshRef.current.setMatrixAt(i, tempObject.matrix);
    }

    meshRef.current.instanceMatrix.needsUpdate = true;
  });

  return (
    <instancedMesh ref={meshRef} args={[null, null, count]}>
      <tetrahedronGeometry args={[0.08, 0]} />
      <meshBasicMaterial
        transparent
        opacity={0.4}
        blending={THREE.AdditiveBlending}
        depthWrite={false}
      />
    </instancedMesh>
  );
}


// ── GRAVITY CORES ─────────────────────────────────────────────────────────────
// Dense neural clusters: a hot nucleus wrapped in animated dendrite filaments.

const NeuralIdentityCore = forwardRef(function NeuralIdentityCore({ color, share, isDominant, currentState }, ref) {
  const coreRef = useRef();
  const coreMaterialRef = useRef();
  const dendriteRefs = useRef([]);

  // Manage massBase (permanent) and momentumCurrent (temporary pulse state)
  const [massBase, setMassBase] = useState(share);
  const momentumCurrentRef = useRef(0.0);
  const [momentumCurrent, setMomentumCurrent] = useState(0.0);

  // Sync initial massBase with share if it changes from backend
  useEffect(() => {
    setMassBase(share);
  }, [share]);

  useImperativeHandle(ref, () => ({
    triggerAbsorption(mass_impact = 0, momentum_burst = 0) {
      setMassBase((prev) => prev + mass_impact);
      const nextMomentum = momentumCurrentRef.current + momentum_burst;
      momentumCurrentRef.current = Math.min(3.0, Math.max(-3.0, nextMomentum));
      setMomentumCurrent(momentumCurrentRef.current);
    },
  }), []);

  const dendrites = useMemo(() => {
    const count = 50;
    return Array.from({ length: count }, (_, idx) => {
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(Math.random() * 2 - 1);
      const direction = new THREE.Vector3(
        Math.sin(phi) * Math.cos(theta),
        Math.sin(phi) * Math.sin(theta),
        Math.cos(phi)
      ).normalize();
      const tangent = new THREE.Vector3(
        Math.cos(theta + Math.PI * 0.5),
        Math.sin(theta + Math.PI * 0.5),
        (Math.random() - 0.5) * 0.35
      ).normalize();

      return {
        direction,
        tangent,
        length: 0.28 + Math.random() * 0.42,
        bend: 0.06 + Math.random() * 0.16,
        phase: Math.random() * Math.PI * 2,
        speed: 0.8 + Math.random() * 1.2,
        branchAt: 0.55 + Math.random() * 0.25,
        branchSide: Math.random() > 0.5 ? 1 : -1,
      };
    });
  }, []);

  useFrame((state) => {
    const t = state.clock.getElapsedTime();
    const stateBoost = currentState === 'Black Hole' ? 1.7 : currentState === 'Friction' ? 1.25 : 1;
    const dominanceBoost = isDominant ? stateBoost * 2.2 : 0.75;
    
    // Stable scale driven by massBase
    const clusterScale = 0.72 + massBase * 1.05;

    // Sinusoidal vibration driven by momentumCurrent pulse
    const vibration = 1 + Math.sin(t * dominanceBoost * 12) * momentumCurrent * 0.05;

    if (coreRef.current) {
      coreRef.current.scale.setScalar(clusterScale * vibration);
    }

    if (coreMaterialRef.current) {
      coreMaterialRef.current.emissiveIntensity = 1.6 + massBase * 1.8 + momentumCurrent * 3.2;
      coreMaterialRef.current.opacity = Math.min(1, 0.82 + massBase * 0.12);
    }

    dendrites.forEach((dendrite, idx) => {
      const line = dendriteRefs.current[idx];
      if (!line) return;

      const wave = Math.sin(t * dendrite.speed * dominanceBoost + dendrite.phase);
      const twitch = wave * dendrite.bend * (isDominant ? 1.45 : 0.55) * (1 + momentumCurrent * 0.35);
      const baseLength = dendrite.length * clusterScale;
      const positions = line.geometry.attributes.position.array;

      for (let point = 0; point < 4; point++) {
        const u = point / 3;
        const branchKick = point > 1 ? (u - dendrite.branchAt) * dendrite.branchSide * 0.16 : 0;
        const outward = dendrite.direction.clone().multiplyScalar(baseLength * u);
        const curve = dendrite.tangent.clone().multiplyScalar((dendrite.bend + twitch + branchKick) * Math.sin(u * Math.PI));
        const pos = outward.add(curve);

        positions[point * 3] = pos.x;
        positions[point * 3 + 1] = pos.y;
        positions[point * 3 + 2] = pos.z;
      }

      line.geometry.attributes.position.needsUpdate = true;
      line.material.opacity = Math.min(
        1,
        0.28 + massBase * 0.42 + momentumCurrent * 0.24 + (isDominant ? Math.abs(wave) * 0.24 : 0)
      );
    });

    // Momentum pulse decays constantly to zero
    const decayedMomentum = THREE.MathUtils.lerp(momentumCurrentRef.current, 0, 0.02);
    if (Math.abs(decayedMomentum - momentumCurrentRef.current) > 0.0005) {
      momentumCurrentRef.current = decayedMomentum;
      setMomentumCurrent(decayedMomentum);
    } else if (momentumCurrentRef.current !== 0) {
      momentumCurrentRef.current = 0;
      setMomentumCurrent(0);
    }
  });

  // Determine the number of visible dendrites based on massBase
  const visibleDendriteCount = Math.min(dendrites.length, Math.max(5, Math.round(massBase * 100)));

  return (
    <group>
      <mesh ref={coreRef}>
        <sphereGeometry args={[0.18, 32, 32]} />
        <meshStandardMaterial
          ref={coreMaterialRef}
          color={color}
          emissive={color}
          emissiveIntensity={1.6 + share * 1.8}
          transparent
          opacity={Math.min(1, 0.82 + share * 0.12)}
          blending={THREE.AdditiveBlending}
          depthWrite={false}
        />
      </mesh>

      {dendrites.slice(0, visibleDendriteCount).map((dendrite, idx) => {
        const points = new Float32Array(12);
        for (let point = 0; point < 4; point++) {
          const u = point / 3;
          const pos = dendrite.direction.clone().multiplyScalar(dendrite.length * u);
          points[point * 3] = pos.x;
          points[point * 3 + 1] = pos.y;
          points[point * 3 + 2] = pos.z;
        }

        return (
          <line key={idx} ref={(el) => (dendriteRefs.current[idx] = el)}>
            <bufferGeometry>
              <bufferAttribute attach="attributes-position" args={[points, 3]} />
            </bufferGeometry>
            <lineBasicMaterial
              color={color}
              transparent
              opacity={0.45}
              blending={THREE.AdditiveBlending}
              depthWrite={false}
            />
          </line>
        );
      })}
    </group>
  );
});

function GravityCores({ coreRefs, fieldMasses, fieldConfig, keys, currentState, onCoreClick }) {
  const masses = useMemo(() => normalizeMasses(fieldMasses, keys), [fieldMasses, keys]);
  const dominantField = useMemo(() => {
    return keys.reduce((winner, field) => (
      (masses[field] ?? 0) > (masses[winner] ?? 0) ? field : winner
    ), keys[0]);
  }, [keys, masses]);

  return (
    <>
      {keys.map((field, idx) => {
        const { position, color } = fieldConfig[field];
        const share = masses[field] ?? 0;

        return (
          <group key={field} position={position}>
            <NeuralIdentityCore
              ref={(el) => {
                if (el) coreRefs.current[field] = el;
              }}
              color={color}
              share={share}
              isDominant={field === dominantField}
              currentState={currentState}
            />

            {/* Invisible Generous Raycast Hit-Box for Perfect Click Target Area */}
            <mesh
              onClick={(e) => {
                e.stopPropagation();
                if (onCoreClick) onCoreClick(field);
              }}
              onPointerOver={(e) => {
                e.stopPropagation();
                document.body.style.cursor = 'pointer';
              }}
              onPointerOut={(e) => {
                e.stopPropagation();
                document.body.style.cursor = 'default';
              }}
            >
              <sphereGeometry args={[share === 0 ? 0.22 : (0.42 + share * 0.38), 16, 16]} />
              <meshBasicMaterial transparent opacity={0.0} depthWrite={false} />
            </mesh>
          </group>
        );
      })}
    </>
  );
}

export default function Nebula3DBackground({
  events = [],
  fieldMasses = {},
  connections = {},
  currentState,
  finalScore,
  driftDelta,
  onCoreClick,
}) {
  const [isCommandPressed, setIsCommandPressed] = useState(false);
  const coreRefs = useRef({});

  // Capture initial event IDs to filter out historical events from emitting new sparks on load
  const [initialEventIds] = useState(() => new Set(events.filter(ev => ev.event_id).map(ev => ev.event_id)));

  const { config, keys, pairs } = useMemo(() => {
    return getDynamicConfig(Object.keys(fieldMasses));
  }, [Object.keys(fieldMasses).join(',')]);

  // Map incoming events to sparks, excluding those that were present on mount
  const incomingSignals = useMemo(() => {
    return events
      .filter(ev => ev.event_id && ev.dominant_attractor && !initialEventIds.has(ev.event_id))
      .map(ev => {
        const targetField = ev.dominant_attractor;
        const fieldConf = config[targetField];
        return {
          id: ev.event_id,
          targetPos: fieldConf ? fieldConf.position : new THREE.Vector3(),
          score: ev.final_score ?? 0,
          color: fieldConf ? fieldConf.color : '#ffffff',
          physics_profile: {
            behavioral_type: ev.behavioral_type ?? 'structured',
            visual_scale: ev.physics?.visual_scale ?? 1.0,
          },
          mass_impact: ev.physics?.mass_impact ?? 0.0,
          momentum_burst: ev.physics?.momentum_burst ?? 0.0,
          category: targetField,
        };
      });
  }, [events, config, initialEventIds]);

  const handleEnergyImpact = (spark) => {
    const targetCore = coreRefs.current[spark.category];
    if (targetCore) {
      targetCore.triggerAbsorption(spark.mass_impact, spark.momentum_burst);
    }
  };

  // Setup keyboard event listeners for CMD/CTRL key
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Meta' || e.key === 'Control') {
        setIsCommandPressed(true);
      }
    };
    const handleKeyUp = (e) => {
      if (e.key === 'Meta' || e.key === 'Control') {
        setIsCommandPressed(false);
      }
    };
    const handleBlur = () => {
      setIsCommandPressed(false);
    };

    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);
    window.addEventListener('blur', handleBlur);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
      window.removeEventListener('blur', handleBlur);
    };
  }, []);

  return (
    <div style={{ position: 'fixed', inset: 0, zIndex: 0 }}>
      {/* Visual tip/HUD helper for controls */}
      <div style={{
        position: 'absolute',
        bottom: '24px',
        left: '50%',
        transform: 'translateX(-50%)',
        zIndex: 5,
        fontFamily: 'var(--font-mono)',
        fontSize: '9px',
        color: 'rgba(255, 255, 255, 0.35)',
        letterSpacing: '0.15em',
        pointerEvents: 'none',
        textTransform: 'uppercase',
        transition: 'color 0.3s ease',
        background: 'rgba(0, 0, 0, 0.45)',
        padding: '6px 12px',
        borderRadius: '4px',
        border: '1px solid rgba(255, 255, 255, 0.05)',
        backdropFilter: 'blur(4px)',
        color: isCommandPressed ? 'var(--neon-purple)' : 'rgba(255, 255, 255, 0.35)',
        boxShadow: isCommandPressed ? '0 0 10px rgba(188, 19, 254, 0.2)' : 'none'
      }}>
        {isCommandPressed ? 'Orbit Camera Active (Drag Mouse)' : 'Hold CMD ⌘ / CTRL to orbit scenario'}
      </div>

      <Canvas 
        camera={{ position: [0, 0, 6], fov: 60 }}
        raycaster={{ params: { Points: { threshold: 0.16 } } }}
        style={{ pointerEvents: 'auto' }}
      >
        <NebulaFogBackground />
        <ambientLight intensity={0.4} />
        <directionalLight position={[5, 5, 5]} intensity={1.6} color="#ffffff" />
        <pointLight position={[-4, -4, 3]} intensity={1.2} color="#ffffff" />
        <NeuralFilaments connections={connections} fieldConfig={config} pairs={pairs} />
        <GravityCores
          coreRefs={coreRefs}
          fieldMasses={fieldMasses}
          fieldConfig={config}
          keys={keys}
          currentState={currentState}
          onCoreClick={onCoreClick}
        />
        <NebulaParticles
          fieldMasses={fieldMasses}
          fieldConfig={config}
          keys={keys}
          currentState={currentState}
          finalScore={finalScore}
          driftDelta={driftDelta}
          isOrbiting={isCommandPressed}
        />
        <EventSparkEmitter
          incomingSignals={incomingSignals}
          onEnergyImpact={handleEnergyImpact}
        />
        <OrbitControls 
          enabled={isCommandPressed}
          enableZoom={true} 
          enablePan={true}
          makeDefault
        />
      </Canvas>
    </div>
  );
}
