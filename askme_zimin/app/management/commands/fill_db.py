from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from faker import Faker
import random
from tqdm import tqdm
from app.models import Profile, Tag, Question, Answer, QuestionLike, AnswerLike
from django.db import transaction
import time

class Command(BaseCommand):
    help = 'Populate DB with test data'

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='Base multiplication factor')

    def generate_username(self, fake, i):
        return f"{fake.user_name()}_{i}"[:150]

    def generate_email(self, username):
        return f"{username}@example.com"

    def generate_unique_tag_name(self, fake, i):
        return f"{fake.word()}-{fake.word()}-{i}"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        ratio = kwargs['ratio']
        batch_size = ratio // 2
        fake = Faker()
        start_time = time.time()

        self.stdout.write("Creating users and profiles...")
        users = []
        for i in tqdm(range(ratio), desc="Users"):
            username = self.generate_username(fake, i)
            users.append(User(
                username=username,
                email=self.generate_email(username),
                password=fake.password(length=12)
            ))
        User.objects.bulk_create(users, batch_size=batch_size)

        profiles = [Profile(user=user) for user in tqdm(users, desc="Profiles")]
        Profile.objects.bulk_create(profiles, batch_size=batch_size)

        self.stdout.write("Creating tags...")
        tags = [
            Tag(name=self.generate_unique_tag_name(fake, i))
            for i in tqdm(range(ratio), desc="Tags")
        ]
        Tag.objects.bulk_create(tags, batch_size=batch_size)

        self.stdout.write("Creating questions...")
        questions = [
            Question(
                title=f"Question {i}: {fake.sentence()}"[:100], 
                text='\n\n'.join(fake.paragraphs(nb=random.randint(2, 5))),
                author=random.choice(profiles)
            )
            for i in tqdm(range(ratio * 10), desc="Questions")
        ]
        Question.objects.bulk_create(questions, batch_size=batch_size)

        self.stdout.write("Adding tags to questions...")
        for question in tqdm(questions, desc="Tags"):
            question.tags.set(random.sample(list(tags), random.randint(1, 3)))

        self.stdout.write("Creating answers...")
        answers = []
        answers_per_question = 10
        
        for question in tqdm(questions, desc="Answers"):
            answers.extend([
                Answer(
                    text='\n\n'.join(fake.paragraphs(nb=random.randint(1, 3))),
                    question=question,
                    author=random.choice(profiles),
                    is_correct=False
                )
                for i in range(answers_per_question)
            ])
        
        Answer.objects.bulk_create(answers, batch_size=batch_size*5)

        self.stdout.write("Creating question likes...")
        question_likes = []
        total_question_likes = ratio * 100
        seen_pairs = set()

        with tqdm(total=total_question_likes, desc="Question likes") as pbar:
            while len(question_likes) < total_question_likes:
                profile = random.choice(profiles)
                question = random.choice(questions)
                pair = (question.id, profile.id)
                
                if pair not in seen_pairs:
                    seen_pairs.add(pair)
                    question_likes.append(QuestionLike(
                        question=question,
                        user=profile,
                        value=random.choice([1, -1])
                    ))
                    pbar.update(1)

        QuestionLike.objects.bulk_create(question_likes, batch_size=batch_size)

        self.stdout.write("Creating answer likes...")
        answer_likes = []
        total_answer_likes = ratio * 100
        seen_pairs = set()

        with tqdm(total=total_answer_likes, desc="Answer likes") as pbar:
            while len(answer_likes) < total_answer_likes:
                profile = random.choice(profiles)
                answer = random.choice(answers)
                pair = (answer.id, profile.id)
                
                if pair not in seen_pairs:
                    seen_pairs.add(pair)
                    answer_likes.append(AnswerLike(
                        answer=answer,
                        user=profile,
                        value=random.choice([1, -1])
                    ))
                    pbar.update(1)

        AnswerLike.objects.bulk_create(answer_likes, batch_size=batch_size)

        elapsed_time = time.time() - start_time
        self.stdout.write(self.style.SUCCESS(
            f"\nDatabase populated successfully in {elapsed_time:.2f} seconds!\n"
            f"Users: {len(users)}\n"
            f"Tags: {len(tags)}\n"
            f"Questions: {len(questions)}\n"
            f"Answers: {len(answers)}\n"
            f"Question likes: {len(question_likes)}\n"
            f"Answer likes: {len(answer_likes)}\n"
        ))