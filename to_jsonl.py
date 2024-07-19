import pandas as pd
import json

# Load the Excel file
file_path = 'Fine-tuning instruction set, Jul 18_with_paper.xlsx' 
df = pd.read_excel(file_path)

file_path = "prompt_template/system.txt"
system_prompt = ""
with open(file_path, 'r', encoding='utf-8') as file:
    system_prompt = file.read()



file_path = "questions/HIV_Set1_Jul8.csv"
q_df = pd.read_csv(file_path)

def find_prompt_by_question(question, q_df):
    # Search for the row where the question matches
    row = q_df[q_df['question'] == question]
    
    if not row.empty:
        # Return the corresponding prompt
        return row['prompt'].values[0]
    else:
        return None

# Function to convert each row to the desired JSONL format
def row_to_jsonl(row, q_df):
    return {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Paper Content: {row['Paper Content']};\n Question: {row['Question']};\n Prompt: {find_prompt_by_question(row['Question'], q_df)}"},
            {"role": "model", "content": f"Answer: {row['Answer']};\n Reference Sentences: {row['Reference Sentences']};\n Rationale: {row['Rationale']}"}
        ]
    }

def row_to_jsonl_individual(row, q_df):
    prompt = find_prompt_by_question(row['Question'], q_df)
    
    return {
        "System Content": system_prompt,
        "Paper Content": row['Paper Content'],
        "Question": row['Question'],
        "Prompt": prompt,
        "Answer": row['Answer'],
        "Reference Sentences": row['Reference Sentences'],
        "Rationale": row['Rationale']
    }



# Apply the function to each row and convert to JSONL format
jsonl_data = df.apply(lambda row: json.dumps(row_to_jsonl(row, q_df)), axis=1).tolist()

# Save JSONL data to a file
with open('training_set.jsonl', 'w', encoding='utf-8') as f:
    f.write('\n'.join(jsonl_data))


# Apply the function to each row and convert to JSONL format
jsonl_data = df.apply(lambda row: json.dumps(row_to_jsonl_individual(row, q_df), ensure_ascii=False), axis=1).tolist()

# Save JSONL data to a file
with open('training_set_individual.jsonl', 'w', encoding='utf-8') as f:
    f.write('\n'.join(jsonl_data))


