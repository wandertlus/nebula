import React, { useEffect, useState } from 'react';
import * as THREE from 'three';
import DataSpark from './DataSpark';

const randomFarStart = (radius = 15) => {
  const theta = Math.random() * Math.PI * 2;
  const phi = Math.acos(Math.random() * 2 - 1);

  return new THREE.Vector3(
    radius * Math.sin(phi) * Math.cos(theta),
    radius * Math.sin(phi) * Math.sin(theta),
    radius * Math.cos(phi)
  );
};

const EventSparkEmitter = ({ incomingSignals = [], onEnergyImpact }) => {
  const [activeSparks, setActiveSparks] = useState([]);

  useEffect(() => {
    setActiveSparks((current) => {
      const activeIds = new Set(current.map((spark) => spark.id));
      const newSparks = incomingSignals
        .filter((signal) => signal?.id && !activeIds.has(signal.id))
        .map((signal) => ({
          ...signal,
          startPos: randomFarStart(),
        }));

      return newSparks.length > 0 ? [...current, ...newSparks] : current;
    });
  }, [incomingSignals]);

  const handleImpact = (spark) => {
    setActiveSparks((current) => current.filter((item) => item.id !== spark.id));
    if (onEnergyImpact) {
      onEnergyImpact({
        id: spark.id,
        category: spark.category,
        score: spark.score,
        targetPos: spark.targetPos,
        mass_impact: spark.mass_impact ?? 0,
        momentum_burst: spark.momentum_burst ?? 0,
      });
    }
  };

  return (
    <>
      {activeSparks.map((spark) => (
        <DataSpark
          key={spark.id}
          startPos={spark.startPos}
          targetPos={spark.targetPos}
          score={spark.score}
          color={spark.color}
          physics_profile={spark.physics_profile}
          onImpact={() => handleImpact(spark)}
        />
      ))}
    </>
  );
};

export default EventSparkEmitter;
