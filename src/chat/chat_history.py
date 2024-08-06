from datetime import datetime
from ..file_format import dump_csv
from ..file_format import load_csv
import re
from src.checksum import get_md5
from src.select_content.test_set import select_test_set


class ChatHistory:

    def __init__(self, file_path, chat_context, save_format='csv'):
        self.folder = file_path.parent / 'chat_history'
        self.folder.mkdir(exist_ok=True)

        self.save_format = save_format

        self.model = chat_context['model']
        self.chat_mode = chat_context['chat_mode']

        self.chatlog = self.load_file()

        # Remove item without question id
        self.chatlog = [
            i
            for i in self.chatlog
            # if i.get('question_id') and i['answer'] != ''
        ]

        today = datetime.today()
        self.date = today.strftime("%Y%m%d")

    def check_result_exist(self):
        for i in self.folder.iterdir():
            if 'csv' in i.suffix.lower():
                return True

        return False

    @property
    def save_file_name(self):
        return 'chat_history'

    @property
    def save_path(self):
        return self.folder / f"{self.save_file_name}.{self.save_format}"

    @property
    def chat_history(self):
        chat_history = []
        for i in self.chatlog:
            log = (
                f'Question: {i["question"]}\n\n'
                f'Evidence: {i["evidence"]}\n\n'
                f'Rationale: {i["rationale"]}\n\n'
                f'Answer: {i["answer"]}\n\n'

            )
            chat_history.append(log)
        return '\n\n'.join(chat_history)

    def log(self, resp, questions={}):
        answer = resp['answer']
        del resp['answer']

        answers = parse_answers(answer)

        # one question
        if 'question' in resp:
            [
                i.update({
                    'question': resp['question'],
                    'question_id': resp['question_id'],
                })
                for i in answers
            ]
            del resp['question']

        answers = [
            a
            for a in answers
            if all(
                k in a
                for k in [
                    'question',
                    'evidence',
                    'rationale',
                    'answer',
                    ]
            )
        ]

        if not answers:
            answers = [
                {
                    'question_id': qid,
                    'question': q,
                    'answer': '',
                    'explain': '',
                    'sentences': '',
                }
                for qid, q in questions.items()
            ]

        if questions:
            answers = map_answer_to_question(answers, questions)

        answers = [
            i
            for i in answers
            if i.get('question_id')
        ]

        # remove duplicated answer
        answers = {
            (i['question_id'], i['answer']): i
            for i in answers
        }

        answers = list(answers.values())

        performance = resp

        for a in answers:
            a.update(performance)
            a['model'] = self.model
            a['chat_mode'] = self.chat_mode
            a['date'] = self.date
            self.chatlog.append(a)

        self.dump_file()

        return answers

    def check_answer_exist(self, qid, question, content, run_number):
        # TODO, also check all parts being processed
        for i in self.chatlog:
            if self.find_answered_question(qid, question, content, run_number):
                return True
        return False

    def find_answered_question(
            self,
            qid,
            question,
            content,
            run_number,
            check_content=False,
            model_date=False):
        # TODO, for embedding method, the query of question always do once.
        result = []
        for i in self.chatlog:
            if int(i['run_number']) != run_number:
                continue

            if str(qid) != str(i['question_id']):
                continue

            # if question != i['question']:
            #     continue

            if not model_date:
                m1 = i['model'].split('-')[:2]
                m1 = '-'.join(m1)
                m2 = self.model.split('-')[:2]
                m2 = '-'.join(m2)
                if m1 != m2:
                    continue
            else:
                if self.model != i['model']:
                    continue

            if self.chat_mode != i['chat_mode']:
                continue

            # if check_content and (get_md5(content) != i.get('md5')):
            #     continue

            # if i['answer'] == '':
            #     continue

            result.append(i)

        return result

    def load_file(self):
        if not self.save_path.exists():
            return []
        return load_csv(self.save_path)

    def dump_log(self):
        self.dump_file()

    def dump_file(self):
        # TODO, header order
        self.save_format = 'csv'
        dump_csv(self.save_path, self.chatlog, headers=[
            'question_id',
            'question',
            'evidence',
            'rationale',
            'answer',
            'completion_tokens',
            'prompt_tokens',
            'total_tokens',
            'seconds',
            'model',
            'chat_mode',
            'date',
        ])


