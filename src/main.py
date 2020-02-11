import argparse
import webbrowser
from vinci.vinci import app


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--nopen", help="Open browser tab.", action="store_true")
    parser.add_argument("--port", type=int, help="HTTP address port.", default=5000)
    parser.add_argument("--debug", type=bool, help="Set debug flags", default=False)
    args = parser.parse_args()

    if not args.nopen:
        webbrowser.open_new_tab(f"http://localhost:{args.port}/")

    app.run(debug=args.debug, host="0.0.0.0", port=args.port, use_reloader=args.debug)


if __name__ == "__main__":
    main()
