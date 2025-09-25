import base64
import json
import zlib
import requests
from logging import info, critical


MERMAID_API = "https://mermaid.ink/img/"


def _encode_diagram(diagram: str) -> str:
    """ Converts diagram string to pako-compressed base64 encoding 
    
    :param diagram: Mermaid diagram string to be converted
    :type diagram: str

    :returns: Pako-compressed base64 encoded string
    :rtype: str
    """
    graph_json = {
        "code": diagram,
        "mermaid": {"theme": "default"}
    }

    byte_data = json.dumps(graph_json).encode('ascii')
    compressed_data = zlib.compress(byte_data, level=9)
    b64_encoded = base64.b64encode(compressed_data).decode('ascii')

    return b64_encoded.replace('+', '-').replace('/', '_')


def _build_url(diagram: str) -> str:
    """ Constructs mermaid ink API url to generate mermaid diagram image
    
    :param diagram: Mermaid script from which the diagram will be generated
    :type diagram: str

    :returns: Mermaid ink API url
    :rtype: str
    """
    encoded_diagram = _encode_diagram(diagram)
    return f"{MERMAID_API}pako:{encoded_diagram}"


def _is_valid_diagram(url: str) -> bool:
    """ Validates Mermaid API url
    
    :param url: Url to validate
    :type url: str

    :returns: Whether url is valid or not
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
    """ Constructs API url and validates it
    
    :param diagram: Mermaid diagram script
    :type diagram: str

    :returns: API url if it's valid, otherwise None
    :rtype: str | None
    """
    diagram_url = _build_url(diagram)

    if _is_valid_diagram(diagram_url):
        return diagram_url

    return None
