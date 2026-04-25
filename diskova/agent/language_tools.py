"""
Language Tools - Translation & Multi-language Support
==================================================
Translation, language detection, and multi-language text processing.
"""

import json
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime


# Common translations dictionary (offline fallback)
TRANSLATIONS = {
    "hello": {"es": "hola", "fr": "bonjour", "de": "hallo", "ja": "こんにちは", "zh": "你好", "ko": "안녕하세요", "pt": "olá", "it": "ciao", "ru": "привет", "ar": "مرحبا"},
    "goodbye": {"es": "adiós", "fr": "au revoir", "de": "auf wiedersehen", "ja": "さようなら", "zh": "再见", "ko": "안녕히 가세요", "pt": "adeus", "it": "arrivederci", "ru": "до свидания", "ar": "مع السلامة"},
    "thank you": {"es": "gracias", "fr": "merci", "de": "danke", "ja": "ありがとう", "zh": "谢谢", "ko": "감사합니다", "pt": "obrigado", "it": "grazie", "ru": "спасибо", "ar": "شكرا"},
    "yes": {"es": "sí", "fr": "oui", "de": "ja", "ja": "はい", "zh": "是", "ko": "네", "pt": "sim", "it": "sì", "ru": "да", "ar": "نعم"},
    "no": {"es": "no", "fr": "non", "de": "nein", "ja": "いいえ", "zh": "不", "ko": "아니요", "pt": "não", "it": "no", "ru": "нет", "ar": "لا"},
    "please": {"es": "por favor", "fr": "s'il vous plaît", "de": "bitte", "ja": "お願いします", "zh": "请", "ko": "제발", "pt": "por favor", "it": "per favore", "ru": "пожалуйста", "ar": "من فضلك"},
    "sorry": {"es": "lo siento", "fr": "désolé", "ja": "ごめんなさい", "zh": "对不起", "ko": "죄송합니다", "pt": "desculpe", "it": "scusa", "ru": "извините", "ar": "آسف"},
    "help": {"es": "ayuda", "fr": "aide", "de": "hilfe", "ja": "助けて", "zh": "帮助", "ko": "도와주세요", "pt": "ajuda", "it": "aiuto", "ru": "помощь", "ar": "مساعدة"},
    "welcome": {"es": "bienvenido", "fr": "bienvenue", "de": "willkommen", "ja": "ようこそ", "zh": "欢迎", "ko": "환영합니다", "pt": "bem-vindo", "it": "benvenuto", "ru": "добро пожаловать", "ar": "أهلا وسهلا"},
    "good morning": {"es": "buenos días", "fr": "bonjour", "de": "guten morgen", "ja": "おはようございます", "zh": "早上好", "ko": "좋은 아침", "pt": "bom dia", "it": "buongiorno", "ru": "доброе утро", "ar": "صباح الخير"},
    "good night": {"es": "buenas noches", "fr": "bonne nuit", "de": "gute nacht", "ja": "おやすみなさい", "zh": "晚安", "ko": "좋은 밤", "pt": "boa noite", "it": "buonanotte", "ru": "спокойной ночи", "ar": "تصبح على خير"},
    "how are you": {"es": "¿cómo estás?", "fr": "comment allez-vous?", "de": "wie geht es dir?", "ja": "お元気ですか?", "zh": "你好吗?", "ko": "어떻게 지내세요?", "pt": "como você está?", "it": "come stai?", "ru": "как дела?", "ar": "كيف حالك؟"},
    "i love you": {"es": "te quiero", "fr": "je t'aime", "ja": "愛してる", "zh": "我爱你", "ko": "사랑해요", "pt": "eu te amo", "it": "ti amo", "ru": "я тебя люблю", "ar": "أحبك"},
}

# Language codes and names
LANGUAGES = {
    "en": "English", "es": "Spanish", "fr": "French", "de": "German",
    "it": "Italian", "pt": "Portuguese", "ru": "Russian", "ar": "Arabic",
    "zh": "Chinese", "ja": "Japanese", "ko": "Korean", "hi": "Hindi",
    "th": "Thai", "vi": "Vietnamese", "nl": "Dutch", "pl": "Polish",
    "tr": "Turkish", "sv": "Swedish", "hi": "Hindi", "id": "Indonesian",
    "ms": "Malay", "cs": "Czech", "ro": "Romanian", "hu": "Hungarian",
}


