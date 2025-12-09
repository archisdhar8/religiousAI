import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { FloatingParticles } from "@/components/chat/FloatingParticles";
import { Sparkles, Mail, Lock, ArrowRight, Eye, EyeOff, User } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { signUp, login } from "@/lib/api";

const Login = () => {
  const [isSignUp, setIsSignUp] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      if (isSignUp) {
        // Sign up
        const response = await signUp({
          email,
          password,
          name: name || undefined,
        });

        if (response.success) {
          toast({
            title: "Account created!",
            description: "Welcome to Divine Wisdom. Redirecting...",
          });
          navigate("/chat");
        }
      } else {
        // Login
        const response = await login({ email, password });

        if (response.success) {
          toast({
            title: "Welcome back!",
            description: "Redirecting to your divine conversation...",
          });
          navigate("/chat");
        }
      }
    } catch (error) {
      toast({
        title: isSignUp ? "Sign up failed" : "Login failed",
        description: error instanceof Error ? error.message : "Please try again",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-divine flex flex-col">
      <FloatingParticles />

      {/* Navigation */}
      <nav className="relative z-20 border-b border-gold/20 bg-card/50 backdrop-blur-md">
        <div className="container max-w-6xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link to="/" className="flex items-center gap-2">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-gold to-accent flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-primary-foreground" />
              </div>
              <span className="font-display text-2xl font-semibold text-foreground">
                Divine <span className="text-gradient-gold">Wisdom</span>
              </span>
            </Link>
          </div>
        </div>
      </nav>

      {/* Login Form */}
      <main className="flex-1 relative z-10 flex items-center justify-center py-12 px-4">
        <div className="w-full max-w-md">
          <div className="bg-card/60 backdrop-blur-sm border border-gold/20 rounded-3xl p-8 shadow-xl">
            <div className="text-center mb-8">
              <div className="w-16 h-16 mx-auto rounded-full bg-gradient-to-br from-gold to-accent flex items-center justify-center mb-4">
                <Sparkles className="w-8 h-8 text-primary-foreground" />
              </div>
              <h1 className="font-display text-3xl font-bold text-foreground mb-2">
                {isSignUp ? "Create Account" : "Welcome Back"}
              </h1>
              <p className="text-muted-foreground font-body">
                {isSignUp
                  ? "Begin your spiritual journey today"
                  : "Continue your divine conversation"}
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              {/* Name field - only show on sign up */}
              {isSignUp && (
                <div className="space-y-2">
                  <Label htmlFor="name" className="font-body">
                    Name (optional)
                  </Label>
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                    <Input
                      id="name"
                      type="text"
                      placeholder="Your name"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      className="pl-10 bg-background/50 border-gold/30 focus:border-gold"
                    />
                  </div>
                </div>
              )}

              <div className="space-y-2">
                <Label htmlFor="email" className="font-body">
                  Email
                </Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                  <Input
                    id="email"
                    type="email"
                    placeholder="your@email.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="pl-10 bg-background/50 border-gold/30 focus:border-gold"
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="password" className="font-body">
                  Password
                </Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                  <Input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="pl-10 pr-10 bg-background/50 border-gold/30 focus:border-gold"
                    required
                    minLength={6}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                  >
                    {showPassword ? (
                      <EyeOff className="w-5 h-5" />
                    ) : (
                      <Eye className="w-5 h-5" />
                    )}
                  </button>
                </div>
                {isSignUp && (
                  <p className="text-xs text-muted-foreground">
                    Password must be at least 6 characters
                  </p>
                )}
              </div>

              <Button
                type="submit"
                variant="golden"
                size="lg"
                className="w-full"
                disabled={isLoading}
              >
                {isLoading ? (
                  <span className="flex items-center gap-2">
                    <span className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                    {isSignUp ? "Creating account..." : "Signing in..."}
                  </span>
                ) : (
                  <span className="flex items-center gap-2">
                    {isSignUp ? "Create Account" : "Sign In"}
                    <ArrowRight className="w-4 h-4" />
                  </span>
                )}
              </Button>
            </form>

            <div className="mt-6 text-center">
              <p className="text-sm text-muted-foreground font-body">
                {isSignUp ? "Already have an account?" : "Don't have an account?"}{" "}
                <button
                  onClick={() => {
                    setIsSignUp(!isSignUp);
                    setName("");
                  }}
                  className="text-gold hover:text-gold/80 font-medium transition-colors"
                >
                  {isSignUp ? "Sign In" : "Sign Up"}
                </button>
              </p>
            </div>

            <div className="mt-6 pt-6 border-t border-gold/20 text-center">
              <Link
                to="/chat"
                className="text-sm text-muted-foreground hover:text-foreground font-body transition-colors"
              >
                Continue as guest →
              </Link>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Login;
