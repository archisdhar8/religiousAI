import { useState, useRef, useEffect, useCallback } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { ReligionSelector, getReligionInfo } from "@/components/chat/ReligionSelector";
import { ChatMessage } from "@/components/chat/ChatMessage";
import { ChatInput } from "@/components/chat/ChatInput";
import { TypingIndicator } from "@/components/chat/TypingIndicator";
import { FloatingParticles } from "@/components/chat/FloatingParticles";
import { ConversationPrompts } from "@/components/chat/ConversationPrompts";
import { ChatHistory } from "@/components/chat/ChatHistory";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { 
  sendChatMessage, 
  getGreeting, 
  getSessionId, 
  isAuthenticated, 
  getStoredUser, 
  logout,
  getChats,
  createChat,
  getChatById,
  ChatSummary,
} from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import { User, LogOut, Users, Home, PanelLeftClose, PanelLeft } from "lucide-react";

interface Message {
  id: string;
  content: string;
  isUser: boolean;
}

const Index = () => {
  const [searchParams] = useSearchParams();
  const religionFromUrl = searchParams.get("religion");
  const [selectedReligion, setSelectedReligion] = useState(
    religionFromUrl || "christianity"
  );
  const [messages, setMessages] = useState<Message[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [isInitialized, setIsInitialized] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const { toast } = useToast();
  const navigate = useNavigate();

  // Auth state
  const [user, setUser] = useState(getStoredUser());
  const isLoggedIn = isAuthenticated();

  // Chat history state
  const [chats, setChats] = useState<ChatSummary[]>([]);
  const [currentChatId, setCurrentChatId] = useState<string | undefined>();
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false); // Desktop sidebar state
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false); // Mobile overlay state
  const [isLoadingChats, setIsLoadingChats] = useState(true);

  const religionInfo = getReligionInfo(selectedReligion);

  // Load chat history
  const loadChats = useCallback(async (setCurrent: boolean = false): Promise<string | undefined> => {
    try {
      setIsLoadingChats(true);
      const response = await getChats();
      setChats(response.chats);
      // Only set current chat ID on initial load if we don't have one
      if (setCurrent && response.current_chat_id) {
        setCurrentChatId(response.current_chat_id);
        return response.current_chat_id;
      }
      return undefined;
    } catch (error) {
      console.error("Failed to load chats:", error);
      return undefined;
    } finally {
      setIsLoadingChats(false);
    }
  }, []);

  // Load a specific chat's messages
  const loadChatMessages = useCallback(async (chatId: string) => {
    try {
      console.log("Loading chat messages for:", chatId);
      const chat = await getChatById(chatId);
      console.log("Got chat:", chat);
      
      setCurrentChatId(chatId);
      
      // Set religion from chat if available
      if (chat.religion) {
        setSelectedReligion(chat.religion);
      }
      
      // Convert chat messages to our Message format
      if (chat.messages && chat.messages.length > 0) {
        const loadedMessages: Message[] = chat.messages.map((msg, idx) => ({
          id: `${chatId}-${idx}`,
          content: msg.content,
          isUser: msg.role === "user",
        }));
        console.log("Setting messages:", loadedMessages);
        setMessages(loadedMessages);
      } else {
        // Empty chat, show greeting
        console.log("Empty chat, showing greeting");
        setMessages([
          {
            id: "welcome",
            content: "Welcome, seeker. I am here to offer guidance drawn from the sacred wisdom of humanity's great spiritual traditions. Share with me what weighs upon your heart, and together we shall find light for your path.",
            isUser: false,
          },
        ]);
      }
    } catch (error) {
      console.error("Failed to load chat:", error);
      toast({
        title: "Error",
        description: "Failed to load conversation",
        variant: "destructive",
      });
    }
  }, [toast]);

  const loadInitialGreeting = useCallback(async () => {
    try {
      const greetingResponse = await getGreeting();
      if (greetingResponse.greeting) {
        setMessages([
          {
            id: "welcome",
            content: greetingResponse.greeting,
            isUser: false,
          },
        ]);
      }
    } catch (error) {
      console.error("Failed to load greeting:", error);
      // Fallback welcome message
      setMessages([
        {
          id: "welcome",
          content: "Welcome, seeker. I am here to offer guidance drawn from the sacred wisdom of humanity's great spiritual traditions. Share with me what weighs upon your heart, and together we shall find light for your path.",
          isUser: false,
        },
      ]);
    }
  }, []);

  // Track if we're in the middle of sending a message
  const [isSendingMessage, setIsSendingMessage] = useState(false);

  // Initialize on mount
  useEffect(() => {
    const initialize = async () => {
      // Load chat history and get current chat ID
      const chatId = await loadChats(true);
      
      if (chatId) {
        // Load the current chat's messages
        const chat = await getChatById(chatId);
        if (chat.messages && chat.messages.length > 0) {
          const loadedMessages: Message[] = chat.messages.map((msg, idx) => ({
            id: `${chatId}-${idx}`,
            content: msg.content,
            isUser: msg.role === "user",
          }));
          setMessages(loadedMessages);
        } else {
          loadInitialGreeting();
        }
      } else {
        // No existing chats, show greeting
        loadInitialGreeting();
      }
      
      setIsInitialized(true);
    };
    
    if (!isInitialized) {
      initialize();
    }
  }, [isInitialized, loadChats, loadInitialGreeting]);

  useEffect(() => {
    // Only auto-scroll to bottom if user has sent messages (conversation has started)
    // Don't scroll on initial load when only welcome message is present
    const hasUserMessages = messages.some((msg) => msg.isUser);
    if (hasUserMessages && scrollRef.current) {
      // Small delay to ensure DOM is updated
      setTimeout(() => {
        scrollRef.current?.scrollIntoView({ behavior: "smooth" });
      }, 100);
    }
  }, [messages, isTyping]);

  // Update user state when auth changes
  useEffect(() => {
    setUser(getStoredUser());
  }, []);

  // Update religion from URL params if present
  useEffect(() => {
    const religionFromUrl = searchParams.get("religion");
    if (religionFromUrl) {
      // Validate religion ID exists in available religions
      const validReligions = ["christianity", "islam", "judaism", "hinduism", "buddhism", "sikhism", "taoism", "shinto"];
      if (validReligions.includes(religionFromUrl) && religionFromUrl !== selectedReligion) {
        setSelectedReligion(religionFromUrl);
        // Reset messages and load new greeting when religion changes from URL
        setMessages([]);
        setIsInitialized(false);
      }
    }
  }, [searchParams, selectedReligion]);

  const handleReligionChange = (religion: string) => {
    setSelectedReligion(religion);
    // Reset messages and load new greeting when religion changes
    loadInitialGreeting();
  };

  // Handle creating a new chat
  const handleNewChat = async () => {
    try {
      const newChat = await createChat(selectedReligion);
      setCurrentChatId(newChat.id);
      setMessages([]);
      await loadInitialGreeting();
      // Refresh the chat list to show all chats including the new one
      await loadChats(false);
    } catch (error) {
      console.error("Failed to create new chat:", error);
      toast({
        title: "Error",
        description: "Failed to create new conversation",
        variant: "destructive",
      });
    }
  };

  // Handle selecting a chat from history
  const handleSelectChat = (chatId: string) => {
    if (chatId === currentChatId) return;
    loadChatMessages(chatId);
  };

  const handleLogout = async () => {
    await logout();
    setUser(null);
    toast({
      title: "Logged out",
      description: "Come back soon, seeker.",
    });
  };

  const handleSendMessage = async (content: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      content,
      isUser: true,
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsTyping(true);
    setIsSendingMessage(true);

    try {
      // Build conversation history for context
      const conversationHistory = messages
        .filter((msg) => !msg.id.startsWith("welcome"))
        .reduce<Array<{ question: string; answer: string }>>((acc, msg, idx, arr) => {
          if (msg.isUser && idx < arr.length - 1) {
            const nextMsg = arr[idx + 1];
            if (!nextMsg.isUser) {
              acc.push({
                question: msg.content,
                answer: nextMsg.content,
              });
            }
          }
          return acc;
        }, []);

      // Send message to API
      const response = await sendChatMessage({
        message: content,
        religion: selectedReligion,
        session_id: getSessionId(),
        chat_id: currentChatId,
        conversation_history: conversationHistory,
        mode: "standard",
      });

      // Update current chat ID if returned from API (happens on first message)
      if (response.chat_id) {
        if (response.chat_id !== currentChatId) {
          setCurrentChatId(response.chat_id);
        }
        // Always refresh chat list to update preview/title
        await loadChats(false);
      }

      const divineMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: response.response,
        isUser: false,
      };

      setIsTyping(false);
      setIsSendingMessage(false);
      setMessages((prev) => [...prev, divineMessage]);

      // Show crisis alert if needed
      if (response.is_crisis) {
        toast({
          title: "Important Notice",
          description: "If you're in crisis, please reach out to professional help immediately.",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error("Failed to send message:", error);
      setIsTyping(false);
      setIsSendingMessage(false);
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "I apologize, but I'm having trouble connecting right now. Please try again in a moment.",
        isUser: false,
      };
      
      setMessages((prev) => [...prev, errorMessage]);
      
      toast({
        title: "Connection Error",
        description: error instanceof Error ? error.message : "Failed to send message. Please try again.",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="min-h-screen bg-divine flex">
      <FloatingParticles />
      
      {/* Chat History Sidebar */}
      <aside className="relative z-20 h-screen hidden md:block">
        <ChatHistory
          chats={chats}
          currentChatId={currentChatId}
          onSelectChat={handleSelectChat}
          onNewChat={handleNewChat}
          onRefresh={() => loadChats(false)}
          isCollapsed={isSidebarCollapsed}
          onToggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
        />
      </aside>
      
      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="relative z-10 border-b border-gold/20 bg-card/50 backdrop-blur-sm">
          <div className="px-4 py-4">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 max-w-4xl mx-auto">
              <div className="flex items-center justify-between">
                {/* Mobile sidebar toggle */}
                <Button 
                  variant="ghost" 
                  size="icon" 
                  onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                  className="md:hidden hover:bg-gold/10 mr-2"
                  title="Toggle chat history"
                >
                  {isMobileMenuOpen ? <PanelLeftClose className="h-5 w-5" /> : <PanelLeft className="h-5 w-5" />}
                </Button>
                
                <Link to="/" className="hover:opacity-80 transition-opacity">
                  <div>
                    <h1 className="font-display text-2xl md:text-3xl font-semibold text-foreground">
                      Divine <span className="text-gradient-gold">Wisdom</span>
                    </h1>
                    <p className="text-sm text-muted-foreground font-body">
                      Seek guidance from the divine
                    </p>
                  </div>
                </Link>
                
                {/* Account Button - Mobile visible, desktop in flex row */}
                <div className="md:hidden flex items-center gap-2">
                  <Button 
                    variant="ghost" 
                    size="icon" 
                    onClick={() => navigate("/")}
                    className="hover:bg-gold/10"
                    title="Go to Homepage"
                  >
                    <Home className="h-5 w-5" />
                  </Button>
                  {isLoggedIn && user ? (
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon" className="rounded-full">
                          <div className="w-9 h-9 rounded-full bg-gradient-to-br from-gold to-accent flex items-center justify-center">
                            <span className="text-sm font-semibold text-primary-foreground">
                              {user.name?.charAt(0).toUpperCase() || user.email?.charAt(0).toUpperCase()}
                            </span>
                          </div>
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end" className="w-56">
                        <DropdownMenuLabel>
                          <div className="flex flex-col">
                            <span className="font-medium">{user.name || "Seeker"}</span>
                            <span className="text-xs text-muted-foreground">{user.email}</span>
                          </div>
                        </DropdownMenuLabel>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem onClick={() => navigate("/community")}>
                          <Users className="mr-2 h-4 w-4" />
                          Community
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={handleLogout}>
                          <LogOut className="mr-2 h-4 w-4" />
                          Sign out
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  ) : (
                    <Button variant="golden" size="sm" onClick={() => navigate("/login")}>
                      Sign In
                    </Button>
                  )}
                </div>
              </div>
              
              <div className="flex items-center gap-3">
                <Button 
                  variant="ghost" 
                  size="icon" 
                  onClick={() => navigate("/")}
                  className="hidden md:flex hover:bg-gold/10"
                  title="Go to Homepage"
                >
                  <Home className="h-5 w-5" />
                </Button>
                
                <ReligionSelector 
                  value={selectedReligion} 
                  onChange={handleReligionChange}
                />
                
                {/* Account Button - Desktop */}
                <div className="hidden md:block">
                  {isLoggedIn && user ? (
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon" className="rounded-full hover:bg-gold/10">
                          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-gold to-accent flex items-center justify-center">
                            <span className="text-sm font-semibold text-primary-foreground">
                              {user.name?.charAt(0).toUpperCase() || user.email?.charAt(0).toUpperCase()}
                            </span>
                          </div>
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end" className="w-56">
                        <DropdownMenuLabel>
                          <div className="flex flex-col">
                            <span className="font-medium">{user.name || "Seeker"}</span>
                            <span className="text-xs text-muted-foreground">{user.email}</span>
                          </div>
                        </DropdownMenuLabel>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem onClick={() => navigate("/community")}>
                          <Users className="mr-2 h-4 w-4" />
                          Community
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={handleLogout}>
                          <LogOut className="mr-2 h-4 w-4" />
                          Sign out
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  ) : (
                    <Button variant="golden" size="sm" onClick={() => navigate("/login")}>
                      <User className="mr-2 h-4 w-4" />
                      Sign In
                    </Button>
                  )}
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* Chat Area */}
        <main className="flex-1 relative z-10 overflow-hidden">
          <ScrollArea className="h-[calc(100vh-180px)]">
            <div className="max-w-4xl mx-auto px-4 py-6">
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

        {/* Input Area - Sticky at bottom */}
        <footer className="sticky bottom-0 z-10 border-t border-gold/20 bg-card/50 backdrop-blur-sm">
          <div className="max-w-4xl mx-auto px-4 py-4">
            {/* Show prompts only when there's only the welcome message (no user messages yet) */}
            <ConversationPrompts
              religion={selectedReligion}
              onPromptClick={handleSendMessage}
              visible={messages.filter((msg) => msg.isUser).length === 0 && !isTyping}
            />
            
            <div className="mt-6">
              <ChatInput
                onSend={handleSendMessage}
                disabled={isTyping}
                placeholder={`Speak with ${religionInfo?.deity || "the divine"}...`}
              />
            </div>
            <p className="text-center text-xs text-muted-foreground mt-3 font-body">
              This is a spiritual reflection tool. Responses are for contemplation purposes.
            </p>
          </div>
        </footer>
      </div>
      
      {/* Mobile Sidebar Overlay */}
      {isMobileMenuOpen && (
        <div className="md:hidden fixed inset-0 z-30">
          <div 
            className="absolute inset-0 bg-black/50" 
            onClick={() => setIsMobileMenuOpen(false)}
          />
          <div className="absolute left-0 top-0 h-full">
            <ChatHistory
              chats={chats}
              currentChatId={currentChatId}
              onSelectChat={(chatId) => {
                handleSelectChat(chatId);
                setIsMobileMenuOpen(false);
              }}
              onNewChat={() => {
                handleNewChat();
                setIsMobileMenuOpen(false);
              }}
              onRefresh={() => loadChats(false)}
              isCollapsed={false}
              onToggleCollapse={() => setIsMobileMenuOpen(false)}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default Index;
