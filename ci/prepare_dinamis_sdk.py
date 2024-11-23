# author: Florian de Boissieu
# Prepare the dinamis sdk authentication for CI tests
# TODO: remove when new version of dinamis-sdk is released (supporting env variables)

import json
import os
from path import Path

DINAMIS_API_KEY_FILE = Path("~/.config/dinamis_sdk_auth/.api_key").expand()

if not DINAMIS_API_KEY_FILE.exists():
    DINAMIS_API_KEY = os.getenv("DINAMIS_API_KEY")
    DINAMIS_API_SECRET = os.getenv("DINAMIS_API_SECRET")

    DINAMIS_API_KEY_FILE.parent.makedirs_p()

    api_key = {"access-key": DINAMIS_API_KEY, "secret-key": DINAMIS_API_SECRET}
    with open(DINAMIS_API_KEY_FILE, "w") as f:
        json.dump(api_key, f)