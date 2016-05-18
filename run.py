import os
from crowdtask import create_app

env = os.getenv('ENV')
port = int(os.environ.get('PORT', 5000))
app = create_app(env)
app.run(host='0.0.0.0', port=port, debug=app.debug, ssl_context='adhoc')
#app.run(host='0.0.0.0', port=port, debug=app.debug, ssl_context=('ssl.cert','ssl.key'))
