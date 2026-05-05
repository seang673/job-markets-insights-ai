import {useState} from "react";

interface Props {
    selectedRole: string;
    onRoleChange: (role: string) => void;
}

const PRESET_ROLES = [
    "Software Engineer",
    "Data Scientist",
    "Machine Learning Engineer",
    "Quality Assurance Engineer",
    "Backend Engineer",
    "Frontend Engineer",
    "DevOps Engineer",
    "Full Stack Engineer",
];

export default function RoleSelector({ selectedRole, onRoleChange }: Props) {
    const [customRole, setCustomRole] = useState("");

    return(
        <div className="mb-6 flex flex-col gap-4">
            <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Select Role</label>
                <select
                    value={selectedRole}
                    onChange={(e) => onRoleChange(e.target.value)}
                    className="border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                    <option value="">-- All Roles --</option>
                    {PRESET_ROLES.map((role) => (
                        <option key={role} value={role}>
                            {role}
                        </option>
                    ))}
                </select>
            </div>
        </div>
    );
}
