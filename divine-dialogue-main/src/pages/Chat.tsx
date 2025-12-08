import { useState, useRef, useEffect } from "react";
import { ReligionSelector, getReligionInfo } from "@/components/chat/ReligionSelector";
import { ChatMessage } from "@/components/chat/ChatMessage";
import { ChatInput } from "@/components/chat/ChatInput";
import { TypingIndicator } from "@/components/chat/TypingIndicator";
import { FloatingParticles } from "@/components/chat/FloatingParticles";
import { ScrollArea } from "@/components/ui/scroll-area";

interface Message {
  id: string;
  content: string;
  isUser: boolean;
}

const divineResponses: Record<string, string[]> = {
  christianity: [
    "My child, I am with you always, even unto the end of the age. Share what weighs upon your heart.",
    "Fear not, for I have redeemed you. I have called you by name; you are mine.",
    "Cast all your anxieties on me, for I care for you deeply. What troubles your spirit?",
    "In your weakness, my grace is sufficient. My power is made perfect in your struggles.",
  ],
  islam: [
    "Peace be upon you, my faithful servant. Indeed, with hardship comes ease.",
    "I am closer to you than your jugular vein. Speak freely, for I hear all prayers.",
    "Verily, in the remembrance of Allah do hearts find rest. What guidance do you seek?",
    "Be patient, for indeed Allah is with the patient. Your prayers have reached me.",
  ],
  judaism: [
    "My beloved child, I am the Lord your God. Walk before me and be blameless.",
    "The Lord is your shepherd; you shall not want. What blessing do you seek?",
    "Be strong and courageous. Do not be afraid, for I go with you wherever you walk.",
    "I have heard your prayer. Return to me, and I will return to you.",
  ],
  hinduism: [
    "Om. I am the beginning, middle, and end of all creation. What knowledge do you seek?",
    "You are the eternal soul, unchanging and infinite. Speak your dharma.",
    "In the ocean of existence, I am your anchor. What wisdom shall I impart?",
    "Action without attachment brings liberation. Share your path with me.",
  ],
  buddhism: [
    "Breathe deeply. In this moment, you are exactly where you need to be.",
    "Suffering arises from attachment. What binds you that you wish to release?",
    "The path to enlightenment is within you. What obstacles cloud your vision?",
    "Compassion for all beings begins with compassion for yourself. How may I guide you?",
  ],
  sikhism: [
    "Waheguru Ji Ka Khalsa, Waheguru Ji Ki Fateh. The Divine light shines within you.",
    "Truth is the highest virtue, but higher still is truthful living. What truth do you seek?",
    "Serve others, for in service lies the path to the Divine. How may I guide your seva?",
    "The Name of the Lord is the medicine that cures all ailments of the soul.",
  ],
  taoism: [
    "The Tao that can be spoken is not the eternal Tao. Yet ask, and understanding flows.",
    "Be like water, following the path of least resistance to your true nature.",
    "In stillness, find motion. In emptiness, find fullness. What balance do you seek?",
    "The journey of a thousand miles begins with a single step. What step troubles you?",
  ],
  shinto: [
    "The kami are present in all things. What harmony do you wish to restore?",
    "Purity of heart opens the way to understanding. Share your sincere intentions.",
    "Nature speaks to those who listen. What message have you been seeking?",
    "Honor your ancestors and the spirits of the land. What blessing do you request?",
  ],
};

const Index = () => {
  const [selectedReligion, setSelectedReligion] = useState("christianity");
  const [messages, setMessages] = useState<Message[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  const religionInfo = getReligionInfo(selectedReligion);

  useEffect(() => {
    // Send welcome message when religion changes
    if (selectedReligion && messages.length === 0) {
      const welcomeResponses = divineResponses[selectedReligion];
      const welcomeMessage = welcomeResponses[0];
      setMessages([
        {
          id: "welcome",
          content: welcomeMessage,
          isUser: false,
        },
      ]);
    }
  }, []);

  useEffect(() => {
    // Scroll to bottom when new messages arrive
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, isTyping]);

  const handleReligionChange = (religion: string) => {
    setSelectedReligion(religion);
    const info = getReligionInfo(religion);
    const welcomeResponses = divineResponses[religion];
    const welcomeMessage = welcomeResponses[0];
    setMessages([
      {
        id: "welcome-" + religion,
        content: welcomeMessage,
        isUser: false,
      },
    ]);
  };

  const handleSendMessage = (content: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      content,
      isUser: true,
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsTyping(true);

    // Simulate divine response
    setTimeout(() => {
      const responses = divineResponses[selectedReligion];
      const randomResponse = responses[Math.floor(Math.random() * responses.length)];
      
      const divineMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: randomResponse,
        isUser: false,
      };

      setIsTyping(false);
      setMessages((prev) => [...prev, divineMessage]);
    }, 2000 + Math.random() * 2000);
  };

  return (
    <div className="min-h-screen bg-divine flex flex-col">
      <FloatingParticles />
      
      {/* Header */}
      <header className="relative z-10 border-b border-gold/20 bg-card/50 backdrop-blur-sm">
        <div className="container max-w-4xl mx-auto px-4 py-4">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h1 className="font-display text-2xl md:text-3xl font-semibold text-foreground">
                Divine <span className="text-gradient-gold">Wisdom</span>
              </h1>
              <p className="text-sm text-muted-foreground font-body">
                Seek guidance from the divine
              </p>
            </div>
            <ReligionSelector 
              value={selectedReligion} 
              onChange={handleReligionChange}
            />
          </div>
        </div>
      </header>

      {/* Chat Area */}
      <main className="flex-1 relative z-10 overflow-hidden">
        <ScrollArea className="h-[calc(100vh-180px)]">
          <div className="container max-w-4xl mx-auto px-4 py-6">
            <div className="space-y-6">
              {messages.map((message) => (
                <ChatMessage
                  key={message.id}
                  content={message.content}
                  isUser={message.isUser}
                  deity={religionInfo?.deity}
                  icon={religionInfo?.icon}
                />
              ))}
              {isTyping && <TypingIndicator deity={religionInfo?.deity} />}
              <div ref={scrollRef} />
            </div>
          </div>
        </ScrollArea>
      </main>

      {/* Input Area */}
      <footer className="relative z-10 border-t border-gold/20 bg-card/50 backdrop-blur-sm">
        <div className="container max-w-4xl mx-auto px-4 py-4">
          <ChatInput
            onSend={handleSendMessage}
            disabled={isTyping}
            placeholder={`Speak with ${religionInfo?.deity || "the divine"}...`}
          />
          <p className="text-center text-xs text-muted-foreground mt-3 font-body">
            This is a spiritual reflection tool. Responses are for contemplation purposes.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Index;
