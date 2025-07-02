import json
import os
from contextlib import contextmanager
from typing import Dict, Generator, Optional

from aiogram.utils.i18n import I18n


class TxtI18n(I18n):
    """Load translations from JSON .txt files."""

    def find_locales(self) -> Dict[str, object]:
        translations: Dict[str, object] = {}
        for name in os.listdir(self.path):
            locale_dir = os.path.join(self.path, name)
            if not os.path.isdir(locale_dir):
                continue
            txt_path = os.path.join(locale_dir, "LC_MESSAGES", self.domain + ".txt")
            if os.path.exists(txt_path):
                translations[name] = self._load_txt(txt_path)
        return translations

    @staticmethod
    def _load_txt(path: str) -> object:
        with open(path, "r", encoding="utf-8") as f:
            mapping = json.load(f)

        class Translator:
            def gettext(self, singular: str) -> str:
                return mapping.get(singular, singular)

            def ngettext(self, singular: str, plural: str, n: int) -> str:
                key = singular if n == 1 else plural
                return mapping.get(key, key)

        return Translator()
