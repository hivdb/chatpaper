from openai import OpenAI
from src.preset import PAPER_PATH
import time
from src.file_format import load_jsonl
import os

DATASET_PATH = PAPER_PATH / 'dataset'


def fine_tune_gpt4o():

    client = OpenAI()

    train_set = DATASET_PATH / 'by_paper' / 'train_set.jsonl'

    print('# Train set', len(load_jsonl(train_set)))

    train_file = client.files.create(
        file=open(train_set, "rb"),
        purpose="fine-tune"
    )

    val_set = DATASET_PATH / 'by_paper' / 'val_set.jsonl'
    val_file = client.files.create(
        file=open(val_set, "rb"),
        purpose="fine-tune"
    )

    client.fine_tuning.jobs.create(
        training_file=train_file.id,
        validation_file=val_file.id,
        model="gpt-4o-mini-2024-07-18",
        suffix='hivdb',
        seed=73,
        hyperparameters={
            'batch_size': 1,
            'n_epochs': 3,
        }
    )


def monitor_job():
    client = OpenAI()

    # List 10 fine-tuning jobs
    models = client.fine_tuning.jobs.list(limit=10)
    for i in models.data:
        print(i)

    job_id = input('Monitor job id:')

    while True:
        result = client.fine_tuning.jobs.list_events(fine_tuning_job_id=job_id)
        for i in result.data:
            print(i)
        # print(result)
        time.sleep(10)

    # Retrieve the state of a fine-tune
    # client.fine_tuning.jobs.retrieve("ftjob-abc123")

    # Cancel a job
    # client.fine_tuning.jobs.cancel("ftjob-abc123")

    # List up to 10 events from a fine-tuning job
    # client.fine_tuning.jobs.list_events(fine_tuning_job_id="ftjob-abc123", limit=10)

    # Delete a fine-tuned model (must be an owner of the org the model was created in)
    # client.models.delete("ft:gpt-3.5-turbo:acemeco:suffix:abc123")

    # completion = client.chat.completions.create(
    # model="ft:gpt-4o-mini:my-org:custom_suffix:id",
    # messages=[
    #     {"role": "system", "content": "You are a helpful assistant."},
    #     {"role": "user", "content": "Hello!"}
    # ]
    # )
    # print(completion.choices[0].message)


def del_ft_job():
    client = OpenAI()

    # List 10 fine-tuning jobs
    models = client.fine_tuning.jobs.list(limit=10)
    for i in models.data:
        print(i)

    job_id = input('Monitor job id:')

    result = client.models.delete(job_id)
    print(result)

