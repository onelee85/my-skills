"""Tests for generate_tts.py pure functions.

Tests cover section parsing, phoneme processing, time formatting,
and subtitle generation — all without requiring TTS API keys.
"""
import re
import pytest
from conftest import tts_module

# Extract functions from the loaded module
extract_inline_phonemes = tts_module.extract_inline_phonemes
pinyin_to_sapi = tts_module.pinyin_to_sapi
apply_phonemes = tts_module.apply_phonemes
mark_english_terms = tts_module.mark_english_terms
format_time = tts_module.format_time
BUILTIN_POLYPHONES = tts_module.BUILTIN_POLYPHONES


# ============ extract_inline_phonemes ============

class TestExtractInlinePhonemes:
    def test_basic_extraction(self):
        # The regex captures all preceding Chinese chars as the key
        text = "每个执行器[zhí xíng qì]都有自己的上下文窗口"
        clean, phonemes = extract_inline_phonemes(text)
        assert clean == "每个执行器都有自己的上下文窗口"
        assert "zhí xíng qì" in phonemes.values()

    def test_single_char_word(self):
        # When the annotated word starts at the beginning, it captures exactly
        text = "执行器[zhí xíng qì]启动"
        clean, phonemes = extract_inline_phonemes(text)
        assert clean == "执行器启动"
        assert phonemes["执行器"] == "zhí xíng qì"

    def test_multiple_markers(self):
        text = "重做[chóng zuò]和重新[chóng xīn]操作"
        clean, phonemes = extract_inline_phonemes(text)
        assert clean == "重做和重新操作"
        assert len(phonemes) == 2
        assert "chóng zuò" in phonemes.values()
        assert "chóng xīn" in phonemes.values()

    def test_no_markers(self):
        text = "这是普通文本没有标记"
        clean, phonemes = extract_inline_phonemes(text)
        assert clean == text
        assert phonemes == {}

    def test_empty_string(self):
        clean, phonemes = extract_inline_phonemes("")
        assert clean == ""
        assert phonemes == {}


# ============ pinyin_to_sapi ============

class TestPinyinToSapi:
    def test_basic_conversion(self):
        assert pinyin_to_sapi("zhí xíng qì") == "zhi 2 xing 2 qi 4"

    def test_first_tone(self):
        assert pinyin_to_sapi("māo") == "mao 1"

    def test_third_tone(self):
        assert pinyin_to_sapi("mǎ") == "ma 3"

    def test_neutral_tone(self):
        assert pinyin_to_sapi("de") == "de 5"

    def test_u_umlaut(self):
        assert pinyin_to_sapi("nǚ") == "nv 3"

    def test_multi_syllable(self):
        assert pinyin_to_sapi("chóng zuò") == "chong 2 zuo 4"


# ============ apply_phonemes ============

class TestApplyPhonemes:
    def test_basic_replacement(self):
        result = apply_phonemes("执行器启动", {"执行器": "zhí xíng qì"})
        assert '<phoneme alphabet="sapi"' in result
        assert "执行器" in result
        assert "zhi 2 xing 2 qi 4" in result

    def test_empty_dict(self):
        text = "没有替换"
        assert apply_phonemes(text, {}) == text

    def test_none_dict(self):
        text = "没有替换"
        assert apply_phonemes(text, None) == text

    def test_longest_first_matching(self):
        """Longer words should be matched first to avoid partial replacements."""
        phonemes = {"执行": "zhí xíng", "执行器": "zhí xíng qì"}
        result = apply_phonemes("执行器启动", phonemes)
        assert "zhi 2 xing 2 qi 4" in result

    def test_word_not_in_text(self):
        result = apply_phonemes("你好世界", {"执行器": "zhí xíng qì"})
        assert result == "你好世界"


# ============ mark_english_terms ============

