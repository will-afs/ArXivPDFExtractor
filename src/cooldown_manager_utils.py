import urllib

def get_permission_to_request_arxiv(cooldown_manager_uri:str):
    """Request permission to contact ArXiv.org API to the CooldownManager of the project

    Parameters:

    Returns:
    bool : True if the CooldownManager gave its permission, False otherwise
    """
    return urllib.request.urlopen(cooldown_manager_uri)