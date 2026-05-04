import { useEffect, useState } from "react";
import { fetchInsightsOverview } from "../api/insights";
import { InsightsOverview } from "../types/insights";
import DashboardGrid from "../components/layout/DashboardGrid";

export default function Dashboard() {
    const [data, setData] = useState<InsightsOverview | null>(null);
    const [loading, setLoading] = useState(true);
    
    useEffect(() => {
        fetchInsightsOverview().then((res) => {
            setData(res);
            setLoading(false);
        });
    }, []);

    if (loading) {
        return <div className="p-6">Loading insights...</div>;
    }
    if (!data){
        return <div className="p-6">No insights data available.</div>;
    }

    return (
        <div className="p-6">
            <h1 className="text-3xl font-bold mb-4">Job Market Insights For ({data.role}) position</h1>
            <p className="text-gray-600 mb-6">Total Job Postings: {data.total_jobs}</p>
            <DashboardGrid data={data} />
        </div>
    );
}