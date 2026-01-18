"""
Tests for .gitignore generation and merging
"""

import tempfile
from pathlib import Path
import pytest
from gitignore_generator.generator import GitignoreGenerator


class TestGitignoreGenerator:
    """Test gitignore generation and merging logic"""

    def test_generator_init(self):
        """Test initialization"""
        with tempfile.TemporaryDirectory() as tmpdir:
            gen = GitignoreGenerator(str(Path(tmpdir) / ".gitignore"))
            assert gen is not None

    def test_merge_templates(self):
        """Test merging multiple templates"""
        with tempfile.TemporaryDirectory() as tmpdir:
            gen = GitignoreGenerator(str(Path(tmpdir) / ".gitignore"))
            
            templates = [
                ("Python", "*.pyc\n__pycache__/\n"),
                ("Git", ".git/\n"),
            ]
            
            result = gen.merge_templates(templates)
            
            assert "##### Python #####" in result
            assert "##### Git #####" in result
            assert "##### This Repo #####" in result
            assert "*.pyc" in result

    def test_duplicate_detection(self):
        """Test that duplicate rules are not included"""
        with tempfile.TemporaryDirectory() as tmpdir:
            gen = GitignoreGenerator(str(Path(tmpdir) / ".gitignore"))
            
            templates = [
                ("Python", "*.pyc\n__pycache__/\n"),
                ("Test", "*.pyc\ntest-results/\n"),  # *.pyc is duplicate
            ]
            
            result = gen.merge_templates(templates)
            
            # Both sections should be present
            assert "##### Python #####" in result
            assert "##### Test #####" in result
            
            # Both unique rules should be present
            assert "__pycache__/" in result
            assert "test-results/" in result

    def test_generate_creates_file(self):
        """Test that generate creates a .gitignore file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            gitignore_path = Path(tmpdir) / ".gitignore"
            gen = GitignoreGenerator(str(gitignore_path))
            
            templates = [
                ("Python", "*.pyc\n"),
            ]
            
            success, message = gen.generate(templates)
            
            assert success
            assert gitignore_path.exists()
            assert "*.pyc" in gitignore_path.read_text()

    def test_generate_append_mode(self):
        """Test append mode merges with existing .gitignore"""
        with tempfile.TemporaryDirectory() as tmpdir:
            gitignore_path = Path(tmpdir) / ".gitignore"
            
            # Create existing .gitignore
            gitignore_path.write_text("existing_rule/\n")
            
            gen = GitignoreGenerator(str(gitignore_path))
            
            templates = [
                ("Python", "*.pyc\n"),
            ]
            
            success, message = gen.generate(templates, merge_strategy='append')
            
            assert success
            content = gitignore_path.read_text()
            assert "existing_rule/" in content
            assert "*.pyc" in content

    def test_validate_syntax(self):
        """Test .gitignore syntax validation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            gen = GitignoreGenerator(str(Path(tmpdir) / ".gitignore"))
            
            content = "*.pyc\n__pycache__/\n"
            is_valid, warnings = gen.validate_syntax(content)
            
            assert is_valid
            assert len(warnings) == 0
