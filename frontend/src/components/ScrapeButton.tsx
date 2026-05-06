import {useState} from "react";
import {scrapeJobs} from "../api/scrape";

interface Props {
    role: string;
    onScrapeComplete: () => void;
}

export default function ScrapeButton({ role, onScrapeComplete }: Props) {
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState("");

    async function handleScrape() {
        setLoading(true);
        setMessage("");

        try {
            await scrapeJobs(role);
            setMessage("Scraping has started, please wait a moment!");
            onScrapeComplete();
        } catch (error) {
            setMessage("Failed to initiate scraping.");
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="mb-4">
            <button
                onClick={handleScrape}
                disabled={loading}
                className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
            >
                {loading ? "Scraping..." : "Scrape Jobs"}
            </button>
            {message && <p className="text-sm text-gray-600 mt-2">{message}</p>}
        </div>
    )
};