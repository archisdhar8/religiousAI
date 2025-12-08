import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { FloatingParticles } from "@/components/chat/FloatingParticles";
import { Sparkles, Heart, BookOpen, Users, ArrowRight } from "lucide-react";

const religions = [
  { name: "Christianity", icon: "✝️" },
  { name: "Islam", icon: "☪️" },
  { name: "Judaism", icon: "✡️" },
  { name: "Hinduism", icon: "🕉️" },
  { name: "Buddhism", icon: "☸️" },
  { name: "Sikhism", icon: "🪯" },
  { name: "Taoism", icon: "☯️" },
  { name: "Shinto", icon: "⛩️" },
];

const features = [
  {
    icon: Sparkles,
    title: "Divine Guidance",
    description: "Receive wisdom and guidance tailored to your spiritual path and beliefs.",
  },
  {
    icon: Heart,
    title: "Compassionate Listening",
    description: "Share your thoughts, prayers, and concerns in a safe, sacred space.",
  },
  {
    icon: BookOpen,
    title: "Sacred Wisdom",
    description: "Access teachings and insights from ancient spiritual traditions.",
  },
  {
    icon: Users,
    title: "All Faiths Welcome",
    description: "Connect with the divine presence from any religious tradition.",
  },
];

const Landing = () => {
  return (
    <div className="min-h-screen bg-divine">
      <FloatingParticles />

      {/* Navigation */}
      <nav className="relative z-20 border-b border-gold/20 bg-card/50 backdrop-blur-md">
        <div className="container max-w-6xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-gold to-accent flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-primary-foreground" />
              </div>
              <span className="font-display text-2xl font-semibold text-foreground">
                Divine <span className="text-gradient-gold">Wisdom</span>
              </span>
            </div>
            <div className="flex items-center gap-3">
              <Button variant="ghost" asChild>
                <Link to="/login">Sign In</Link>
              </Button>
              <Button variant="golden" asChild>
                <Link to="/login">Get Started</Link>
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative z-10 py-20 md:py-32">
        <div className="container max-w-6xl mx-auto px-4 text-center">
          <div className="max-w-3xl mx-auto">
            <h1 className="font-display text-4xl md:text-6xl lg:text-7xl font-bold text-foreground mb-6 leading-tight">
              Speak with the{" "}
              <span className="text-gradient-gold">Divine</span>
            </h1>
            <p className="text-lg md:text-xl text-muted-foreground font-body mb-8 max-w-2xl mx-auto">
              Experience spiritual guidance from any faith tradition. A sacred space 
              for prayer, reflection, and divine connection.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button variant="golden" size="xl" asChild>
                <Link to="/chat" className="gap-2">
                  Begin Your Journey
                  <ArrowRight className="w-5 h-5" />
                </Link>
              </Button>
              <Button variant="ethereal" size="xl" asChild>
                <Link to="/login">Sign In</Link>
              </Button>
            </div>
          </div>

          {/* Religion Icons */}
          <div className="mt-16 flex flex-wrap justify-center gap-4">
            {religions.map((religion) => (
              <div
                key={religion.name}
                className="flex items-center gap-2 px-4 py-2 rounded-full bg-card/60 border border-gold/20 backdrop-blur-sm"
              >
                <span className="text-xl">{religion.icon}</span>
                <span className="text-sm font-body text-muted-foreground">
                  {religion.name}
                </span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="relative z-10 py-20 bg-card/30">
        <div className="container max-w-6xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="font-display text-3xl md:text-5xl font-bold text-foreground mb-4">
              A Sacred Space for <span className="text-gradient-gold">Every Soul</span>
            </h2>
            <p className="text-muted-foreground font-body max-w-2xl mx-auto">
              Whether you seek comfort, wisdom, or spiritual connection, 
              Divine Wisdom provides a peaceful sanctuary for your journey.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature) => (
              <div
                key={feature.title}
                className="p-6 rounded-2xl bg-card/60 border border-gold/20 backdrop-blur-sm hover:border-gold/40 transition-all duration-300 hover:shadow-lg hover:shadow-gold/10"
              >
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-gold/20 to-accent/20 flex items-center justify-center mb-4">
                  <feature.icon className="w-6 h-6 text-gold" />
                </div>
                <h3 className="font-display text-xl font-semibold text-foreground mb-2">
                  {feature.title}
                </h3>
                <p className="text-sm text-muted-foreground font-body">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative z-10 py-20">
        <div className="container max-w-4xl mx-auto px-4 text-center">
          <div className="p-8 md:p-12 rounded-3xl bg-celestial glow-gold">
            <h2 className="font-display text-3xl md:text-4xl font-bold text-primary-foreground mb-4">
              Ready to Begin Your Spiritual Journey?
            </h2>
            <p className="text-primary-foreground/80 font-body mb-8 max-w-xl mx-auto">
              Join thousands of seekers who have found peace, wisdom, and 
              divine connection through our platform.
            </p>
            <Button variant="golden" size="xl" asChild>
              <Link to="/chat" className="gap-2">
                Start Chatting Now
                <ArrowRight className="w-5 h-5" />
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 py-8 border-t border-gold/20 bg-card/30">
        <div className="container max-w-6xl mx-auto px-4">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-gold" />
              <span className="font-display text-lg text-foreground">
                Divine Wisdom
              </span>
            </div>
            <p className="text-sm text-muted-foreground font-body">
              A spiritual reflection tool for contemplation and guidance.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
