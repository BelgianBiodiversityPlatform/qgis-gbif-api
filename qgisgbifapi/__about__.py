#! python3  # noqa: E265

"""
    Metadata about the package to easily retrieve informations about it.
    See: https://packaging.python.org/guides/single-sourcing-package-version/
"""

# ############################################################################
# ########## Libraries #############
# ##################################

# standard library
from configparser import ConfigParser
from pathlib import Path

# ############################################################################
# ########## Globals ###############
# ##################################

DIR_PLUGIN_ROOT: Path = Path(__file__).parent
PLG_METADATA_FILE: Path = DIR_PLUGIN_ROOT.resolve() / "metadata.txt"


# ############################################################################
# ########## Functions #############
# ##################################
def plugin_metadata_as_dict() -> dict:
    """Read plugin metadata.txt and returns it as a Python dict.

    Raises:
        IOError: if metadata.txt is not found

    Returns:
        dict: dict of dicts.
    """
    config = ConfigParser()
    if PLG_METADATA_FILE.is_file():
        config.read(PLG_METADATA_FILE.resolve(), encoding="UTF-8")
        return {s: dict(config.items(s)) for s in config.sections()}
    else:
        raise OSError("Plugin metadata.txt not found at: %s" % PLG_METADATA_FILE)  # noqa: E501


# ############################################################################
# ########## Variables #############
# ##################################

# store full metadata.txt as dict into a var
__plugin_md__: dict = plugin_metadata_as_dict()

__api_endpoint__: str = __plugin_md__.get("api").get("endpoint")
__api_occurrences_search__: str = __plugin_md__.get("api").get("occurrences_search")  # noqa: E501
__api_per_page_records__: str = __plugin_md__.get("api").get("per_page_records")  # noqa: E501
__api_max_total_records__: str = __plugin_md__.get("api").get("max_total_records")  # noqa: E501
__api_warning_threshold__: str = __plugin_md__.get("api").get("warning_threshold")  # noqa: E501
__api_timeout__: str = __plugin_md__.get("api").get("timeout_ms")  # noqa: E501
__field_list__: list = [
    t.strip() for t in __plugin_md__.get("api").get("list_minimal_mode_fields").split(',')  # noqa: E501
]
