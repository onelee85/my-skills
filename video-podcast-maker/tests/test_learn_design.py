"""Tests for learn_design.py — image extraction and preference management."""
import hashlib
import json
import os
import shutil
import tempfile

import pytest

from conftest import learn_module as learn


# ============ TestGenerateReferenceId ============

class TestGenerateReferenceId:
    def test_bilibili_url(self):
        url = "https://www.bilibili.com/video/BV1xx411c7mD"
        ref_id = learn.generate_reference_id(url)
        assert ref_id == "bilibili-BV1xx411c7mD"

    def test_youtube_url(self):
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        ref_id = learn.generate_reference_id(url)
        assert ref_id == "youtube-dQw4w9WgXcQ"

    def test_youtube_short_url(self):
        url = "https://youtu.be/dQw4w9WgXcQ"
        ref_id = learn.generate_reference_id(url)
        assert ref_id == "youtube-dQw4w9WgXcQ"

    def test_deterministic_fallback_hash(self):
        url = "https://example.com/some/random/video"
        ref_id1 = learn.generate_reference_id(url)
        ref_id2 = learn.generate_reference_id(url)
        assert ref_id1 == ref_id2  # deterministic
        assert ref_id1.startswith("ref-")
        # Verify the hash is md5-based (8 chars)
        expected_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        assert ref_id1 == f"ref-{expected_hash}"

    def test_local_video(self):
        ref_id = learn.generate_reference_id("/path/to/my_video.mp4")
        assert ref_id == "local-my_video"

    def test_images_with_name(self):
        ref_id = learn.generate_reference_id(None, name="my-style")
        assert ref_id == "images-my-style"

    def test_images_without_name(self):
        ref_id = learn.generate_reference_id(None)
        # Should produce a timestamp-based fallback like images-YYYYMMDD or images-<hash>
        assert ref_id.startswith("images-")

    def test_collision_suffix(self):
        existing_ids = {"bilibili-BV1xx411c7mD", "bilibili-BV1xx411c7mD-2"}
        url = "https://www.bilibili.com/video/BV1xx411c7mD"
        ref_id = learn.generate_reference_id(url, existing_ids=existing_ids)
        assert ref_id == "bilibili-BV1xx411c7mD-3"

    def test_no_collision_when_unique(self):
        existing_ids = {"other-id"}
        url = "https://www.bilibili.com/video/BV1xx411c7mD"
        ref_id = learn.generate_reference_id(url, existing_ids=existing_ids)
        assert ref_id == "bilibili-BV1xx411c7mD"


# ============ TestDetectInputType ============

class TestDetectInputType:
    def test_url(self):
        assert learn.detect_input_type("https://www.bilibili.com/video/BV1xx411c7mD") == "url"
        assert learn.detect_input_type("http://example.com/video") == "url"

    def test_video(self, tmp_path):
        video_file = tmp_path / "test.mp4"
        video_file.touch()
        assert learn.detect_input_type(str(video_file)) == "local_video"

    def test_image(self, tmp_path):
        image_file = tmp_path / "test.jpg"
        image_file.touch()
        assert learn.detect_input_type(str(image_file)) == "image"

    def test_unsupported_extension(self, tmp_path):
        unsupported_file = tmp_path / "test.pdf"
        unsupported_file.touch()
        assert learn.detect_input_type(str(unsupported_file)) == "unsupported"

    def test_nonexistent_file(self):
        assert learn.detect_input_type("/nonexistent/path/file.mp4") == "not_found"


# ============ TestDetectOrientation ============

class TestDetectOrientation:
    def test_horizontal(self):
        assert learn.detect_orientation(1920, 1080) == "horizontal"
        assert learn.detect_orientation(3840, 2160) == "horizontal"

    def test_vertical(self):
        assert learn.detect_orientation(1080, 1920) == "vertical"
        assert learn.detect_orientation(2160, 3840) == "vertical"

    def test_square(self):
        assert learn.detect_orientation(1080, 1080) == "square"


# ============ TestCreateReferenceDir ============

