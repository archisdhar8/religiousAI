import { cn } from "@/lib/utils";

interface ChatMessageProps {
  content: string;
  isUser: boolean;
  deity?: string;
  icon?: string;
}

export const ChatMessage = ({ content, isUser, deity, icon }: ChatMessageProps) => {
  return (
    <div
      className={cn(
        "flex gap-3 animate-fade-in",
        isUser ? "flex-row-reverse" : "flex-row"
      )}
    >
      {/* Avatar */}
      <div
        className={cn(
          "flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center text-lg",
          isUser
            ? "bg-secondary text-secondary-foreground"
            : "bg-celestial glow-gold-subtle"
        )}
      >
        {isUser ? "🙏" : icon || "✨"}
      </div>

      {/* Message bubble */}
      <div
        className={cn(
          "max-w-[80%] md:max-w-[70%] rounded-2xl px-4 py-3 font-body",
          isUser
            ? "bg-primary text-primary-foreground rounded-br-sm"
            : "bg-card border border-gold/20 rounded-bl-sm glow-gold-subtle"
        )}
      >
        {!isUser && deity && (
          <p className="text-xs text-gold font-medium mb-1 font-display tracking-wide">
            {deity} speaks:
          </p>
        )}
        <p className="text-sm md:text-base leading-relaxed whitespace-pre-wrap">
          {content}
        </p>
      </div>
    </div>
  );
};
