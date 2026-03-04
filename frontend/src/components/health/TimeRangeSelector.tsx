import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";

interface TimeRangeSelectorProps {
  value: number;
  onChange: (days: number) => void;
}

export function TimeRangeSelector({ value, onChange }: TimeRangeSelectorProps) {
  return (
    <Tabs value={String(value)} onValueChange={(v) => onChange(Number(v))}>
      <TabsList>
        <TabsTrigger value="7">7 Days</TabsTrigger>
        <TabsTrigger value="30">30 Days</TabsTrigger>
        <TabsTrigger value="90">90 Days</TabsTrigger>
      </TabsList>
    </Tabs>
  );
}
