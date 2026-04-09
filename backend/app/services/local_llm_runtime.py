from __future__ import annotations

import logging
import shutil
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional

from app.core.config import Settings, get_settings

logger = logging.getLogger(__name__)


class LocalLLMRuntime:
    _model = None
    _model_path: Optional[str] = None
    _lock = Lock()

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()

    def ensure_model_path(self) -> Path:
        model_dir = Path(self.settings.local_llm_model_dir)
        model_dir.mkdir(parents=True, exist_ok=True)
        model_path = model_dir / self.settings.local_llm_model_file
        if model_path.exists():
            logger.info("Using local LLM model file: %s", model_path)
            return model_path
        if not self.settings.local_llm_auto_download:
            raise FileNotFoundError(f"Local LLM model file not found: {model_path}")
        download_repo = self.settings.local_llm_download_repo or self.settings.local_llm_model_repo
        download_file = self.settings.local_llm_download_file or self.settings.local_llm_model_file
        if not download_repo or not download_file:
            raise FileNotFoundError("Local LLM download settings are empty.")
        try:
            from huggingface_hub import hf_hub_download
        except ImportError as exc:
            raise RuntimeError("huggingface_hub is not installed.") from exc

        downloaded = hf_hub_download(
            repo_id=download_repo,
            filename=download_file,
            local_dir=str(model_dir),
            local_dir_use_symlinks=False,
        )
        downloaded_path = Path(downloaded)
        if downloaded_path.name != model_path.name:
            shutil.copyfile(downloaded_path, model_path)
            logger.info("Copied local LLM model from %s to %s", downloaded_path, model_path)
            return model_path
        logger.info("Downloaded local LLM model to: %s", downloaded)
        return downloaded_path

    def get_model(self):
        model_path = self.ensure_model_path()
        with self._lock:
            if self.__class__._model is not None and self.__class__._model_path == str(model_path):
                return self.__class__._model
            try:
                from llama_cpp import Llama
            except ImportError as exc:
                raise RuntimeError("llama-cpp-python is not installed.") from exc

            self.__class__._model = Llama(
                model_path=str(model_path),
                chat_format=self.settings.local_llm_chat_format,
                n_ctx=self.settings.local_llm_n_ctx,
                n_threads=self.settings.local_llm_n_threads,
                n_gpu_layers=self.settings.local_llm_n_gpu_layers,
                seed=self.settings.local_llm_seed,
                verbose=False,
            )
            self.__class__._model_path = str(model_path)
            logger.info(
                "Loaded local LLM model %s from %s with ctx=%s threads=%s",
                self.settings.local_llm_profile_name,
                model_path,
                self.settings.local_llm_n_ctx,
                self.settings.local_llm_n_threads,
            )
            return self.__class__._model

    def create_chat_completion(self, messages: List[Dict[str, str]], schema: Dict[str, Any]) -> Dict[str, Any]:
        model = self.get_model()
        response = model.create_chat_completion(
            messages=messages,
            max_tokens=self.settings.local_llm_max_tokens,
            temperature=self.settings.local_llm_temperature,
            top_p=self.settings.local_llm_top_p,
            top_k=self.settings.local_llm_top_k,
            repeat_penalty=self.settings.local_llm_repeat_penalty,
            response_format={
                "type": "json_object",
                "schema": schema,
            },
        )
        logger.info("Local LLM completion generated successfully with profile=%s", self.settings.local_llm_profile_name)
        return response
