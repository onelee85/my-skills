"""Tests for generate_shorts.py pure functions.

Tests cover section filtering, PascalCase conversion, timing generation,
and script title extraction — all without requiring ffmpeg or Remotion.
"""
import json
import os
import tempfile
import pytest
from conftest import shorts_module

to_pascal_case = shorts_module.to_pascal_case
filter_sections = shorts_module.filter_sections
generate_timing = shorts_module.generate_timing
load_script = shorts_module.load_script
FPS = shorts_module.FPS
INTRO_FRAMES = shorts_module.INTRO_FRAMES
CTA_FRAMES = shorts_module.CTA_FRAMES


# ============ to_pascal_case ============

class TestToPascalCase:
    def test_kebab_case(self):
        assert to_pascal_case("content-1") == "Content1"

    def test_snake_case(self):
        assert to_pascal_case("my_section") == "MySection"

    def test_single_word(self):
        assert to_pascal_case("pipeline") == "Pipeline"

    def test_with_version(self):
        assert to_pascal_case("arch-v2") == "ArchV2"

    def test_multiple_hyphens(self):
        assert to_pascal_case("a-b-c") == "ABC"

    def test_mixed_separators(self):
        assert to_pascal_case("my-long_name") == "MyLongName"


# ============ filter_sections ============

class TestFilterSections:
    @staticmethod
    def _make_timing(sections):
        return {"sections": sections}

    @staticmethod
    def _make_section(name, duration=30, is_silent=False):
        return {
            "name": name,
            "duration": duration,
            "duration_frames": duration * FPS,
            "start_time": 0,
            "start_frame": 0,
            "is_silent": is_silent,
        }

    def test_filters_skip_names(self):
        timing = self._make_timing([
            self._make_section("hero"),
            self._make_section("features"),
            self._make_section("outro"),
        ])
        result = filter_sections(timing, min_duration=20, skip_names="hero,outro")
        assert len(result) == 1
        assert result[0]["name"] == "features"

    def test_filters_short_sections(self):
        timing = self._make_timing([
            self._make_section("features", duration=30),
            self._make_section("brief", duration=10),
        ])
        result = filter_sections(timing, min_duration=20, skip_names="")
        assert len(result) == 1
        assert result[0]["name"] == "features"

    def test_filters_silent_sections(self):
        timing = self._make_timing([
            self._make_section("features", is_silent=False),
            self._make_section("outro", is_silent=True),
        ])
        result = filter_sections(timing, min_duration=0, skip_names="")
        assert len(result) == 1
        assert result[0]["name"] == "features"

    def test_empty_sections(self):
        result = filter_sections({"sections": []}, min_duration=20, skip_names="hero")
        assert result == []

    def test_all_filtered_out(self):
        timing = self._make_timing([self._make_section("hero", duration=5)])
        result = filter_sections(timing, min_duration=20, skip_names="")
        assert result == []

    def test_skip_names_with_spaces(self):
        timing = self._make_timing([
            self._make_section("hero"),
            self._make_section("features"),
        ])
        result = filter_sections(timing, min_duration=0, skip_names="hero , features")
        assert result == []


# ============ generate_timing ============

class TestGenerateTiming:
    def test_basic_timing(self):
        section = {
            "name": "features",
            "label": "功能介绍",
            "duration": 30.0,
            "duration_frames": 900,
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            result = generate_timing(section, tmpdir)

        assert result["fps"] == FPS
        assert result["total_frames"] == INTRO_FRAMES + 900 + CTA_FRAMES
        assert result["source_section"] == "features"
        assert len(result["sections"]) == 3

        intro = result["sections"][0]
        assert intro["name"] == "intro"
        assert intro["is_silent"] is True
        assert intro["duration_frames"] == INTRO_FRAMES

        content = result["sections"][1]
        assert content["name"] == "features"
        assert content["start_frame"] == INTRO_FRAMES
        assert content["duration_frames"] == 900

        cta = result["sections"][2]
        assert cta["name"] == "cta"
        assert cta["is_silent"] is True
        assert cta["start_frame"] == INTRO_FRAMES + 900

    def test_writes_json_file(self):
        section = {
            "name": "demo",
            "label": "演示",
            "duration": 20.0,
            "duration_frames": 600,
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            generate_timing(section, tmpdir)
            json_path = os.path.join(tmpdir, "short_timing.json")
            assert os.path.exists(json_path)
            with open(json_path) as f:
                data = json.load(f)
            assert data["source_section"] == "demo"


# ============ load_script ============

class TestLoadScript:
    def test_basic_extraction(self):
        script = "[SECTION:hero]\n大家好，欢迎来到本期视频。\n\n[SECTION:features]\n功能介绍，这是一个测试。\n"
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "podcast.txt"), "w", encoding="utf-8") as f:
                f.write(script)
            result = load_script(tmpdir)
        assert "hero" in result
        assert "features" in result

    def test_title_truncation(self):
        long_line = "这是一个非常非常非常非常非常非常非常非常长的标题超过三十个字符限制了吧"
        script = f"[SECTION:test]\n{long_line}\n"
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "podcast.txt"), "w", encoding="utf-8") as f:
                f.write(script)
            result = load_script(tmpdir)
        assert len(result["test"]) <= 30

    def test_missing_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = load_script(tmpdir)
        assert result == {}

    def test_empty_section(self):
        script = "[SECTION:hero]\n\n[SECTION:features]\n内容\n"
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "podcast.txt"), "w", encoding="utf-8") as f:
                f.write(script)
            result = load_script(tmpdir)
        assert "hero" not in result
        assert "features" in result

    def test_hyphenated_section_name(self):
        script = "[SECTION:content-1]\n第一部分内容\n"
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "podcast.txt"), "w", encoding="utf-8") as f:
                f.write(script)
            result = load_script(tmpdir)
        assert "content-1" in result
