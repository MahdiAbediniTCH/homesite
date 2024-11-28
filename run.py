import sys
from homesite import app

if __name__ == "__main__":
    debug = True
    if len(sys.argv) > 1:
        debug = bool(int(sys.argv[1]))
    print(" * GUEST PASSWORD: 20532102")
    app.run(debug=debug, port=80, host="0.0.0.0")
