import { useEffect, useMemo, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { AxiosError } from "axios";

import { useProblemMutations, useProblemQuery, useProblemsQuery } from "../hooks/useProblems";
import { problemSchema, type ProblemFormValues } from "../schemas/problem";
import type { ProblemPayload } from "../types/api";

const defaultValues: ProblemFormValues = {
  title: "",
  description: "",
  starter_code: "def solve(value):\n    return value\n",
  reference_solution_summary: "",
  concept_tags: "",
  misconception_taxonomy: "",
  visible_input: "[]",
  visible_expected: "0",
  hidden_input: "[]",
  hidden_expected: "0"
};

const parseArgs = (value: string) => {
  const parsed = JSON.parse(value);
  return Array.isArray(parsed) ? parsed : [parsed];
};

const parseExpected = (value: string) => JSON.parse(value);

const toPayload = (values: ProblemFormValues): ProblemPayload => ({
  title: values.title,
  description: values.description,
  starter_code: values.starter_code,
  reference_solution_summary: values.reference_solution_summary,
  concept_tags: values.concept_tags.split(",").map((item) => item.trim()).filter(Boolean),
  misconception_taxonomy: values.misconception_taxonomy.split(",").map((item) => item.trim()).filter(Boolean),
  test_cases: [
    {
      input_data: { args: parseArgs(values.visible_input) },
      expected_output: parseExpected(values.visible_expected),
      is_hidden: false,
      order_index: 0
    },
    {
      input_data: { args: parseArgs(values.hidden_input) },
      expected_output: parseExpected(values.hidden_expected),
      is_hidden: true,
      order_index: 1
    }
  ]
});

export const TeacherProblemManagementPage = () => {
  const { data: problems } = useProblemsQuery();
  const [selectedProblemId, setSelectedProblemId] = useState<number | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const selectedProblem = useProblemQuery(selectedProblemId ?? 0, Boolean(selectedProblemId));
  const { createMutation, updateMutation, deleteMutation } = useProblemMutations();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors }
  } = useForm<ProblemFormValues>({
    resolver: zodResolver(problemSchema),
    defaultValues
  });

  useEffect(() => {
    if (!selectedProblem.data) {
      reset(defaultValues);
      return;
    }

    const visible = selectedProblem.data.test_cases.find((item) => !item.is_hidden);
    const hidden = selectedProblem.data.test_cases.find((item) => item.is_hidden);

    reset({
      title: selectedProblem.data.title,
      description: selectedProblem.data.description,
      starter_code: selectedProblem.data.starter_code,
      reference_solution_summary: selectedProblem.data.reference_solution_summary,
      concept_tags: selectedProblem.data.concept_tags.join(", "),
      misconception_taxonomy: selectedProblem.data.misconception_taxonomy.join(", "),
      visible_input: JSON.stringify(visible?.input_data.args ?? []),
      visible_expected: JSON.stringify(visible?.expected_output ?? 0),
      hidden_input: JSON.stringify(hidden?.input_data.args ?? []),
      hidden_expected: JSON.stringify(hidden?.expected_output ?? 0)
    });
  }, [reset, selectedProblem.data]);

  const activeErrorMessage = useMemo(() => {
    const mutationError =
      (createMutation.error as AxiosError<{ detail?: string }> | null)?.response?.data?.detail ??
      (updateMutation.error as AxiosError<{ detail?: string }> | null)?.response?.data?.detail ??
      (deleteMutation.error as AxiosError<{ detail?: string }> | null)?.response?.data?.detail;
    return formError ?? mutationError ?? null;
  }, [createMutation.error, deleteMutation.error, formError, updateMutation.error]);

  return (
    <main className="mx-auto max-w-7xl space-y-6 px-4 py-10">
      <section className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-sm font-semibold text-blue-700">Teacher Problems</p>
          <h1 className="mt-2 text-3xl font-bold text-slate-900">교사용 문제 관리</h1>
          <p className="mt-3 text-sm leading-6 text-slate-600">
            문제 생성, 수정, 삭제를 직접 API와 연결해 관리합니다.
          </p>
        </div>
        <button
          className="button-secondary"
          onClick={() => {
            setSelectedProblemId(null);
            setFormError(null);
            reset(defaultValues);
          }}
          type="button"
        >
          새 문제 작성
        </button>
      </section>

      <div className="grid gap-6 xl:grid-cols-[0.8fr_1.2fr]">
        <section className="card p-6">
          <h2 className="text-lg font-semibold text-slate-900">문제 목록</h2>
          <div className="mt-4 space-y-3">
            {problems?.length ? (
              problems.map((problem) => (
                <div className="rounded-2xl border border-slate-200 p-4" key={problem.id}>
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="font-medium text-slate-900">{problem.title}</p>
                      <p className="mt-1 text-sm text-slate-500">{problem.description}</p>
                    </div>
                    <button className="button-secondary" onClick={() => setSelectedProblemId(problem.id)} type="button">
                      수정
                    </button>
                  </div>
                </div>
              ))
            ) : (
              <div className="rounded-2xl bg-slate-50 p-4 text-sm text-slate-500">등록된 문제가 없습니다.</div>
            )}
          </div>
        </section>

        <section className="card p-6">
          <h2 className="text-lg font-semibold text-slate-900">{selectedProblemId ? "문제 수정" : "문제 생성"}</h2>
          <form
            className="mt-5 space-y-4"
            onSubmit={handleSubmit((values) => {
              setFormError(null);
              try {
                const payload = toPayload(values);
                if (selectedProblemId) {
                  updateMutation.mutate({ problemId: selectedProblemId, payload });
                } else {
                  createMutation.mutate(payload, {
                    onSuccess: () => {
                      reset(defaultValues);
                    }
                  });
                }
              } catch {
                setFormError("테스트 입력과 정답은 JSON 형식으로 입력해 주세요.");
              }
            })}
          >
            <div>
              <label className="label-text">제목</label>
              <input className="input-base" {...register("title")} />
              {errors.title ? <p className="mt-2 text-sm text-red-600">{errors.title.message}</p> : null}
            </div>

            <div>
              <label className="label-text">문제 설명</label>
              <textarea className="input-base min-h-28" {...register("description")} />
              {errors.description ? <p className="mt-2 text-sm text-red-600">{errors.description.message}</p> : null}
            </div>

            <div>
              <label className="label-text">Starter Code</label>
              <textarea className="input-base min-h-40 font-mono" {...register("starter_code")} />
            </div>

            <div>
              <label className="label-text">정답 요약</label>
              <textarea className="input-base min-h-24" {...register("reference_solution_summary")} />
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="label-text">concept_tags</label>
                <input className="input-base" {...register("concept_tags")} />
              </div>
              <div>
                <label className="label-text">misconception_taxonomy</label>
                <input className="input-base" {...register("misconception_taxonomy")} />
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="label-text">공개 테스트 args JSON</label>
                <textarea className="input-base min-h-24 font-mono" {...register("visible_input")} />
              </div>
              <div>
                <label className="label-text">공개 테스트 expected JSON</label>
                <textarea className="input-base min-h-24 font-mono" {...register("visible_expected")} />
              </div>
              <div>
                <label className="label-text">숨김 테스트 args JSON</label>
                <textarea className="input-base min-h-24 font-mono" {...register("hidden_input")} />
              </div>
              <div>
                <label className="label-text">숨김 테스트 expected JSON</label>
                <textarea className="input-base min-h-24 font-mono" {...register("hidden_expected")} />
              </div>
            </div>

            {activeErrorMessage ? <div className="rounded-2xl bg-red-50 px-4 py-3 text-sm text-red-700">{activeErrorMessage}</div> : null}

            <div className="flex flex-wrap gap-3">
              <button
                className="button-primary"
                disabled={createMutation.isPending || updateMutation.isPending}
                type="submit"
              >
                {selectedProblemId ? "문제 수정" : "문제 생성"}
              </button>
              {selectedProblemId ? (
                <button
                  className="button-secondary"
                  disabled={deleteMutation.isPending}
                  onClick={() => {
                    deleteMutation.mutate(selectedProblemId, {
                      onSuccess: () => {
                        setSelectedProblemId(null);
                        reset(defaultValues);
                      }
                    });
                  }}
                  type="button"
                >
                  삭제
                </button>
              ) : null}
            </div>
          </form>
        </section>
      </div>
    </main>
  );
};
