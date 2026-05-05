import { useEffect, useState } from "react";
import { fetchInsightsOverview } from "../api/insights";
import { InsightsOverview } from "../types/insights";
import DashboardGrid from "../components/layout/DashboardGrid";
import RoleSelector from "../components/RoleSelector";
import ScrapeButton from "../components/ScrapeButton";

export default function Dashboard() {
    const [data, setData] = useState<InsightsOverview | null>(null);
    const [loading, setLoading] = useState(true);
    const [selectedRole, setSelectedRole] = useState("Software Engineer");

    useEffect(() => {
        fetchInsightsOverview(selectedRole).then((res) => {
            setData(res);
            setLoading(false);
        });
    }, [selectedRole]);


    return (
        <div className="p-6">
            <h1 className="text-3xl font-bold mb-4">Job Market Insights</h1>
            <RoleSelector selectedRole={selectedRole} onRoleChange={setSelectedRole} />

            <ScrapeButton role={selectedRole} onScrapeComplete={() => {
                //refresh insights after scraping begins
                fetchInsightsOverview(selectedRole).then((res) => {
                    setData(res);
                });
            }} />
            {loading && <div>Loading insights...</div>}
            {!loading && data && (
                <>
                <p className="text-gray-600 mb-6">
                    Total Jobs: {data.total_jobs} 
                    <span className="ml-2 text-indigo-600 font-medium">
                    ({data.role})
                    </span>
                </p>
                    <DashboardGrid data={data} />
                </>
            )}
        </div>
    );
}