import base64
import requests


MERMAID_API = "https://mermaid.ink/img/"


def _encode_diagram(diagram: str) -> str:
    """ Converts script string to base64 encoding 
    
    :param diagram: String to be converted
    :type diagram: str

    :returns: Converted string
    :rtype: str
    """
    diagram_bytes = diagram.encode("utf8")
    base64_bytes = base64.urlsafe_b64encode(diagram_bytes)
    return base64_bytes.decode("ascii")


def _build_url(diagram: str) -> str:
    """ Constructs mermaid ink API url to generate mermaid diagram image
    
    :param diagram: Mermaid script from which the diagram will be generated
    :type diagram: str

    :returns: Mermaid ink API url
    :rtype: str
    """
    encoded_diagram = _encode_diagram(diagram)
    return f"{MERMAID_API}{encoded_diagram}"


def _is_valid_diagram(url: str) -> bool:
    """ Validates Mermaid API url
    
    :param url: Url to validate
    :type url: str

    :returns: Whether url is valid or not
    :rtype: bool
    """
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
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
