import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from ui.app import *
```

**`requirements.txt`** (make sure all these are in it):
```
fastapi
uvicorn
gspread
oauth2client
pandas
streamlit
requests