class TestCreateReferenceDir:
    def test_creates_structure(self, tmp_path):
        ref_dir = learn.create_reference_dir(str(tmp_path), "test-ref")
        assert os.path.isdir(ref_dir)
        frames_dir = os.path.join(ref_dir, "frames")
        assert os.path.isdir(frames_dir)

    def test_returns_path(self, tmp_path):
        ref_dir = learn.create_reference_dir(str(tmp_path), "my-ref")
        assert ref_dir == os.path.join(str(tmp_path), "my-ref")


# ============ TestCopyImages ============

class TestCopyImages:
    def _make_images(self, tmp_path, count, ext=".png"):
        images = []
        for i in range(count):
            img = tmp_path / f"img_{i:02d}{ext}"
            img.write_bytes(b"\x89PNG\r\n")  # fake content
            images.append(str(img))
        return images

    def test_copies_images(self, tmp_path):
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        ref_dir = tmp_path / "ref"
        ref_dir.mkdir()
        (ref_dir / "frames").mkdir()

        images = self._make_images(src_dir, 3)
        result = learn.copy_images(images, str(ref_dir))

        assert len(result) == 3
        for f in result:
            assert os.path.exists(f)

    def test_first_becomes_cover(self, tmp_path):
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        ref_dir = tmp_path / "ref"
        ref_dir.mkdir()
        (ref_dir / "frames").mkdir()

        images = self._make_images(src_dir, 2)
        learn.copy_images(images, str(ref_dir))

        # Cover should exist in ref_dir root
        covers = [f for f in os.listdir(str(ref_dir)) if f.startswith("cover")]
        assert len(covers) == 1

    def test_cover_preserves_extension(self, tmp_path):
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        ref_dir = tmp_path / "ref"
        ref_dir.mkdir()
        (ref_dir / "frames").mkdir()

        images = self._make_images(src_dir, 2, ext=".jpg")
        learn.copy_images(images, str(ref_dir))

        assert os.path.exists(os.path.join(str(ref_dir), "cover.jpg"))

    def test_max_frames_cap(self, tmp_path):
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        ref_dir = tmp_path / "ref"
        ref_dir.mkdir()
        (ref_dir / "frames").mkdir()

        # 12 images — should copy only MAX_FRAMES=8
        images = self._make_images(src_dir, 12)
        result = learn.copy_images(images, str(ref_dir))

        assert len(result) == learn.MAX_FRAMES


# ============ TestSaveReport ============

class TestSaveReport:
    def test_writes_valid_json(self, tmp_path):
        ref_dir = str(tmp_path)
        report = {
            "ref_id": "test-ref",
            "source": "url",
            "orientation": "horizontal",
            "frame_count": 5,
            "frames": [],
        }
        learn.save_report(report, ref_dir)

        report_path = os.path.join(ref_dir, "report.json")
        assert os.path.exists(report_path)

        with open(report_path, encoding="utf-8") as f:
            loaded = json.load(f)

        assert loaded["ref_id"] == "test-ref"
        assert loaded["frame_count"] == 5

    def test_load_report(self, tmp_path):
        ref_dir = str(tmp_path)
        report = {"ref_id": "abc", "frame_count": 3}
        learn.save_report(report, ref_dir)
        loaded = learn.load_report(ref_dir)
        assert loaded["ref_id"] == "abc"


# ============ TestPreferenceManagement ============

