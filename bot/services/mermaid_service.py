import base64
import json
import zlib
import requests
from logging import info, critical


MERMAID_API = "https://mermaid.ink"


def _encode_diagram(diagram: str) -> str:
    """Encode a Mermaid diagram into a pako-compressed Base64 string.

    :param diagram: Mermaid diagram definition to encode.
    :type diagram: str

    :returns: Pako-compressed and Base64-encoded diagram string.
    :rtype: str
    """
    graph_json = {
        "code": diagram,
        "mermaid": {"theme": "default"}
    }

    byte_data = json.dumps(graph_json).encode('ascii')
    compressed_data = zlib.compress(byte_data, level=9)
    b64_encoded = base64.b64encode(compressed_data).decode('ascii')

    return b64_encoded.replace('+', '-').replace('/', '_').strip('=')


def _build_url(diagram: str, type: str = 'img') -> str:
    """Build the Mermaid.ink API URL for a given diagram.

    :param diagram: Mermaid diagram definition.
    :type diagram: str

    :returns: Fully constructed Mermaid.ink API URL.
    :rtype: str
    """
    encoded_diagram = _encode_diagram(diagram)
    return f"{MERMAID_API}/{type}/pako:{encoded_diagram}"


def _is_valid_diagram(url: str) -> bool:
    """Check whether a Mermaid.ink API URL returns a valid response.

    :param url: API URL to validate.
    :type url: str

    :returns: True if the URL is valid (HTTP 200), otherwise False.
    :rtype: bool
    """
    try:
        response = requests.get(url, timeout=5)
        info(f"url: {url} - code: {response.status_code}")
        return response.status_code == 200
    except requests.RequestException as e:
        critical(e)
        return False


def generate_mermaid_diagram(diagram: str) -> str | None:
    """Generate a valid Mermaid.ink API URL for a given diagram.

    This function encodes the diagram, constructs the API URL,
    and validates it before returning.

    :param diagram: Mermaid diagram definition.
    :type diagram: str

    :returns: Valid API URL if available, otherwise ``None``.
    :rtype: str | None
    """
    diagram_url = _build_url(diagram)

    if _is_valid_diagram(diagram_url):
        return diagram_url

    return None
