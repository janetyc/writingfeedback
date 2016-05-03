import os
from crowdtask import create_app

port = int(os.environ.get('PORT', 5000))
app = create_app(os.getenv('ENV'))
app.run(host='0.0.0.0', port=port, debug=app.debug)
