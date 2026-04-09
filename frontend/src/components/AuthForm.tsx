import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import { loginSchema, registerSchema, type LoginFormValues, type RegisterFormValues } from "../schemas/auth";

interface AuthFormProps {
  mode: "login" | "register";
  isPending?: boolean;
  errorMessage?: string;
  onSubmit: (values: LoginFormValues | RegisterFormValues) => void;
}

export const AuthForm = ({ mode, isPending, errorMessage, onSubmit }: AuthFormProps) => {
  const isRegister = mode === "register";
  const {
    register,
    handleSubmit,
    formState: { errors }
  } = useForm<LoginFormValues | RegisterFormValues>({
    resolver: zodResolver(isRegister ? registerSchema : loginSchema),
    defaultValues: isRegister ? { role: "student" } : undefined
  });

  return (
    <form className="card space-y-5 p-8" onSubmit={handleSubmit(onSubmit)}>
      <div className="space-y-2">
        <h1 className="text-2xl font-bold text-slate-900">{isRegister ? "ClueMap 회원가입" : "ClueMap 로그인"}</h1>
        <p className="text-sm text-slate-600">
          {isRegister ? "학생과 교사 역할을 선택해 계정을 생성하세요." : "학습 복구 흐름을 이어서 진행하세요."}
        </p>
      </div>

      <div>
        <label className="label-text" htmlFor="email">
          이메일
        </label>
        <input className="input-base" id="email" type="email" {...register("email")} />
        {errors.email ? <p className="mt-2 text-sm text-red-600">{errors.email.message}</p> : null}
      </div>

      <div>
        <label className="label-text" htmlFor="password">
          비밀번호
        </label>
        <input className="input-base" id="password" type="password" {...register("password")} />
        {errors.password ? <p className="mt-2 text-sm text-red-600">{errors.password.message}</p> : null}
      </div>

      {isRegister ? (
        <div>
          <label className="label-text" htmlFor="role">
            역할
          </label>
          <select className="input-base" id="role" {...register("role")}>
            <option value="student">student</option>
            <option value="teacher">teacher</option>
          </select>
          {"role" in errors && errors.role ? <p className="mt-2 text-sm text-red-600">{errors.role.message}</p> : null}
        </div>
      ) : null}

      {errorMessage ? <div className="rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700">{errorMessage}</div> : null}

      <button className="button-primary w-full" disabled={isPending} type="submit">
        {isPending ? "처리 중..." : isRegister ? "회원가입" : "로그인"}
      </button>
    </form>
  );
};
