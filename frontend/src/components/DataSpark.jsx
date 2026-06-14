import React, { useMemo, useRef, useState } from 'react';
import { useFrame } from '@react-three/fiber';
import { Trail } from '@react-three/drei';
import * as THREE from 'three';

const toVector3 = (value) => {
  if (value?.isVector3) return value.clone();
  if (Array.isArray(value)) return new THREE.Vector3(...value);
  return new THREE.Vector3();
};

const SPARK_PRESETS = {
  structured: {
    radius: 0.08,
    segments: 16,
    trailWidth: 0.8,
    trailLength: 14,
    speedBase: 0.012,
    speedScore: 0.025,
  },
  casual: {
    radius: 0.02,
    segments: 8,
    trailWidth: 0.18,
    trailLength: 4,
    speedBase: 0.09,
    speedScore: 0.16,
  },
  degenerate: {
    radius: 0.06,
    segments: 12,
    trailWidth: 0.55,
    trailLength: 9,
    speedBase: 0.025,
    speedScore: 0.05,
  },
};

const DataSpark = ({
  startPos,
  targetPos,
  score = 0,
  color = '#ffffff',
  physics_profile,
  onImpact,
}) => {
  const meshRef = useRef();
  const [impacted, setImpacted] = useState(false);

  const currentPos = useMemo(() => toVector3(startPos), [startPos]);
  const target = useMemo(() => toVector3(targetPos), [targetPos]);
  const clampedScore = Math.min(1, Math.max(0, score));
  const sparkPhysics = useMemo(() => {
    const type = physics_profile?.behavioral_type ?? 'structured';
    const visualScale = Math.max(0.1, physics_profile?.visual_scale ?? 1);
    const preset = SPARK_PRESETS[type] ?? SPARK_PRESETS.structured;

    return {
      radius: preset.radius * visualScale,
      segments: preset.segments,
      trailWidth: preset.trailWidth * visualScale,
      trailLength: Math.max(1, preset.trailLength * visualScale),
      speedBase: preset.speedBase,
      speedScore: preset.speedScore,
    };
  }, [physics_profile]);

  useFrame((state) => {
    if (impacted || !meshRef.current) return;

    const time = state.clock.getElapsedTime();
    const distance = currentPos.distanceTo(target);

    if (distance < 0.5) {
      setImpacted(true);
      if (onImpact) onImpact();
      return;
    }

    const speed = sparkPhysics.speedBase + clampedScore * sparkPhysics.speedScore;
    currentPos.lerp(target, speed);

    const orbitAmplitude = (1 - clampedScore) * Math.min(distance, 2.5) * 0.035;
    currentPos.x += Math.cos(time * 5) * orbitAmplitude;
    currentPos.y += Math.sin(time * 5) * orbitAmplitude;

    meshRef.current.position.copy(currentPos);
  });

  if (impacted) return null;

  return (
    <Trail width={sparkPhysics.trailWidth} length={sparkPhysics.trailLength} attenuation={(t) => t * t}>
      <mesh ref={meshRef} position={currentPos}>
        <sphereGeometry args={[sparkPhysics.radius, sparkPhysics.segments, sparkPhysics.segments]} />
        <meshBasicMaterial
          color={color}
          transparent
          opacity={0.95}
          blending={THREE.AdditiveBlending}
          depthWrite={false}
        />
      </mesh>
    </Trail>
  );
};

export default DataSpark;
