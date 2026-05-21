import { InsightsOverview } from "../../types/insights";
import SkillsChart from "../charts/SkillsChart";
import TechStackChart from "../charts/TechStackChart";
import SeniorityChart from "../charts/SeniorityChart";

interface Props {
    data: InsightsOverview;
}

export default function DashboardGrid({ data }: Props) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

      {/* Skills */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5 min-h-[350px]">
        <SkillsChart skills={data.top_skills} />
      </div>

      {/* Tech Stack */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5 min-h-[350px]">
        <TechStackChart tech={data.top_tech_stack} />
      </div>

      {/* Seniority */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5 min-h-[350px] md:col-span-3">
        <SeniorityChart seniority={data.seniority_distribution} />
      </div>

    </div>
  );
}

