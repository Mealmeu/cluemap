import { apiClient } from "./api/client";
import type { Problem, ProblemListItem, ProblemPayload } from "../types/api";

export const getProblems = async () => {
  const { data } = await apiClient.get<ProblemListItem[]>("/api/problems");
  return data;
};

export const getProblem = async (problemId: number) => {
  const { data } = await apiClient.get<Problem>(`/api/problems/${problemId}`);
  return data;
};

export const createProblem = async (payload: ProblemPayload) => {
  const { data } = await apiClient.post<Problem>("/api/problems", payload);
  return data;
};

export const updateProblem = async (problemId: number, payload: Partial<ProblemPayload>) => {
  const { data } = await apiClient.put<Problem>(`/api/problems/${problemId}`, payload);
  return data;
};

export const deleteProblem = async (problemId: number) => {
  const { data } = await apiClient.delete<{ message: string }>(`/api/problems/${problemId}`);
  return data;
};
