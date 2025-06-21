from sentence_transformers import SentenceTransformer

def main():
    """
    Downloads the specified SentenceTransformer model to the cache.
    This script is intended to be run during the build process to pre-load
    the model, preventing download delays during application startup.
    """
    model_name = 'all-MiniLM-L6-v2'
    print(f"Downloading SentenceTransformer model: {model_name}...")
    try:
        SentenceTransformer(model_name)
        print("Model downloaded and cached successfully.")
    except Exception as e:
        print(f"Error downloading model: {e}")
        # Exit with a non-zero status code to fail the build if download fails
        exit(1)

if __name__ == "__main__":
    main() 