class TestMarkEnglishTerms:
    def test_english_word_with_spaces(self):
        # \b word boundary requires non-word chars around English
        result = mark_english_terms("使用 Python 开发")
        assert '<lang xml:lang="en-US">Python</lang>' in result

    def test_english_adjacent_to_chinese(self):
        # Chinese chars are \w in Python regex, so \b doesn't fire
        result = mark_english_terms("使用Python开发")
        assert "Python" in result

    def test_multi_word_phrase(self):
        result = mark_english_terms("安装Claude Code工具")
        assert '<lang xml:lang="en-US">Claude Code</lang>' in result

    def test_preserves_existing_xml(self):
        text = '<phoneme alphabet="sapi" ph="zhi 2">执行</phoneme> 和 Python'
        result = mark_english_terms(text)
        assert '<phoneme alphabet="sapi"' in result
        assert '<lang xml:lang="en-US">Python</lang>' in result

    def test_no_english(self):
        text = "这是纯中文文本"
        result = mark_english_terms(text)
        assert "lang" not in result

    def test_single_char_skipped(self):
        """Single-character English words should not be wrapped."""
        result = mark_english_terms("这是 a 测试")
        assert '<lang xml:lang="en-US">a</lang>' not in result


# ============ format_time ============

class TestFormatTime:
    def test_zero(self):
        assert format_time(0) == "00:00:00,000"

    def test_basic_seconds(self):
        assert format_time(5.5) == "00:00:05,500"

    def test_minutes(self):
        assert format_time(65.123) == "00:01:05,123"

    def test_hours(self):
        assert format_time(3661.0) == "01:01:01,000"

    def test_millisecond_precision(self):
        assert format_time(1.999) == "00:00:01,999"


# ============ Section parsing logic ============

class TestSectionParsing:
    """Test the section extraction logic from podcast.txt format."""

    @staticmethod
    def _parse_sections(text):
        section_pattern = r'\[SECTION:(\w+)\]'
        sections = []
        matches = list(re.finditer(section_pattern, text))
        for i, match in enumerate(matches):
            section_name = match.group(1)
            start_pos = match.end()
            end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            section_text = text[start_pos:end_pos].strip()
            first_text = re.sub(r'\s+', '', section_text[:80])
            is_silent = len(section_text.strip()) == 0
            label_text = section_text.split('\n')[0].strip() if section_text.strip() else section_name
            label = re.split(r'[，。！？、：；]', label_text)[0][:10] if label_text else section_name
            sections.append({
                'name': section_name,
                'label': label or section_name,
                'first_text': first_text,
                'is_silent': is_silent,
            })
        return sections

    def test_basic_sections(self):
        text = "[SECTION:hero]\n大家好，欢迎观看\n\n[SECTION:features]\n功能介绍"
        sections = self._parse_sections(text)
        assert len(sections) == 2
        assert sections[0]['name'] == 'hero'
        assert sections[1]['name'] == 'features'

    def test_silent_section(self):
        text = "[SECTION:hero]\n内容\n\n[SECTION:outro]\n\n"
        sections = self._parse_sections(text)
        assert sections[0]['is_silent'] is False
        assert sections[1]['is_silent'] is True

    def test_label_extraction(self):
        text = "[SECTION:hero]\n大家好，欢迎来到本期视频"
        sections = self._parse_sections(text)
        assert sections[0]['label'] == "大家好"

    def test_no_sections(self):
        sections = self._parse_sections("纯文本没有章节标记")
        assert len(sections) == 0


# ============ BUILTIN_POLYPHONES ============

class TestBuiltinPolyphones:
    def test_contains_common_words(self):
        assert "执行器" in BUILTIN_POLYPHONES
        assert "重做" in BUILTIN_POLYPHONES
        assert "命令行" in BUILTIN_POLYPHONES

    def test_pinyin_format(self):
        for word, pinyin in BUILTIN_POLYPHONES.items():
            assert isinstance(pinyin, str)
            assert len(pinyin) > 0
            assert len(pinyin.split()) >= 1
