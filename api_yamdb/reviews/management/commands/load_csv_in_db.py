import os
import csv

from django.core.management import BaseCommand
from django.conf import settings
from django.db import transaction

from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User

FILE_DIR = os.path.join(settings.BASE_DIR, 'static', 'data')

TABLES = {
    User: 'users.csv',
    Category: 'category.csv',
    Genre: 'genre.csv',
    Title: 'titles.csv',
    Review: 'review.csv',
    Comment: 'comments.csv',
}


class Command(BaseCommand):

    help = 'Импортирует данные из CSV файлов'

    def handle(self, *args, **kwargs):
        self.import_data()
        self.load_genre_title()

    def import_data(self, *args, **kwargs):
        for model, csv_file in TABLES.items():
            with open(
                os.path.join(FILE_DIR, csv_file),
                'r',
                encoding='utf-8'
            ) as file:
                reader = csv.DictReader(file)
                objects = [model(**data) for data in reader]
                with transaction.atomic():
                    model.objects.bulk_create(objects)

        self.stdout.write(self.style.SUCCESS('Все данные загружены'))

    def load_genre_title(self):
        with open(
            os.path.join(FILE_DIR, "genre_title.csv"), encoding="utf-8"
        ) as csvfile:
            reader = csv.DictReader(csvfile, delimiter=",")
            for row in reader:
                title, _ = Title.objects.get_or_create(id=row['title_id'])
                genre, _ = Genre.objects.get_or_create(id=row['genre_id'])
                title.genres.add(genre)
                title.save()

            self.stdout.write(f'Файл {csvfile.name} загружен.')
