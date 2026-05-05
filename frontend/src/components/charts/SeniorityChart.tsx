import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";
import { SeniorityCount } from "../../types/insights";

interface Props {
  seniority: SeniorityCount[];
}

const COLORS = ["#6366F1", "#10B981", "#F59E0B", "#EF4444", "#3B82F6"];

export default function SeniorityChart({ seniority }: Props) {
  return (
    <div className="bg-white p-4 rounded-lg shadow">
      <h2 className="text-xl font-semibold mb-4">Seniority Distribution</h2>

      <ResponsiveContainer width="100%" height={350}>
        <PieChart>
          <Pie
            data={seniority}
            dataKey="count"
            nameKey="level"
            cx="50%"
            cy="50%"
            innerRadius={70}
            outerRadius={120}
            paddingAngle={3}
          >
            {seniority.map((_, index) => (
              <Cell key={index} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
