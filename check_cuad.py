from datasets import load_dataset
dataset = load_dataset('theatticusproject/cuad-qa', trust_remote_code=True)
print("Keys:", dataset['train'].column_names)
print("Sample keys:", dataset['train'][0].keys())
