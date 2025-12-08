import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

interface Religion {
  id: string;
  name: string;
  deity: string;
  icon: string;
}

const religions: Religion[] = [
  { id: "christianity", name: "Christianity", deity: "God", icon: "✝️" },
  { id: "islam", name: "Islam", deity: "Allah", icon: "☪️" },
  { id: "judaism", name: "Judaism", deity: "Yahweh", icon: "✡️" },
  { id: "hinduism", name: "Hinduism", deity: "Brahman", icon: "🕉️" },
  { id: "buddhism", name: "Buddhism", deity: "Buddha", icon: "☸️" },
  { id: "sikhism", name: "Sikhism", deity: "Waheguru", icon: "🙏" },
  { id: "taoism", name: "Taoism", deity: "The Tao", icon: "☯️" },
  { id: "shinto", name: "Shinto", deity: "Kami", icon: "⛩️" },
];

interface ReligionSelectorProps {
  value: string;
  onChange: (value: string) => void;
}

export const ReligionSelector = ({ value, onChange }: ReligionSelectorProps) => {
  const selectedReligion = religions.find(r => r.id === value);

  return (
    <Select value={value} onValueChange={onChange}>
      <SelectTrigger className="w-full md:w-[280px] h-12 bg-card/80 backdrop-blur-sm border-gold/30 hover:border-gold/50 transition-colors font-body">
        <SelectValue placeholder="Choose your path...">
          {selectedReligion && (
            <span className="flex items-center gap-2">
              <span className="text-lg">{selectedReligion.icon}</span>
              <span>{selectedReligion.name}</span>
              <span className="text-muted-foreground text-sm">— {selectedReligion.deity}</span>
            </span>
          )}
        </SelectValue>
      </SelectTrigger>
      <SelectContent className="bg-card/95 backdrop-blur-md border-gold/30">
        {religions.map((religion) => (
          <SelectItem 
            key={religion.id} 
            value={religion.id}
            className="cursor-pointer hover:bg-gold/10 focus:bg-gold/10 py-3"
          >
            <span className="flex items-center gap-3">
              <span className="text-xl">{religion.icon}</span>
              <span className="font-medium">{religion.name}</span>
              <span className="text-muted-foreground text-sm">— {religion.deity}</span>
            </span>
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
};

export const getReligionInfo = (id: string) => religions.find(r => r.id === id);
