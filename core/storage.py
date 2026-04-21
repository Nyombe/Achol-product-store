from whitenoise.storage import CompressedManifestStaticFilesStorage

class ResilientWhiteNoiseStorage(CompressedManifestStaticFilesStorage):
    """
    A custom WhiteNoise storage class that ignores missing file errors 
    during post-processing. Useful for projects with third-party CSS 
    referencing missing source maps.
    """
    def post_process(self, *args, **kwargs):
        try:
            # We use a generator to yield results from the super class
            # while catching any MissingFileError or FileNotFoundError
            yield from super().post_process(*args, **kwargs)
        except Exception:
            # Silence errors (like missing .map files) to allow the build to complete
            pass