class TestPreferenceManagement:
    def _v10_prefs(self):
        return {
            "version": "1.0",
            "updated_at": None,
            "global": {
                "visual": {"theme": "light", "primaryColor": "#4f6ef7"},
                "tts": {"backend": "azure"},
                "content": {"tone": "professional"},
            },
        }

    def _v11_prefs(self):
        return {
            "version": "1.1",
            "updated_at": None,
            "global": {
                "visual": {"theme": "light", "primaryColor": "#4f6ef7"},
                "tts": {"backend": "azure"},
                "content": {"tone": "professional"},
            },
            "topic_patterns": {},
            "style_profiles": {},
            "design_references": {},
            "learning_history": [],
        }

    def test_v10_migrated_to_v11(self, tmp_path):
        prefs_path = str(tmp_path / "prefs.json")
        v10 = self._v10_prefs()
        with open(prefs_path, "w", encoding="utf-8") as f:
            json.dump(v10, f)

        prefs = learn.load_prefs(prefs_path)
        assert prefs["version"] == "1.1"
        assert "style_profiles" in prefs
        assert "design_references" in prefs
        assert "learning_history" in prefs

    def test_migration_preserves_existing_fields(self, tmp_path):
        prefs_path = str(tmp_path / "prefs.json")
        v10 = self._v10_prefs()
        with open(prefs_path, "w", encoding="utf-8") as f:
            json.dump(v10, f)

        prefs = learn.load_prefs(prefs_path)
        assert prefs["global"]["visual"]["primaryColor"] == "#4f6ef7"
        assert prefs["global"]["tts"]["backend"] == "azure"

    def test_add_reference_index(self, tmp_path):
        prefs = self._v11_prefs()
        learn.add_reference_index(
            prefs,
            ref_id="bilibili-BV123",
            title="Test Video",
            source_url="https://bilibili.com/video/BV123",
            tags=["tech"],
        )
        assert "bilibili-BV123" in prefs["design_references"]
        ref = prefs["design_references"]["bilibili-BV123"]
        assert ref["title"] == "Test Video"
        assert ref["tags"] == ["tech"]
        assert "analyzed_at" in ref
        assert "path" in ref

    def test_create_new_style_profile(self, tmp_path):
        prefs = self._v11_prefs()
        learn.add_style_profile(
            prefs,
            name="dark-minimalist",
            description="Dark theme with minimal elements",
            props_override={"primaryColor": "#1a1a2e"},
            preferred_layouts=["CenteredShowcase"],
        )
        assert "dark-minimalist" in prefs["style_profiles"]
        profile = prefs["style_profiles"]["dark-minimalist"]
        assert profile["description"] == "Dark theme with minimal elements"
        assert profile["props_override"]["primaryColor"] == "#1a1a2e"
        assert "CenteredShowcase" in profile["preferred_layouts"]

    def test_update_existing_profile_union_layouts(self, tmp_path):
        prefs = self._v11_prefs()
        learn.add_style_profile(
            prefs,
            name="my-style",
            description="Initial",
            props_override={"primaryColor": "#aaa"},
            preferred_layouts=["SplitLayout"],
        )
        # Update same profile with additional layouts
        learn.add_style_profile(
            prefs,
            name="my-style",
            description="Updated",
            props_override={"primaryColor": "#bbb"},
            preferred_layouts=["CenteredShowcase"],
        )
        profile = prefs["style_profiles"]["my-style"]
        # Union of layouts
        assert "SplitLayout" in profile["preferred_layouts"]
        assert "CenteredShowcase" in profile["preferred_layouts"]
        # Latest props win
        assert profile["props_override"]["primaryColor"] == "#bbb"

    def test_remove_reference_cleans_profiles(self, tmp_path):
        design_refs_base = str(tmp_path / "design_references")
        os.makedirs(design_refs_base)
        ref_id = "bilibili-BV123"
        ref_dir = os.path.join(design_refs_base, ref_id)
        os.makedirs(ref_dir)

        prefs = self._v11_prefs()
        learn.add_reference_index(
            prefs,
            ref_id=ref_id,
            title="Test",
            source_url="https://bilibili.com/video/BV123",
            tags=[],
        )
        learn.add_style_profile(
            prefs,
            name="my-style",
            description="Style",
            props_override={},
            preferred_layouts=[],
            references=[ref_id],
        )

        learn.remove_reference(prefs, ref_id, design_refs_base)

        assert ref_id not in prefs["design_references"]
        assert ref_id not in prefs["style_profiles"].get("my-style", {}).get("references", [])

    def test_cleanup_orphaned_references(self, tmp_path):
        design_refs_base = str(tmp_path / "design_references")
        os.makedirs(design_refs_base)

        prefs = self._v11_prefs()
        # Add reference that has a real directory
        real_ref = "local-existing"
        os.makedirs(os.path.join(design_refs_base, real_ref))
        learn.add_reference_index(prefs, ref_id=real_ref, title="Real", source_url=None, tags=[])

        # Add reference without a directory (orphan)
        orphan_ref = "local-orphan"
        learn.add_reference_index(prefs, ref_id=orphan_ref, title="Orphan", source_url=None, tags=[])

        learn.cleanup_orphaned_references(prefs, design_refs_base)

        assert real_ref in prefs["design_references"]
        assert orphan_ref not in prefs["design_references"]
