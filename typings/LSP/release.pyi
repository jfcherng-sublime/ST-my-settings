import argparse
from _typeshed import Incomplete

PACKAGE_PATH: Incomplete
MESSAGE_DIR: str
MESSAGE_PATH: Incomplete
CONFIGURATION: Incomplete
RELEASE_BRANCH: Incomplete
GITHUB_REPO: Incomplete
RELEASE_VERSION_PREFIX: Incomplete
SETTINGS: Incomplete
PYTHON_VERSION_PATH: Incomplete

def get_message(fname: str) -> str: ...
def put_message(fname: str, text: str) -> None: ...
def build_messages_json(version_history: list[str]) -> None:
    """Write the version history to the messages.json file."""
def version_history() -> list[str]:
    """Return a list of all releases."""
def parse_version(version: str) -> tuple[int, int, int]:
    """Convert filename to version tuple (major, minor, patch)."""
def get_version_with_prefix(version: str) -> str: ...
def git(*args: str) -> str | None:
    """Run git command within current package path."""
def commit_release(version: str) -> None:
    """Create a 'Cut <version>' commit and tag."""
def build_release(args: argparse.Namespace) -> None:
    """Build the new release locally."""
def publish_release(args: argparse.Namespace) -> None:
    """Publish the new release."""
