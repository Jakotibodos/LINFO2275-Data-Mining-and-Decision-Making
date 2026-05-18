import subprocess

#Define different configurations as dictionaries
experiments = [
    {
        "name": "small model",
        "args": ["--lr", "1e-3"]
    },
    {
        "name": "fast_learning",
        "args": ["--num_epochs", "2000", "--lr", "5e-3", "--batch_size", "1024"]
    },
    {
        "name": "long_train",
        "args": ["--num_epochs", "10000", "--initial_epsilon", "0.5"]
    }
]

def run_train(config):
    # 'train.py' should be the name of your original file
    command = ["python", "train.py"] + config["args"]
    
    # Change log and save paths so experiments don't overwrite each other
    command += ["--log_path", f"tensorboard_{config['name']}"]
    command += ["--saved_path", f"models_{config['name']}"]
    
    print(f"--- Starting Experiment: {config['name']} ---")
    subprocess.run(command)

if __name__ == "__main__":
    for exp in experiments:
        run_train(exp)