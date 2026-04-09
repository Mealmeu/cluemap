import { z } from "zod";

export const loginSchema = z.object({
  email: z.string().email("올바른 이메일을 입력하세요."),
  password: z.string().min(8, "비밀번호는 8자 이상이어야 합니다.")
});

export const registerSchema = loginSchema.extend({
  role: z.enum(["student", "teacher"])
});

export type LoginFormValues = z.infer<typeof loginSchema>;
export type RegisterFormValues = z.infer<typeof registerSchema>;
