export const TypingIndicator = ({ deity }: { deity?: string }) => {
  return (
    <div className="flex gap-3 animate-fade-in">
      <div className="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center text-lg bg-celestial glow-gold-subtle">
        ✨
      </div>
      <div className="bg-card border border-gold/20 rounded-2xl rounded-bl-sm px-4 py-3 glow-gold-subtle">
        {deity && (
          <p className="text-xs text-gold font-medium mb-2 font-display tracking-wide">
            {deity} is contemplating...
          </p>
        )}
        <div className="flex gap-1.5">
          <span className="w-2 h-2 rounded-full bg-gold/60 animate-typing-1" />
          <span className="w-2 h-2 rounded-full bg-gold/60 animate-typing-2" />
          <span className="w-2 h-2 rounded-full bg-gold/60 animate-typing-3" />
        </div>
      </div>
    </div>
  );
};
