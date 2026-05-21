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
        setLoading(true);
        fetchInsightsOverview(selectedRole).then((res) => {
            setData(res);
        })
        .catch((error) => {
            console.error("Failed to load insights:", error);
        })
        .finally(() => {
            setLoading(false);
        });
    }, [selectedRole]);


    return (
    <div className="min-h-screen bg-gray-50 p-6 space-y-6">

        {/* Header bar */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <h1 className="text-3xl font-bold text-gray-900">Job Market Insights</h1>
            <div className="flex items-center gap-3">
                <RoleSelector selectedRole={selectedRole} onRoleChange={setSelectedRole} />
                <ScrapeButton
                    role={selectedRole}
                    onScrapeComplete={() => {
                        fetchInsightsOverview(selectedRole).then((res) => setData(res));
                    }}
                />
            </div>
        </div>

        {/* Stat strip */}
        {!loading && data && (
            <div className="flex items-center gap-2 text-sm">
                <span className="text-gray-500">Total jobs:</span>
                <span className="font-semibold text-gray-800">{data.total_jobs}</span>
                <span className="text-gray-300">|</span>
                <span className="text-indigo-600 font-medium">{data.role}</span>
            </div>
        )}

        {/* Loading */}
        {loading && (
            <p className="text-gray-400 text-sm animate-pulse">
                Loading insights for {selectedRole}…
            </p>
        )}

        {/* Grid */}
        {!loading && data && <DashboardGrid data={data} />}

    </div>
    );
}