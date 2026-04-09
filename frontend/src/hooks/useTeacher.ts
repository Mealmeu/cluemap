import { useQuery } from "@tanstack/react-query";

import { getStudentHistory, getTeacherProblemInsights, getTeacherProblemStats } from "../services/teacher";

export const useTeacherProblemStatsQuery = (problemId: number | null) =>
  useQuery({
    queryKey: ["teacher", "stats", problemId],
    queryFn: () => getTeacherProblemStats(problemId as number),
    enabled: Boolean(problemId)
  });

export const useTeacherProblemInsightsQuery = (problemId: number | null) =>
  useQuery({
    queryKey: ["teacher", "insights", problemId],
    queryFn: () => getTeacherProblemInsights(problemId as number),
    enabled: Boolean(problemId)
  });

export const useStudentHistoryQuery = (studentId: number | null) =>
  useQuery({
    queryKey: ["teacher", "student-history", studentId],
    queryFn: () => getStudentHistory(studentId as number),
    enabled: Boolean(studentId)
  });
