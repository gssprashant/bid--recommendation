import shutil
import os

def setup_deployment():
    """
    Set up deployment directory structure and copy required files
    """
    # Create directories if they don't exist
    os.makedirs("models", exist_ok=True)
    
    # Define source and destination paths
    notebook_dir = ".."  # Parent directory with notebook
    deployment_dir = "."  # Current directory
    
    # Copy model files
    try:
        model_files = ["bid_fee_model.joblib", "model_metadata.joblib"]
        for file in model_files:
            src = os.path.join(notebook_dir, "models", file)
            dst = os.path.join(deployment_dir, "models", file)
            if os.path.exists(src):
                shutil.copy2(src, dst)
                print(f"Copied {file}")
            else:
                print(f"Warning: Could not find {file}")
    except Exception as e:
        print(f"Error copying model files: {str(e)}")
    
    # Create .env file from template
    try:
        if not os.path.exists(".env") and os.path.exists(".env.template"):
            shutil.copy2(".env.template", ".env")
            print("Created .env file from template")
    except Exception as e:
        print(f"Error creating .env file: {str(e)}")
    
    print("\nDeployment setup complete!")

if __name__ == "__main__":
    setup_deployment()