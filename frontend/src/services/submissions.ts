import { apiClient } from "./api/client";
import type { AnalysisResult, Submission, SubmissionListResponse } from "../types/api";

export interface SubmissionPayload {
  problem_id: number;
  code: string;
}

export const createSubmission = async (payload: SubmissionPayload) => {
  const { data } = await apiClient.post<Submission>("/api/submissions", payload);
  return data;
};

export const getSubmission = async (submissionId: number) => {
  const { data } = await apiClient.get<Submission>(`/api/submissions/${submissionId}`);
  return data;
};

export const getSubmissionAnalysis = async (submissionId: number) => {
  const { data } = await apiClient.get<AnalysisResult>(`/api/submissions/${submissionId}/analysis`);
  return data;
};

export const getMyProblemSubmissions = async (problemId: number) => {
  const { data } = await apiClient.get<SubmissionListResponse>(`/api/problems/${problemId}/submissions/me`);
  return data.items;
};
