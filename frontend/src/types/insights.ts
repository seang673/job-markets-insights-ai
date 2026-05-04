#Defining the Types

export interface SkillCount {
  name: string;
  count: number;
}

export interface TechCount {
  name: string;
  count: number;
}

export interface SeniorityCount {
  level: string;
  count: number;
}

export interface InsightsOverview {
  total_jobs: number;
  top_skills: SkillCount[];
  top_tech_stack: TechCount[];
  seniority_distribution: SeniorityCount[];
  role: string;
}
