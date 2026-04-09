import Editor from "@monaco-editor/react";

interface CodeEditorPanelProps {
  code: string;
  isSubmitting?: boolean;
  onChange: (value: string) => void;
  onSubmit: () => void;
}

export const CodeEditorPanel = ({ code, isSubmitting, onChange, onSubmit }: CodeEditorPanelProps) => {
  return (
    <section className="card overflow-hidden">
      <div className="flex items-center justify-between border-b border-slate-200 px-5 py-4">
        <div>
          <h2 className="text-lg font-semibold text-slate-900">코드 제출</h2>
          <p className="text-sm text-slate-600">Monaco Editor에서 바로 수정하고 제출할 수 있습니다.</p>
        </div>
        <button className="button-primary" disabled={isSubmitting} onClick={onSubmit} type="button">
          {isSubmitting ? "분석 중..." : "코드 제출"}
        </button>
      </div>
      <Editor
        defaultLanguage="python"
        height="520px"
        language="python"
        onChange={(value) => onChange(value ?? "")}
        options={{
          fontSize: 14,
          minimap: { enabled: false },
          lineNumbersMinChars: 3,
          automaticLayout: true,
          scrollBeyondLastLine: false
        }}
        theme="vs-light"
        value={code}
      />
    </section>
  );
};
