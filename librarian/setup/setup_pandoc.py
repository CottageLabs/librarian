# one-time per environment; safe to run repeatedly
import os
import shutil
import sys

def has_pandoc():
    # honor explicit path if set
    if os.environ.get("PYPANDOC_PANDOC"):
        return os.path.exists(os.environ["PYPANDOC_PANDOC"])
    return shutil.which("pandoc") is not None

def main():
    if has_pandoc():
        print("pandoc already available")
        return 0
    try:
        import pypandoc
    except Exception as e:
        print("pypandoc not installed. Add it to dependencies or install it first.", file=sys.stderr)
        return 1
    print("Downloading pandoc via pypandoc.download_pandoc() ...")
    pypandoc.download_pandoc()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