class LanguageDetector:
    """Detect language of text."""
    
    def __init__(self):
        self.common_words = {
            "en": ["the", "is", "are", "and", "to", "in", "it", "you", "that", "was"],
            "es": ["el", "la", "de", "que", "y", "en", "un", "ser", "have", "from"],
            "fr": ["le", "la", "de", "et", "un", "être", "avoir", "que", "dans", "qui"],
            "de": ["der", "die", "das", "und", "ist", "von", "mit", "sich", "auf", "für"],
            "zh": ["的", "是", "在", "不", "了", "和", "有", "我", "这", "个"],
            "ja": ["の", "は", "が", "を", "に", "と", "で", "も", "な", "から"],
            "ko": ["은", "는", "이", "가", "을", "를", "에", "의", "로", "과"],
            "ru": ["и", "в", "не", "на", "я", "что", "он", "с", "это", "а"],
            "ar": ["في", "من", "على", "that", "هذا", "أن", "ما", "في", "هناك"],
        }
    
    def detect(self, text: str) -> str:
        """Detect language code."""
        if not text:
            return "en"
        
        text_lower = text.lower()
        scores = {}
        
        for lang, words in self.common_words.items():
            count = sum(1 for word in words if word in text_lower)
            if count > 0:
                scores[lang] = count
        
        if scores:
            return max(scores, key=scores.get)
        
        # Check for non-ASCII
        if re.search(r'[\u4e00-\u9fff]', text):
            return "zh"
        if re.search(r'[\u3040-\u309f\u30a0-\u30ff]', text):
            return "ja"
        if re.search(r'[\uac00-\ud7af]', text):
            return "ko"
        if re.search(r'[\u0600-\u06ff]', text):
            return "ar"
        if re.search(r'[\u0400-\u04ff]', text):
            return "ru"
        
        return "en"
    
    def get_name(self, code: str) -> str:
        """Get language name from code."""
        return LANGUAGES.get(code, code.upper())


class Translator:
    """Translate text between languages."""
    
    def __init__(self):
        self.detector = LanguageDetector()
        self.cache = {}
    
    def translate(self, text: str, target: str = "en", source: str = None) -> str:
        """Translate text."""
        if not text:
            return ""
        
        # Auto-detect source
        if source is None:
            source = self.detector.detect(text)
        
        # Same language
        if source == target:
            return text
        
        # Check cache
        cache_key = f"{text}:{source}:{target}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Try online translation
        result = self._translate_online(text, source, target)
        if result:
            self.cache[cache_key] = result
            return result
        
        # Fallback to common translations
        result = self._translate_offline(text, source, target)
        
        self.cache[cache_key] = result
        return result
    
    def _translate_online(self, text: str, source: str, target: str) -> str:
        """Try online translation API."""
        try:
            import requests
            
            # Use LibreTranslate (free) or MyMemory
            if len(text) < 100:
                url = "https://api.mymemory.translated.net/get"
                params = {"q": text, "langpair": f"{source}|{target}"}
                response = requests.get(url, params=params, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("responseStatus") == 200:
                        return data.get("responseData", {}).get("translatedText", "")
        except:
            pass
        
        return ""
    
    def _translate_offline(self, text: str, source: str, target: str) -> str:
        """Offline dictionary fallback."""
        text_lower = text.lower().strip()
        
        # Direct match
        if text_lower in TRANSLATIONS:
            if target in TRANSLATIONS[text_lower]:
                return TRANSLATIONS[text_lower][target]
        
        # Check if it's a common phrase we know
        for original, translations in TRANSLATIONS.items():
            if text_lower in original or original in text_lower:
                if target in translations:
                    return translations[target]
        
        return f"[{target.upper()}] {text}"


class MultilingualProcessor:
    """Process text in multiple languages."""
    
    def __init__(self):
        self.translator = Translator()
        self.detector = LanguageDetector()
    
    def process(self, text: str, target_lang: str = None) -> Dict:
        """Process text with language detection and translation."""
        source_lang = self.detector.detect(text)
        
        result = {
            "original": text,
            "detected_lang": source_lang,
            "detected_name": self.detector.get_name(source_lang),
            "target_lang": target_lang or source_lang,
            "translated": text,
        }
        
        if target_lang and target_lang != source_lang:
            result["translated"] = self.translator.translate(text, target_lang, source_lang)
        
        return result
    
    def detect_language(self, text: str) -> str:
        """Detect and return language info."""
        code = self.detector.detect(text)
        return f"{code.upper()} ({self.detector.get_name(code)})"


# Global instance
_translator = None
_detector = None


def get_translator() -> Translator:
    """Get translator instance."""
    global _translator
    if _translator is None:
        _translator = Translator()
    return _translator


def get_detector() -> LanguageDetector:
    """Get detector instance."""
    global _detector
    if _detector is None:
        _detector = LanguageDetector()
    return _detector


# Easy functions
def detect_language(text: str) -> str:
    """Detect language of text."""
    return get_detector().detect(text)


def translate(text: str, target: str = "en", source: str = None) -> str:
    """Translate text."""
    return get_translator().translate(text, target, source)


def detect_and_translate(text: str, target: str = "en") -> Dict:
    """Detect language and translate."""
    processor = MultilingualProcessor()
    return processor.process(text, target)


def supported_languages() -> List[str]:
    """List supported languages."""
    return list(LANGUAGES.items())


if __name__ == "__main__":
    print("Language Tools")
    
    # Test detection
    detector = get_detector()
    print(f"Hello -> {detector.detect('Hello')}")
    print(f"こんにちは -> {detector.detect('こんにちは')}")
    print(f"你好 -> {detector.detect('你好')}")
    
    # Test translation
    translator = get_translator()
    print(f"Hola (es->en): {translator.translate('Hola', 'en', 'es')}")
    print(f"Thank you (en->ja): {translator.translate('thank you', 'ja', 'en')}")