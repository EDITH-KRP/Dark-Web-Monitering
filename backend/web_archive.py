import requests

def fetch_archive(url):
    """Fetch the archived version of a website"""
    archive_url = f'http://archive.org/wayback/available?url={url}'
    
    try:
        response = requests.get(archive_url)
        data = response.json()
        
        if data['archived_snapshots']:
            return {'status': 'found', 'url': data['archived_snapshots']['closest']['url']}
        else:
            return {'status': 'not found'}

    except requests.RequestException as e:
        return {'error': f"Failed to fetch archive: {e}"}
