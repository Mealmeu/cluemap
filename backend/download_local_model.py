from app.services.local_llm_runtime import LocalLLMRuntime


def main() -> None:
    runtime = LocalLLMRuntime()
    path = runtime.ensure_model_path()
    print(path)


if __name__ == "__main__":
    main()
