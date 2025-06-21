from sentence_transformers import SentenceTransformer

def main():
    """
    Downloads the specified SentenceTransformer model to a local path.
    This script is intended to be run during the build process to pre-load
    the model into the project directory, so it gets bundled with the deploy.
    """
    model_name = 'all-MiniLM-L6-v2'
    save_path = 'all-MiniLM-L6-v2-local'

    print(f"Downloading SentenceTransformer model '{model_name}' to '{save_path}'...")
    try:
        model = SentenceTransformer(model_name)
        model.save(path=save_path)
        print("Model downloaded and saved successfully to local path.")
    except Exception as e:
        print(f"Error downloading model: {e}")
        # Exit with a non-zero status code to fail the build if download fails
        exit(1)

if __name__ == "__main__":
    main() 