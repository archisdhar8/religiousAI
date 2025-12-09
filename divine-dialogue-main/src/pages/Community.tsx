import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { FloatingParticles } from "@/components/chat/FloatingParticles";
import { useToast } from "@/hooks/use-toast";
import {
  isAuthenticated,
  getStoredUser,
  getCommunityProfile,
  createCommunityProfile,
  getMatches,
  getConnections,
  getConnectionRequests,
  sendConnectionRequest,
  respondToConnection,
  Match,
  Connection,
  ConnectionRequestData,
  CommunityProfile,
} from "@/lib/api";
import {
  Sparkles,
  Users,
  UserPlus,
  MessageCircle,
  Heart,
  Check,
  X,
  ArrowLeft,
  Loader2,
  Star,
} from "lucide-react";

const TRADITIONS = [
  { id: "christianity", name: "Christianity", icon: "✝️" },
  { id: "islam", name: "Islam", icon: "☪️" },
  { id: "buddhism", name: "Buddhism", icon: "☸️" },
  { id: "hinduism", name: "Hinduism", icon: "🕉️" },
  { id: "judaism", name: "Judaism", icon: "✡️" },
  { id: "taoism", name: "Taoism", icon: "☯️" },
  { id: "sikhism", name: "Sikhism", icon: "🙏" },
  { id: "interfaith", name: "Interfaith", icon: "🌍" },
];

