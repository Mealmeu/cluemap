import { apiClient } from "./api/client";
import type { StudentHistoryResponse, TeacherProblemInsights, TeacherProblemStats } from "../types/api";

export const getTeacherProblemStats = async (problemId: number) => {
  const { data } = await apiClient.get<TeacherProblemStats>(`/api/teacher/problems/${problemId}/stats`);
  return data;
};

export const getTeacherProblemInsights = async (problemId: number) => {
  const { data } = await apiClient.get<TeacherProblemInsights>(`/api/teacher/problems/${problemId}/insights`);
  return data;
};

export const getStudentHistory = async (studentId: number) => {
  const { data } = await apiClient.get<StudentHistoryResponse>(`/api/teacher/students/${studentId}/history`);
  return data;
};
