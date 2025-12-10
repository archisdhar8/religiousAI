import { Button } from "@/components/ui/button";
import { Sparkles } from "lucide-react";

interface ConversationPromptsProps {
  religion: string;
  onPromptClick: (prompt: string) => void;
  visible: boolean;
}

const RELIGION_PROMPTS: Record<string, string[]> = {
  christianity: [
    "How can I find peace in times of uncertainty?",
    "What does forgiveness mean in my daily life?",
    "How do I strengthen my relationship with God?",
  ],
  islam: [
    "How can I practice gratitude in my daily life?",
    "What guidance does the Quran offer for difficult decisions?",
    "How do I find balance between faith and worldly responsibilities?",
  ],
  judaism: [
    "How can I find meaning in times of struggle?",
    "What does the Torah teach about living a righteous life?",
    "How do I maintain my connection to God in modern times?",
  ],
  hinduism: [
    "How can I find my dharma and purpose in life?",
    "What does the Bhagavad Gita teach about dealing with challenges?",
    "How do I practice detachment while staying engaged in the world?",
  ],
  buddhism: [
    "How can I practice mindfulness in stressful situations?",
    "What does the path to inner peace look like?",
    "How do I let go of attachments that cause suffering?",
  ],
  sikhism: [
    "How can I serve others while maintaining my spiritual practice?",
    "What does the Guru Granth Sahib teach about equality?",
    "How do I find the divine within myself and others?",
  ],
  taoism: [
    "How can I find harmony in the natural flow of life?",
    "What does the Tao Te Ching teach about simplicity?",
    "How do I practice wu wei (effortless action) in my daily life?",
  ],
  shinto: [
    "How can I connect with the kami (spirits) in nature?",
    "What does Shinto teach about purity and gratitude?",
    "How do I honor my ancestors and maintain family traditions?",
  ],
};

export const ConversationPrompts = ({
  religion,
  onPromptClick,
  visible,
}: ConversationPromptsProps) => {
  if (!visible) return null;

  const prompts = RELIGION_PROMPTS[religion] || RELIGION_PROMPTS.christianity;

  return (
    <div className="w-full">
      <div className="flex items-center gap-2 mb-3">
        <Sparkles className="h-4 w-4 text-gold" />
        <p className="text-sm text-muted-foreground font-body">
          Start a conversation:
        </p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {prompts.map((prompt, index) => (
          <Button
            key={index}
            variant="outline"
            onClick={() => onPromptClick(prompt)}
            className="h-auto min-h-[80px] py-4 px-4 text-left justify-start font-body text-sm bg-card/60 backdrop-blur-sm border-gold/30 hover:border-gold/60 hover:bg-gold/10 transition-all duration-200 rounded-xl group whitespace-normal"
          >
            <span className="group-hover:text-foreground text-muted-foreground transition-colors">
              {prompt}
            </span>
          </Button>
        ))}
      </div>
    </div>
  );
};

