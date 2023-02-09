try:
    from nltk.downloader import Downloader
    from nltk import download, download_shell

    download('vader_lexicon', quiet=True)
except ModuleNotFoundError:
    print("nltk module not properly installed")
