import { InsightsOverview } from "../../types/insights";
import SkillsChart from "../charts/SkillsChart";
import TechStackChart from "../charts/TechStackChart";
import SeniorityChart from "../charts/SeniorityChart";

interface Props {
    data: InsightsOverview;
}

export default function DashboardGrid({data}: Props) {
    return (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <SkillsChart skills={data.top_skills} />
            <TechStackChart techStack={data.top_tech_stack} />
            <div className="lg:col-span-2">
                <SeniorityChart seniorityDistribution={data.seniority_distribution} />
            </div>
        </div>
    );
}