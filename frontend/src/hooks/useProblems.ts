import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { createProblem, deleteProblem, getProblem, getProblems, updateProblem } from "../services/problems";
import type { ProblemPayload } from "../types/api";

export const problemKeys = {
  all: ["problems"] as const,
  detail: (problemId: number) => ["problems", problemId] as const
};

export const useProblemsQuery = () =>
  useQuery({
    queryKey: problemKeys.all,
    queryFn: getProblems
  });

export const useProblemQuery = (problemId: number, enabled = true) =>
  useQuery({
    queryKey: problemKeys.detail(problemId),
    queryFn: () => getProblem(problemId),
    enabled
  });

export const useProblemMutations = () => {
  const queryClient = useQueryClient();

  const createMutation = useMutation({
    mutationFn: createProblem,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: problemKeys.all });
    }
  });

  const updateMutation = useMutation({
    mutationFn: ({ problemId, payload }: { problemId: number; payload: Partial<ProblemPayload> }) =>
      updateProblem(problemId, payload),
    onSuccess: async (problem) => {
      await queryClient.invalidateQueries({ queryKey: problemKeys.all });
      await queryClient.invalidateQueries({ queryKey: problemKeys.detail(problem.id) });
    }
  });

  const deleteMutation = useMutation({
    mutationFn: deleteProblem,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: problemKeys.all });
    }
  });

  return {
    createMutation,
    updateMutation,
    deleteMutation
  };
};
