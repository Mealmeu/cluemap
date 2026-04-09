export type Role = "student" | "teacher";

export interface User {
  id: number;
  email: string;
  role: Role;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface MessageResponse {
  message: string;
}

export interface ProblemListItem {
  id: number;
  title: string;
  description: string;
  concept_tags: string[];
  created_at: string;
}

export interface TestCase {
  id: number;
  input_data: Record<string, unknown>;
  expected_output: unknown | null;
  is_hidden: boolean;
  order_index: number;
}

export interface Problem {
  id: number;
  title: string;
  description: string;
  starter_code: string;
  reference_solution_summary: string;
  concept_tags: string[];
  misconception_taxonomy: string[];
  created_by: number | null;
  created_at: string;
  updated_at: string;
  test_cases: TestCase[];
}

export interface AnalysisResult {
  id: number;
  submission_id: number;
  category: string;
  confidence: number;
  student_state: string;
  why_wrong: string;
  evidence: string[];
  hint_level_1: string;
  hint_level_2: string;
  review_topics: string[];
  teacher_summary: string;
  analysis_version: string;
  created_at: string;
}

export interface Submission {
  id: number;
  user_id: number;
  problem_id: number;
  code: string;
  run_status: string;
  passed_count: number;
  total_count: number;
  score: number;
  stdout_excerpt: string | null;
  stderr_excerpt: string | null;
  failure_summary: Array<Record<string, unknown>>;
  execution_time_ms: number | null;
  improved: boolean | null;
  created_at: string;
  updated_at: string;
  analysis_result: AnalysisResult | null;
}

export interface SubmissionListResponse {
  items: Submission[];
}

export interface CategoryCount {
  category: string;
  count: number;
}

export interface RepeatedFailureStudent {
  student_id: number;
  email: string;
  failure_count: number;
  latest_submission_at: string | null;
}

export interface TeacherProblemStats {
  problem_id: number;
  total_submissions: number;
  passed_submissions: number;
  failed_submissions: number;
  average_score: number;
  misconception_distribution: CategoryCount[];
  repeated_failures: RepeatedFailureStudent[];
}

export interface TeacherProblemInsights {
  problem_id: number;
  summary: string;
  focus_points: string[];
  review_topics: string[];
  teacher_summaries: string[];
}

export interface StudentHistoryItem {
  submission_id: number;
  problem_id: number;
  problem_title: string;
  run_status: string;
  score: number;
  category: string | null;
  created_at: string;
}

export interface StudentHistoryResponse {
  student_id: number;
  items: StudentHistoryItem[];
}

export interface ProblemPayload {
  title: string;
  description: string;
  starter_code: string;
  reference_solution_summary: string;
  concept_tags: string[];
  misconception_taxonomy: string[];
  test_cases: Array<{
    input_data: Record<string, unknown>;
    expected_output: unknown;
    is_hidden: boolean;
    order_index: number;
  }>;
}
