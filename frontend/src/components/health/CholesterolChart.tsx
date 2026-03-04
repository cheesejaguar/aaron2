import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import type { CholesterolLog } from "@/types";

interface CholesterolChartProps {
  data: CholesterolLog[];
}

export function CholesterolChart({ data }: CholesterolChartProps) {
  const chartData = [...data]
    .reverse()
    .map((log) => ({
      date: new Date(log.measured_at).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
      }),
      Total: log.total_mg_dl,
      LDL: log.ldl ?? 0,
      HDL: log.hdl ?? 0,
      Triglycerides: log.triglycerides ?? 0,
    }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
        <XAxis dataKey="date" stroke="hsl(var(--muted-foreground))" fontSize={12} />
        <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
        <Tooltip
          contentStyle={{
            backgroundColor: "hsl(var(--card))",
            border: "1px solid hsl(var(--border))",
            borderRadius: "8px",
          }}
        />
        <Legend />
        <Bar dataKey="Total" fill="hsl(var(--primary))" />
        <Bar dataKey="LDL" fill="#ef4444" />
        <Bar dataKey="HDL" fill="#22c55e" />
        <Bar dataKey="Triglycerides" fill="#f59e0b" />
      </BarChart>
    </ResponsiveContainer>
  );
}
