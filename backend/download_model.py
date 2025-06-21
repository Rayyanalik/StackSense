from sentence_transformers import SentenceTransformer
import json
import numpy as np
import os

def main():
    """
    Downloads the model and pre-computes project embeddings.
    This script is intended to be run during the build process to create
    all necessary artifacts, preventing delays during application startup.
    """
    # --- Part 1: Download and save the model ---
    model_name = 'all-MiniLM-L6-v2'
    save_path = 'all-MiniLM-L6-v2-local'

    print(f"Downloading SentenceTransformer model '{model_name}' to '{save_path}'...")
    try:
        model = SentenceTransformer(model_name)
        model.save(path=save_path)
        print("Model downloaded and saved successfully to local path.")
    except Exception as e:
        print(f"Error downloading model: {e}")
        exit(1)

    # --- Part 2: Pre-compute and save project embeddings ---
    project_data_path = os.path.join('data', 'projects.json')
    embeddings_save_path = 'project_embeddings.npy'

    print(f"Loading project data from '{project_data_path}'...")
    try:
        with open(project_data_path, 'r') as f:
            project_data = json.load(f)
        
        print("Pre-computing project embeddings...")
        descriptions = [p.get('description', '') for p in project_data]
        
        # Load the model from the local path we just saved it to
        local_model = SentenceTransformer(save_path)
        embeddings = local_model.encode(descriptions, convert_to_tensor=False)
        
        print(f"Saving embeddings to '{embeddings_save_path}'...")
        np.save(embeddings_save_path, embeddings)
        print("Project embeddings pre-computed and saved successfully.")

    except Exception as e:
        print(f"Error pre-computing embeddings: {e}")
        exit(1)


if __name__ == "__main__":
    main() 