import { z } from "zod";

export const problemSchema = z.object({
  title: z.string().min(1, "제목을 입력하세요."),
  description: z.string().min(1, "문제 설명을 입력하세요."),
  starter_code: z.string().min(1, "starter code를 입력하세요."),
  reference_solution_summary: z.string().min(1, "정답 요약을 입력하세요."),
  concept_tags: z.string().min(1, "개념 태그를 입력하세요."),
  misconception_taxonomy: z.string().min(1, "오개념 taxonomy를 입력하세요."),
  visible_input: z.string().min(1, "공개 테스트 입력을 입력하세요."),
  visible_expected: z.string().min(1, "공개 테스트 정답을 입력하세요."),
  hidden_input: z.string().min(1, "숨김 테스트 입력을 입력하세요."),
  hidden_expected: z.string().min(1, "숨김 테스트 정답을 입력하세요.")
});

export type ProblemFormValues = z.infer<typeof problemSchema>;