const Community = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const user = getStoredUser();
  const isLoggedIn = isAuthenticated();

  // State
  const [loading, setLoading] = useState(true);
  const [profile, setProfile] = useState<CommunityProfile | null>(null);
  const [matches, setMatches] = useState<Match[]>([]);
  const [connections, setConnections] = useState<Connection[]>([]);
  const [requests, setRequests] = useState<ConnectionRequestData[]>([]);
  const [activeTab, setActiveTab] = useState("matches");

  // Profile form state
  const [displayName, setDisplayName] = useState("");
  const [bio, setBio] = useState("");
  const [selectedTraditions, setSelectedTraditions] = useState<string[]>([]);
  const [optIn, setOptIn] = useState(true);
  const [savingProfile, setSavingProfile] = useState(false);

  // Load data on mount
  useEffect(() => {
    if (!isLoggedIn) {
      navigate("/login");
      return;
    }

    loadData();
  }, [isLoggedIn, navigate]);

  const loadData = async () => {
    setLoading(true);
    try {
      // Load profile
      const profileRes = await getCommunityProfile();
      if (profileRes.profile) {
        setProfile(profileRes.profile);
        setDisplayName(profileRes.profile.display_name || "");
        setBio(profileRes.profile.bio || "");
        setSelectedTraditions(profileRes.profile.preferred_traditions || []);
        setOptIn(profileRes.profile.opt_in !== false);
      } else {
        // Set defaults from user
        setDisplayName(user?.name || "");
      }

      // Load matches if profile exists
      if (profileRes.profile?.opt_in) {
        const matchesRes = await getMatches();
        setMatches(matchesRes.matches || []);
      }

      // Load connections
      const connectionsRes = await getConnections();
      setConnections(connectionsRes.connections || []);

      // Load requests
      const requestsRes = await getConnectionRequests();
      setRequests(requestsRes.requests || []);
    } catch (error) {
      console.error("Error loading community data:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveProfile = async () => {
    setSavingProfile(true);
    try {
      const result = await createCommunityProfile({
        display_name: displayName,
        bio,
        preferred_traditions: selectedTraditions,
        opt_in: optIn,
      });

      if (result.success) {
        setProfile(result.profile);
        toast({
          title: "Profile saved!",
          description: "Your spiritual profile has been updated.",
        });

        // Reload matches if opted in
        if (optIn) {
          const matchesRes = await getMatches();
          setMatches(matchesRes.matches || []);
        }
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to save profile. Please try again.",
        variant: "destructive",
      });
    } finally {
      setSavingProfile(false);
    }
  };

  const handleConnect = async (match: Match) => {
    try {
      const result = await sendConnectionRequest(match.email, "I'd like to connect for spiritual conversation.");
      toast({
        title: result.success ? "Request sent!" : "Error",
        description: result.message,
        variant: result.success ? "default" : "destructive",
      });

      if (result.success) {
        // Refresh matches to update UI
        loadData();
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to send request. Please try again.",
        variant: "destructive",
      });
    }
  };

  const handleRespondToRequest = async (fromEmail: string, accept: boolean) => {
    try {
      const result = await respondToConnection(fromEmail, accept);
      toast({
        title: accept ? "Connected!" : "Request declined",
        description: result.message,
      });
      loadData();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to respond. Please try again.",
        variant: "destructive",
      });
    }
  };

  const toggleTradition = (traditionId: string) => {
    setSelectedTraditions((prev) =>
      prev.includes(traditionId)
        ? prev.filter((t) => t !== traditionId)
        : [...prev, traditionId]
    );
  };

  if (!isLoggedIn) {
    return null;
  }

  return (
    <div className="min-h-screen bg-divine">
      <FloatingParticles />

      {/* Header */}
      <header className="relative z-10 border-b border-gold/20 bg-card/50 backdrop-blur-sm">
        <div className="container max-w-5xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="icon" onClick={() => navigate("/chat")}>
                <ArrowLeft className="h-5 w-5" />
              </Button>
              <div>
                <h1 className="font-display text-2xl font-semibold text-foreground">
                  Spiritual <span className="text-gradient-gold">Community</span>
                </h1>
                <p className="text-sm text-muted-foreground font-body">
                  Connect with kindred spirits
                </p>
              </div>
            </div>
            <Link to="/chat">
              <Button variant="outline" size="sm">
                <MessageCircle className="mr-2 h-4 w-4" />
                Back to Chat
              </Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 container max-w-5xl mx-auto px-4 py-8">
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="h-8 w-8 animate-spin text-gold" />
          </div>
        ) : (
          <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
            <TabsList className="grid w-full grid-cols-4 bg-card/50">
              <TabsTrigger value="matches" className="gap-2">
                <Users className="h-4 w-4" />
                Matches
                {matches.length > 0 && (
                  <Badge variant="secondary" className="ml-1">{matches.length}</Badge>
                )}
              </TabsTrigger>
              <TabsTrigger value="connections" className="gap-2">
                <Heart className="h-4 w-4" />
                Connected
                {connections.length > 0 && (
                  <Badge variant="secondary" className="ml-1">{connections.length}</Badge>
                )}
              </TabsTrigger>
              <TabsTrigger value="requests" className="gap-2">
                <UserPlus className="h-4 w-4" />
                Requests
                {requests.length > 0 && (
                  <Badge variant="destructive" className="ml-1">{requests.length}</Badge>
                )}
              </TabsTrigger>
              <TabsTrigger value="profile" className="gap-2">
                <Sparkles className="h-4 w-4" />
                Profile
              </TabsTrigger>
            </TabsList>

            {/* Matches Tab */}
            <TabsContent value="matches" className="space-y-4">
              {!profile?.opt_in ? (
                <Card className="bg-card/60 border-gold/20">
                  <CardContent className="py-8 text-center">
                    <Users className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                    <h3 className="text-lg font-semibold mb-2">Enable Matching</h3>
                    <p className="text-muted-foreground mb-4">
                      Set up your profile and opt-in to discover spiritual companions.
                    </p>
                    <Button variant="golden" onClick={() => setActiveTab("profile")}>
                      Create Profile
                    </Button>
                  </CardContent>
                </Card>
              ) : matches.length === 0 ? (
                <Card className="bg-card/60 border-gold/20">
                  <CardContent className="py-8 text-center">
                    <Users className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                    <h3 className="text-lg font-semibold mb-2">No Matches Yet</h3>
                    <p className="text-muted-foreground">
                      Keep using Divine Wisdom to help us find compatible spiritual companions for you.
                    </p>
                  </CardContent>
                </Card>
              ) : (
                <div className="grid gap-4 md:grid-cols-2">
                  {matches.map((match) => (
                    <Card key={match.email} className="bg-card/60 border-gold/20 hover:border-gold/40 transition-colors">
                      <CardHeader className="pb-2">
                        <div className="flex items-start justify-between">
                          <div className="flex items-center gap-3">
                            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-gold to-accent flex items-center justify-center">
                              <span className="text-lg font-semibold text-primary-foreground">
                                {match.display_name.charAt(0).toUpperCase()}
                              </span>
                            </div>
                            <div>
                              <CardTitle className="text-lg">{match.display_name}</CardTitle>
                              <div className="flex items-center gap-1 text-gold">
                                <Star className="h-4 w-4 fill-current" />
                                <span className="text-sm font-medium">{match.compatibility_score}% match</span>
                              </div>
                            </div>
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        {match.bio && (
                          <p className="text-sm text-muted-foreground">{match.bio}</p>
                        )}
                        <div className="flex flex-wrap gap-1">
                          {match.preferred_traditions.slice(0, 3).map((trad) => {
                            const tradition = TRADITIONS.find((t) => t.id === trad.toLowerCase());
                            return (
                              <Badge key={trad} variant="outline" className="text-xs">
                                {tradition?.icon} {tradition?.name || trad}
                              </Badge>
                            );
                          })}
                        </div>
                        <div className="flex flex-wrap gap-1">
                          {match.matching_traits.slice(0, 3).map((trait, idx) => (
                            <Badge key={idx} variant="secondary" className="text-xs">
                              {trait.split(":")[1] || trait}
                            </Badge>
                          ))}
                        </div>
                        <Button
                          variant="golden"
                          size="sm"
                          className="w-full mt-2"
                          onClick={() => handleConnect(match)}
                        >
                          <UserPlus className="mr-2 h-4 w-4" />
                          Connect
                        </Button>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </TabsContent>

            {/* Connections Tab */}
            <TabsContent value="connections" className="space-y-4">
              {connections.length === 0 ? (
                <Card className="bg-card/60 border-gold/20">
                  <CardContent className="py-8 text-center">
                    <Heart className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                    <h3 className="text-lg font-semibold mb-2">No Connections Yet</h3>
                    <p className="text-muted-foreground">
                      Connect with matches to build your spiritual community.
                    </p>
                  </CardContent>
                </Card>
              ) : (
                <div className="grid gap-4 md:grid-cols-2">
                  {connections.map((conn) => (
                    <Card key={conn.email} className="bg-card/60 border-gold/20">
                      <CardContent className="py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-12 h-12 rounded-full bg-gradient-to-br from-gold to-accent flex items-center justify-center">
                            <span className="text-lg font-semibold text-primary-foreground">
                              {conn.display_name.charAt(0).toUpperCase()}
                            </span>
                          </div>
                          <div className="flex-1">
                            <h3 className="font-semibold">{conn.display_name}</h3>
                            <p className="text-sm text-muted-foreground">{conn.bio}</p>
                          </div>
                          <Badge variant="outline" className="bg-green-500/10 text-green-400 border-green-500/30">
                            <Check className="mr-1 h-3 w-3" />
                            Connected
                          </Badge>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </TabsContent>

            {/* Requests Tab */}
            <TabsContent value="requests" className="space-y-4">
              {requests.length === 0 ? (
                <Card className="bg-card/60 border-gold/20">
                  <CardContent className="py-8 text-center">
                    <UserPlus className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                    <h3 className="text-lg font-semibold mb-2">No Pending Requests</h3>
                    <p className="text-muted-foreground">
                      Connection requests from other seekers will appear here.
                    </p>
                  </CardContent>
                </Card>
              ) : (
                <div className="space-y-4">
                  {requests.map((req) => (
                    <Card key={req.from_email} className="bg-card/60 border-gold/20">
                      <CardContent className="py-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-gold to-accent flex items-center justify-center">
                              <span className="text-lg font-semibold text-primary-foreground">
                                {req.from_name.charAt(0).toUpperCase()}
                              </span>
                            </div>
                            <div>
                              <h3 className="font-semibold">{req.from_name}</h3>
                              <p className="text-sm text-muted-foreground">
                                {req.message || "Wants to connect with you"}
                              </p>
                            </div>
                          </div>
                          <div className="flex gap-2">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleRespondToRequest(req.from_email, false)}
                            >
                              <X className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="golden"
                              size="sm"
                              onClick={() => handleRespondToRequest(req.from_email, true)}
                            >
                              <Check className="mr-1 h-4 w-4" />
                              Accept
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </TabsContent>

            {/* Profile Tab */}
            <TabsContent value="profile">
              <Card className="bg-card/60 border-gold/20">
                <CardHeader>
                  <CardTitle>Your Spiritual Profile</CardTitle>
                  <CardDescription>
                    Help us find compatible spiritual companions by sharing about your journey.
                    Your conversation themes are automatically analyzed to find matches.
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="space-y-2">
                    <Label htmlFor="displayName">Display Name</Label>
                    <Input
                      id="displayName"
                      value={displayName}
                      onChange={(e) => setDisplayName(e.target.value)}
                      placeholder="How you'd like to be known"
                      className="bg-background/50"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="bio">About Your Journey</Label>
                    <Textarea
                      id="bio"
                      value={bio}
                      onChange={(e) => setBio(e.target.value)}
                      placeholder="Share a little about your spiritual journey and what you're seeking..."
                      className="bg-background/50 min-h-[100px]"
                    />
                  </div>

                  <div className="space-y-3">
                    <Label>Faith Traditions You Resonate With</Label>
                    <div className="flex flex-wrap gap-2">
                      {TRADITIONS.map((tradition) => (
                        <Badge
                          key={tradition.id}
                          variant={selectedTraditions.includes(tradition.id) ? "default" : "outline"}
                          className={`cursor-pointer transition-colors ${
                            selectedTraditions.includes(tradition.id)
                              ? "bg-gold text-primary-foreground hover:bg-gold/90"
                              : "hover:bg-gold/10"
                          }`}
                          onClick={() => toggleTradition(tradition.id)}
                        >
                          {tradition.icon} {tradition.name}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  <div className="flex items-center justify-between p-4 bg-background/30 rounded-lg">
                    <div>
                      <Label className="text-base">Enable Community Matching</Label>
                      <p className="text-sm text-muted-foreground">
                        Allow others to find and connect with you
                      </p>
                    </div>
                    <Switch checked={optIn} onCheckedChange={setOptIn} />
                  </div>

                  {profile?.traits && Object.keys(profile.traits).length > 0 && (
                    <div className="p-4 bg-background/30 rounded-lg space-y-2">
                      <Label className="text-sm text-muted-foreground">
                        AI-Detected Spiritual Themes (from your conversations)
                      </Label>
                      <div className="flex flex-wrap gap-1">
                        {Object.entries(profile.traits).map(([category, values]) =>
                          (values as string[]).map((value) => (
                            <Badge key={`${category}-${value}`} variant="secondary" className="text-xs">
                              {value.replace(/_/g, " ")}
                            </Badge>
                          ))
                        )}
                      </div>
                    </div>
                  )}

                  <Button
                    variant="golden"
                    className="w-full"
                    onClick={handleSaveProfile}
                    disabled={savingProfile || !displayName}
                  >
                    {savingProfile ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Saving...
                      </>
                    ) : (
                      <>
                        <Sparkles className="mr-2 h-4 w-4" />
                        Save Profile
                      </>
                    )}
                  </Button>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        )}
      </main>
    </div>
  );
};

export default Community;

