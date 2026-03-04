import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import type { BPLog } from "@/types";

interface BPChartProps {
  data: BPLog[];
}

export function BPChart({ data }: BPChartProps) {
  const chartData = [...data]
    .reverse()
    .map((d) => ({
      date: new Date(d.measured_at).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
      }),
      systolic: d.systolic,
      diastolic: d.diastolic,
      pulse: d.pulse,
    }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
        <XAxis
          dataKey="date"
          stroke="hsl(var(--muted-foreground))"
          fontSize={12}
        />
        <YAxis
          stroke="hsl(var(--muted-foreground))"
          fontSize={12}
          domain={[60, 200]}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: "hsl(var(--card))",
            border: "1px solid hsl(var(--border))",
            borderRadius: "8px",
          }}
        />
        {/* Normal BP reference lines */}
        <ReferenceLine
          y={120}
          stroke="hsl(var(--chart-2))"
          strokeDasharray="5 5"
          label={{ value: "120", position: "right", fontSize: 10 }}
        />
        <ReferenceLine
          y={80}
          stroke="hsl(var(--chart-2))"
          strokeDasharray="5 5"
          label={{ value: "80", position: "right", fontSize: 10 }}
        />
        {/* High BP threshold */}
        <ReferenceLine
          y={140}
          stroke="hsl(var(--destructive))"
          strokeDasharray="3 3"
        />
        <Line
          type="monotone"
          dataKey="systolic"
          stroke="hsl(var(--chart-1))"
          strokeWidth={2}
          dot={{ r: 3 }}
          name="Systolic"
        />
        <Line
          type="monotone"
          dataKey="diastolic"
          stroke="hsl(var(--chart-2))"
          strokeWidth={2}
          dot={{ r: 3 }}
          name="Diastolic"
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
