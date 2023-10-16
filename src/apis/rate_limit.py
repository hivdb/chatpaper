from .embedding import get_token_length
from ..preset import RATE_LIMIT_PATH
from ..preset import MODEL_RATE_LIMITS
from ..file_format import load_json
from ..file_format import dump_json
from datetime import datetime
from src.logs import logger


class RateLimit:

    def __init__(self, file_path=RATE_LIMIT_PATH):
        self.file_path = file_path

        prev_info = {}
        if self.file_path.exists():
            prev_info = load_json(self.file_path)

        self.last_time = datetime.fromisoformat(
            prev_info.get('last_time', datetime.now().isoformat()))
        self.rpm_count = prev_info.get('rpm_count', 0)
        self.tpm_count = prev_info.get('tpm_count', 0)

    def check_hit_limit(self, text, model):
        num_token = get_token_length(text, model)
        now = datetime.now()
        seconds = (now - self.last_time).seconds
        if (seconds > 60):
            self.rpm_count = 1
            self.tpm_count = num_token
            self.last_time = datetime.now()
            return False

        self.rpm_count += 1
        self.tpm_count += num_token

        return self._check_hit_limit(model)

    def chech_hit_context_length(self, text, model):
        num_token = get_token_length(text, model)
        model_limit = MODEL_RATE_LIMITS.get(model)
        if not model_limit:
            raise Exception(f"model {model} not found")

        max_tokens = model_limit['MAX_TOKENS']
        if num_token > max_tokens:
            logger.debug(
                f'Error, Prompt exceeded the context length: {num_token}')
            return True

        return False

    def _check_hit_limit(self, model):
        model_limit = MODEL_RATE_LIMITS.get(model)
        if not model_limit:
            raise Exception(f"model {model} not found")

        rpm = model_limit['RPM']
        if self.rpm_count >= rpm:
            return True

        tpm = model_limit['TPM']
        if self.tpm_count >= tpm:
            return True

        return False

    def dump_json(self):
        dump_json(self.file_path, {
            'last_time': self.last_time.isoformat(),
            'rpm_count': self.rpm_count,
            'tpm_count': self.tpm_count
        })
