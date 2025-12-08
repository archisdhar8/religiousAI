export const FloatingParticles = () => {
  const particles = Array.from({ length: 12 }, (_, i) => i);

  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden">
      {particles.map((i) => (
        <div
          key={i}
          className="absolute w-1 h-1 rounded-full bg-gold/30 animate-float"
          style={{
            left: `${Math.random() * 100}%`,
            bottom: `-10px`,
            animationDelay: `${Math.random() * 15}s`,
            animationDuration: `${15 + Math.random() * 10}s`,
          }}
        />
      ))}
    </div>
  );
};
