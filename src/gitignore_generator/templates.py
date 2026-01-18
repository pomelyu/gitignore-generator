"""
Template fetching and caching from GitHub's gitignore repository.
Uses GitHub API to browse templates and downloads them on-demand.
Local caching to ~/.cache/gitignore-generator/ to minimize network calls.
"""

import json
import os
import urllib.error
import urllib.request
from datetime import datetime
from datetime import timedelta
from pathlib import Path
from typing import Dict
from typing import List
from typing import Optional

GITHUB_API_BASE = "https://api.github.com/repos/github/gitignore/contents"
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/github/gitignore/main"

# Cache location
if os.name == 'nt':  # Windows
    CACHE_DIR = Path(os.getenv('APPDATA', '~')) / 'gitignore-generator' / 'cache'
else:  # macOS, Linux
    CACHE_DIR = Path.home() / '.cache' / 'gitignore-generator'

MANIFEST_FILE = CACHE_DIR / 'manifest.json'
TEMPLATES_CACHE_DIR = CACHE_DIR / 'templates'
CACHE_VALIDITY_DAYS = 7


class TemplateManager:
    """Manages fetching, caching, and searching gitignore templates."""

    def __init__(self):
        """Initialize the template manager."""
        self._manifest: Optional[Dict] = None
        self._ensure_cache_dir()

    def _ensure_cache_dir(self) -> None:
        """Create cache directories if they don't exist."""
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        TEMPLATES_CACHE_DIR.mkdir(parents=True, exist_ok=True)

    def _is_cache_valid(self) -> bool:
        """Check if cached manifest is still valid."""
        if not MANIFEST_FILE.exists():
            return False
        
        mod_time = datetime.fromtimestamp(MANIFEST_FILE.stat().st_mtime)
        age = datetime.now() - mod_time
        return age < timedelta(days=CACHE_VALIDITY_DAYS)

    def _fetch_from_api(self, url: str) -> Optional[str]:
        """Fetch content from GitHub API with error handling."""
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                return response.read().decode('utf-8')
        except urllib.error.URLError as e:
            print(f"Network error: {e}. Check your internet connection.")
            return None
        except Exception as e:
            print(f"Error fetching from GitHub: {e}")
            return None

    def _load_manifest(self) -> Dict:
        """Load manifest from cache or fetch from API."""
        if self._is_cache_valid():
            try:
                with open(MANIFEST_FILE, 'r') as f:
                    self._manifest = json.load(f)
                    return self._manifest
            except Exception as e:
                print(f"Error loading cached manifest: {e}")

        # Fetch fresh manifest from API
        return self._fetch_manifest_from_api()

    def _fetch_manifest_from_api(self) -> Dict:
        """Fetch and cache the template manifest from GitHub API."""
        print("Fetching template list from GitHub...")
        
        # Fetch root templates
        root_data = self._fetch_from_api(GITHUB_API_BASE)
        if not root_data:
            return {}

        manifest = {
            'root': {},
            'Global': {},
            'community': {},
            'timestamp': datetime.now().isoformat()
        }

        try:
            root_templates = json.loads(root_data)
            for item in root_templates:
                if item['type'] == 'file' and item['name'].endswith('.gitignore'):
                    template_name = item['name'].replace('.gitignore', '')
                    manifest['root'][template_name] = {
                        'path': f"{item['name']}",
                        'download_url': item['download_url'],
                        'category': 'root'
                    }
        except json.JSONDecodeError:
            pass

        # Fetch Global templates
        for subfolder in ['Global', 'community']:
            subfolder_data = self._fetch_from_api(f"{GITHUB_API_BASE}/{subfolder}")
            if not subfolder_data:
                continue

            try:
                items = json.loads(subfolder_data)
                for item in items:
                    if item['type'] == 'dir':
                        # Fetch contents of subdirectory
                        subdir_data = self._fetch_from_api(item['url'])
                        if subdir_data:
                            try:
                                sub_items = json.loads(subdir_data)
                                for sub_item in sub_items:
                                    if sub_item['type'] == 'file' and sub_item['name'].endswith('.gitignore'):
                                        template_name = sub_item['name'].replace('.gitignore', '')
                                        full_name = f"{subfolder}/{item['name']}/{template_name}"
                                        manifest[subfolder][full_name] = {
                                            'path': f"{subfolder}/{item['name']}/{sub_item['name']}",
                                            'download_url': sub_item['download_url'],
                                            'category': subfolder
                                        }
                            except json.JSONDecodeError:
                                pass
                    elif item['type'] == 'file' and item['name'].endswith('.gitignore'):
                        template_name = item['name'].replace('.gitignore', '')
                        full_name = f"{subfolder}/{template_name}"
                        manifest[subfolder][full_name] = {
                            'path': f"{subfolder}/{item['name']}",
                            'download_url': item['download_url'],
                            'category': subfolder
                        }
            except json.JSONDecodeError:
                pass

        self._manifest = manifest
        self._save_manifest()
        return manifest

    def _save_manifest(self) -> None:
        """Save manifest to cache file."""
        try:
            with open(MANIFEST_FILE, 'w') as f:
                json.dump(self._manifest, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save manifest cache: {e}")

    def get_manifest(self) -> Dict:
        """Get template manifest (cached or fresh)."""
        if self._manifest is None:
            self._manifest = self._load_manifest()
        return self._manifest

    def _build_search_index(self) -> Dict[str, List[str]]:
        """Build a searchable index of all templates (lowercase for fuzzy matching)."""
        manifest = self.get_manifest()
        index = {}
        
        for category in ['root', 'Global', 'community']:
            for full_name in manifest.get(category, {}):
                # Index by full name and individual parts
                parts = full_name.lower().split('/')
                for part in parts:
                    if part not in index:
                        index[part] = []
                    if full_name not in index[part]:
                        index[part].append(full_name)
        
        return index

    def search_templates(self, query: str) -> List[str]:
        """
        Search for templates matching a query (case-insensitive, fuzzy).
        Returns list of matching template full names.
        """
        if not query.strip():
            return []

        manifest = self.get_manifest()
        query_lower = query.lower()
        results = []

        # Collect all templates
        all_templates = []
        for category in ['root', 'Global', 'community']:
            all_templates.extend(manifest.get(category, {}).keys())

        # Exact match (case-insensitive)
        for template in all_templates:
            if template.lower() == query_lower:
                return [template]

        # Prefix match
        for template in all_templates:
            if template.lower().startswith(query_lower):
                results.append(template)

        # Partial match (any part contains query)
        for template in all_templates:
            if query_lower in template.lower() and template not in results:
                results.append(template)

        return results

    def get_template_content(self, template_name: str) -> Optional[str]:
        """
        Get the content of a template.
        First checks cache, then fetches from GitHub if needed.
        """
        manifest = self.get_manifest()
        
        # Find template in manifest
        template_info = None
        for category in ['root', 'Global', 'community']:
            if template_name in manifest.get(category, {}):
                template_info = manifest[category][template_name]
                break

        if not template_info:
            return None

        # Check cache first
        cache_file = TEMPLATES_CACHE_DIR / f"{template_name.replace('/', '_')}.gitignore"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    return f.read()
            except Exception:
                pass

        # Fetch from GitHub
        download_url = template_info.get('download_url')
        if not download_url:
            # Build URL manually
            download_url = f"{GITHUB_RAW_BASE}/{template_info['path']}"

        content = self._fetch_from_api(download_url)
        
        if content:
            # Cache the content
            try:
                with open(cache_file, 'w') as f:
                    f.write(content)
            except Exception:
                pass
        
        return content

    def get_all_templates(self) -> Dict[str, List[str]]:
        """Return all templates organized by category."""
        manifest = self.get_manifest()
        return {
            'root': sorted(manifest.get('root', {}).keys()),
            'Global': sorted(manifest.get('Global', {}).keys()),
            'community': sorted(manifest.get('community', {}).keys())
        }

    def resolve_template(self, template_name: str) -> Optional[str]:
        """
        Resolve a template name to its full path.
        Handles ambiguous names by suggesting options.
        Returns the resolved template name or None if not found.
        """
        manifest = self.get_manifest()
        
        # Exact match (case-insensitive)
        for category in ['root', 'Global', 'community']:
            for full_name in manifest.get(category, {}):
                if full_name.lower() == template_name.lower():
                    return full_name

        # Search for matches
        matches = self.search_templates(template_name)
        
        if len(matches) == 1:
            return matches[0]
        elif len(matches) > 1:
            return None  # Ambiguous - let caller handle showing options
        
        return None
