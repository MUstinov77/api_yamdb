import csv
import os
from django.core.management import BaseCommand, CommandError
from django.db.utils import IntegrityError

from django.conf import settings
from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User

FILE_DIR = os.path.join(
    settings.BASE_DIR,
    'static\\data'
)


def import_csv():
    with open(
        os.path.join(FILE_DIR, "category.csv"), encoding="utf-8"
    ) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")
        Category.objects.bulk_create(objs=[
            Category(
                id=row['id'],
                name=row['name'],
                slug=row['slug'],
            )
            for row in reader
        ])
        print(f'Файл {csvfile.name} загружен.')

    with open(
        os.path.join(FILE_DIR, "genre.csv"), encoding="utf-8"
    ) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")
        Genre.objects.bulk_create(objs=[
            Genre(
                id=row['id'],
                name=row['name'],
                slug=row['slug'],
            )
            for row in reader
        ])
        print(f'Файл {csvfile.name} загружен.')

    with open(
        os.path.join(FILE_DIR, "users.csv"), encoding="utf-8"
    ) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")
        User.objects.bulk_create(objs=[
            User(
                id=row['id'],
                username=row['username'],
                email=row['email'],
                role=row['role'],
                bio=row['bio'],
                first_name=row['first_name'],
                last_name=row['last_name'],
            )
            for row in reader
        ])
        print(f'Файл {csvfile.name} загружен.')

    with open(
        os.path.join(FILE_DIR, "titles.csv"), encoding="utf-8"
    ) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")
        Title.objects.bulk_create(objs=[
            Title(
                id=row['id'],
                name=row['name'],
                year=row['year'],
                category=Category.objects.get_or_create(
                    id=row['category']
                )[0],
            )
            for row in reader
        ])
        print(f'Файл {csvfile.name} загружен.')

    with open(
        os.path.join(FILE_DIR, "genre_title.csv"), encoding="utf-8"
    ) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")
        for row in reader:
            title, created = Title.objects.get_or_create(
                id=row['title_id']
            )
            genre, created = Genre.objects.get_or_create(
                id=row['genre_id']
            )
            title.genre.add(genre)
            title.save()
        print(f'Файл {csvfile.name} загружен.')

    with open(
        os.path.join(FILE_DIR, "review.csv"), encoding="utf-8"
    ) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")
        Review.objects.bulk_create(objs=[
            Review(
                id=row['id'],
                title=Title.objects.get_or_create(
                    id=row['title_id'])[0],
                text=row['text'],
                author=User.objects.get_or_create(
                    id=row['author'])[0],
                score=row['score'],
                pub_date=row['pub_date'],
            )
            for row in reader
        ])
        print(f'Файл {csvfile.name} загружен.')

    with open(
        os.path.join(FILE_DIR, "comments.csv"), encoding="utf-8"
    ) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")
        Comment.objects.bulk_create(objs=[
            Comment(
                review=Review.objects.get_or_create(
                    id=row['review_id']
                )[0],
                text=row['text'],
                author=User.objects.get_or_create(
                    id=row['author']
                )[0],
                pub_date=row['pub_date'],
            )
            for row in reader
        ])
        print(f'Файл {csvfile.name} загружен.')


class Command(BaseCommand):
    """Импортер данных из csv."""

    help = 'Импорт данных csv из /static/data/ в базу данных.'

    def handle(self, *args, **kwargs):
        try:
            import_csv()
        except IntegrityError:
            raise CommandError(
                'Очистите базу данных перед загрузкой файлов csv,'
                ' воспользуйтесь менеджмент командой flush')
        except FileNotFoundError:
            raise CommandError(
                'Файлы csv в папке static/data не найдены')
        except Exception:
            raise CommandError(
                'Непредвиденная ошибка при выполнении команды importcsv,'
                ' обратитесь к разработчикам'
            )