def parse_answers(answers):
    # TODO: some case the answer format is not always right, give warning.
    answer_list = []
    this_answer = []
    for i in answers.split('\n'):
        if i.startswith('Question') and this_answer:
            answer_list.append('\n'.join(this_answer))
            this_answer = [i]
        else:
            this_answer.append(i)

    if this_answer:
        answer_list.append('\n'.join(this_answer))

    return [
        parse_one_answer(i)
        for i in answer_list
    ]


def parse_one_answer(answer):
    answer = answer.split('\n')
    answer = [i for i in answer if i]
    result = {}
    keys = [
        'Question:',
        'Evidence:',
        'Rationale:',
        'Answer:',
    ]
    for i in answer:
        for k in keys:
            if i.startswith(k):
                t = k[:-1].lower()
                result[t] = i.replace(k, '').strip()

    if 'question' in result:
        q = result['question']
        match = re.match(r'^(?P<id>\d+)\.(?P<question>.*)', q)
        if match:
            result['question_id'] = int(match.groupdict()['id'])
            result['question'] = match.groupdict()['question'].strip()

    return result


def map_answer_to_question(answers, questions):
    # TODO, check answer
    for i in answers:
        if i.get('question_id'):
            continue

        if not i.get('question'):
            continue

        q = i['question']
        for k, v in questions.items():
            if q in v:
                i['question_id'] = k

    return answers


def fix_chat_history_question():

    test_set = select_test_set() / 'Papers'

    for i in test_set.iterdir():
        if not i.is_dir():
            continue

        history_folder = i / 'chat_history'
        if not history_folder.exists():
            # TODO give warning
            continue

        chat_history_file = history_folder / 'chat_history.csv'

        human_ans = {
            str(i['id']): i['question']
            for i in load_csv(i / 'human_answer.csv')
        }

        table = load_csv(chat_history_file)
        for i in table:
            if i['question'] != human_ans[i['question_id']]:
                # print(i['question_id'])
                # TODO dry run
                i['question'] = human_ans[i['question_id']]

        dump_csv(chat_history_file, table)


def fix_chat_history_run_number(run_number=1):

    test_set = select_test_set() / 'Papers'

    for i in test_set.iterdir():
        if not i.is_dir():
            continue

        history_folder = i / 'chat_history'
        if not history_folder.exists():
            # TODO give warning
            continue

        chat_history_file = history_folder / 'chat_history.csv'

        table = load_csv(chat_history_file)
        for i in table:
            if i.get('run_number', '') != '':
                continue
            i['run_number'] = run_number

        dump_csv(chat_history_file, table)


def remove_chat_history_run_number(run_number=100):

    # Protected runs
    if run_number <= 20:
        return

    test_set = select_test_set() / 'Papers'

    for i in test_set.iterdir():
        if not i.is_dir():
            continue

        history_folder = i / 'chat_history'
        if not history_folder.exists():
            # TODO give warning
            continue

        chat_history_file = history_folder / 'chat_history.csv'

        table = load_csv(chat_history_file)
        table = [
            i
            for i in table
            if int(i.get('run_number', '')) != run_number
        ]

        dump_csv(chat_history_file, table)


def remove_chat_history_run_number_and_qid(run_number=101, question_id=[
        2102,]):

    test_set = select_test_set() / 'Papers'

    for i in test_set.iterdir():
        if not i.is_dir():
            continue

        history_folder = i / 'chat_history'
        if not history_folder.exists():
            # TODO give warning
            continue

        chat_history_file = history_folder / 'chat_history.csv'

        table = load_csv(chat_history_file)
        table = [
            i
            for i in table
            if not (
                    int(i.get('run_number', 1)) == run_number and
                    int(i['question_id']) in question_id
                )
        ]
        dump_csv(chat_history_file, table)
