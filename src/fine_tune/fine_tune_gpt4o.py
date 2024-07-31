from openai import OpenAI
from src.preset import PAPER_PATH
import time
import os


def fine_tune_gpt4o():

    client = OpenAI()

    TRAIN_SET = PAPER_PATH.parent / 'train_set.jsonl'

    train_file = client.files.create(
        file=open(TRAIN_SET, "rb"),
        purpose="fine-tune"
    )

    TRAIN_SET = PAPER_PATH.parent / 'val_set.jsonl'
    val_file = client.files.create(
        file=open(TRAIN_SET, "rb"),
        purpose="fine-tune"
    )

    client.fine_tuning.jobs.create(
        training_file=train_file.id,
        validation_file=val_file.id,
        model="gpt-4o-mini-2024-07-18",
        suffix='hivdb',
        hyperparameters={
            'batch_size': 1,
            'n_epochs': 1,
        }
    )


def monitor_job():

    client = OpenAI()

    # List 10 fine-tuning jobs
    print(client.fine_tuning.jobs.list(limit=10))

    job_id = input('Monitor job id:')

    while True:
        print(client.fine_tuning.jobs.list_events(fine_tuning_job_id=job_id, limit=10))
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
