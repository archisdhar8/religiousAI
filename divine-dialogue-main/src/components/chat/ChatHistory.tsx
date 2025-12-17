import { useState } from "react";
import { ChatSummary, deleteChatById, renameChat } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { 
  MessageSquare, 
  Plus, 
  MoreHorizontal, 
  Pencil, 
  Trash2, 
  X,
  Check,
  ChevronLeft,
  ChevronRight
} from "lucide-react";
import { cn } from "@/lib/utils";

interface ChatHistoryProps {
  chats: ChatSummary[];
  currentChatId?: string;
  onSelectChat: (chatId: string) => void;
  onNewChat: () => void;
  onRefresh: () => void;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

export function ChatHistory({
  chats,
  currentChatId,
  onSelectChat,
  onNewChat,
  onRefresh,
  isCollapsed,
  onToggleCollapse,
}: ChatHistoryProps) {
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState("");
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isRenaming, setIsRenaming] = useState(false);

  const handleStartRename = (chat: ChatSummary) => {
    setEditingId(chat.id);
    setEditTitle(chat.title);
  };

  const handleSaveRename = async () => {
    if (!editingId || !editTitle.trim()) return;
    
    setIsRenaming(true);
    try {
      await renameChat(editingId, editTitle.trim());
      onRefresh();
    } catch (error) {
      console.error("Failed to rename chat:", error);
    } finally {
      setIsRenaming(false);
      setEditingId(null);
    }
  };

  const handleCancelRename = () => {
    setEditingId(null);
    setEditTitle("");
  };

  const handleDelete = async () => {
    if (!deleteId) return;
    
    setIsDeleting(true);
    try {
      await deleteChatById(deleteId);
      onRefresh();
    } catch (error) {
      console.error("Failed to delete chat:", error);
    } finally {
      setIsDeleting(false);
      setDeleteId(null);
    }
  };

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return "";
    const date = new Date(dateStr);
    const now = new Date();
    const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return "Today";
    if (diffDays === 1) return "Yesterday";
    if (diffDays < 7) return `${diffDays} days ago`;
    return date.toLocaleDateString();
  };

  // Group chats by date
  const groupedChats = chats.reduce<Record<string, ChatSummary[]>>((acc, chat) => {
    const label = formatDate(chat.updated_at);
    if (!acc[label]) acc[label] = [];
    acc[label].push(chat);
    return acc;
  }, {});

  if (isCollapsed) {
    return (
      <div className="h-full flex flex-col bg-card/30 border-r border-gold/10">
        <Button
          variant="ghost"
          size="icon"
          onClick={onToggleCollapse}
          className="m-2 hover:bg-gold/10"
          title="Expand sidebar"
        >
          <ChevronRight className="h-5 w-5" />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          onClick={onNewChat}
          className="m-2 hover:bg-gold/10"
          title="New chat"
        >
          <Plus className="h-5 w-5" />
        </Button>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-card/30 border-r border-gold/10 w-64">
      {/* Header - Fixed */}
      <div className="flex items-center justify-between p-3 border-b border-gold/10 shrink-0">
        <Button
          variant="ghost"
          size="icon"
          onClick={onToggleCollapse}
          className="hover:bg-gold/10"
          title="Collapse sidebar"
        >
          <ChevronLeft className="h-5 w-5" />
        </Button>
        <span className="font-display text-sm font-medium text-foreground/80">Conversations</span>
        <Button
          variant="ghost"
          size="icon"
          onClick={onNewChat}
          className="hover:bg-gold/10"
          title="New conversation"
        >
          <Plus className="h-5 w-5" />
        </Button>
      </div>

      {/* Chat List - Scrollable inside fixed sidebar */}
      <div className="flex-1 min-h-0 overflow-y-auto">
        <div className="p-2 space-y-4">
          {Object.entries(groupedChats).map(([dateLabel, dateChats]) => (
            <div key={dateLabel}>
              <p className="text-xs text-muted-foreground px-2 mb-2 font-medium">
                {dateLabel}
              </p>
              <div className="space-y-1">
                {dateChats.map((chat) => (
                  <div
                    key={chat.id}
                    className={cn(
                      "group relative rounded-lg transition-colors",
                      currentChatId === chat.id
                        ? "bg-gold/20"
                        : "hover:bg-gold/10"
                    )}
                  >
                    {editingId === chat.id ? (
                      <div className="flex items-center gap-1 p-2">
                        <Input
                          value={editTitle}
                          onChange={(e) => setEditTitle(e.target.value)}
                          className="h-7 text-sm"
                          autoFocus
                          onKeyDown={(e) => {
                            if (e.key === "Enter") handleSaveRename();
                            if (e.key === "Escape") handleCancelRename();
                          }}
                        />
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-7 w-7 shrink-0"
                          onClick={handleSaveRename}
                          disabled={isRenaming}
                        >
                          <Check className="h-4 w-4 text-green-500" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-7 w-7 shrink-0"
                          onClick={handleCancelRename}
                        >
                          <X className="h-4 w-4 text-red-500" />
                        </Button>
                      </div>
                    ) : (
                      <button
                        onClick={() => onSelectChat(chat.id)}
                        className="w-full text-left p-2 pr-12 relative"
                      >
                        <div className="flex items-center gap-2">
                          <MessageSquare className="h-4 w-4 shrink-0 text-gold/60" />
                          <div className="min-w-0 flex-1">
                            <p className="text-sm font-medium text-foreground/90 line-clamp-1">
                              {chat.title}
                            </p>
                          </div>
                        </div>
                      </button>
                    )}
                    
                    {/* Actions dropdown - Always visible */}
                    {editingId !== chat.id && (
                      <div className="absolute right-2 top-1/2 -translate-y-1/2 z-30 flex items-center">
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-8 w-8 hover:bg-gold/20 text-foreground/70 hover:text-foreground border-0 shadow-sm"
                              onClick={(e) => {
                                e.stopPropagation(); // Prevent chat selection when clicking menu
                                e.preventDefault();
                              }}
                              onMouseDown={(e) => {
                                e.stopPropagation(); // Prevent chat selection
                              }}
                            >
                              <MoreHorizontal className="h-5 w-5" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end" className="w-36 z-50" onClick={(e) => e.stopPropagation()}>
                            <DropdownMenuItem 
                              onClick={(e) => {
                                e.stopPropagation();
                                handleStartRename(chat);
                              }}
                            >
                              <Pencil className="mr-2 h-4 w-4" />
                              Rename
                            </DropdownMenuItem>
                            <DropdownMenuItem
                              onClick={(e) => {
                                e.stopPropagation();
                                setDeleteId(chat.id);
                              }}
                              className="text-red-500 focus:text-red-500"
                            >
                              <Trash2 className="mr-2 h-4 w-4" />
                              Delete
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))}

          {chats.length === 0 && (
            <div className="text-center py-8 px-4">
              <MessageSquare className="h-8 w-8 mx-auto mb-3 text-gold/40" />
              <p className="text-sm text-muted-foreground">
                No conversations yet
              </p>
              <p className="text-xs text-muted-foreground/60 mt-1">
                Start a new conversation to begin
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={!!deleteId} onOpenChange={() => setDeleteId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete conversation?</AlertDialogTitle>
            <AlertDialogDescription>
              This will permanently delete this conversation and all its messages.
              This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isDeleting}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              disabled={isDeleting}
              className="bg-red-500 hover:bg-red-600"
            >
              {isDeleting ? "Deleting..." : "Delete"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}

