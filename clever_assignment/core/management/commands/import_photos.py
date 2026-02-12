import csv
from django.core.management.base import BaseCommand, CommandError
from clever_assignment.photos.models import Photo
from clever_assignment.photographers.models import Photographer

class Command(BaseCommand):
    """
    Django management command to import photos and photographers from photos.csv.
    """
    help = 'Import photos and photographers from photos.csv.'

    def handle(self, *args, **options):
        """
        Main handler for import command.
        Reads CSV and creates Photo and Photographer objects.
        """
        try:
            with open('photos.csv', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                photo_count = 0
                photographer_count = 0
                for row in reader:
                    try:
                        photographer, created = Photographer.objects.get_or_create(
                            url=row['photographer_url'],
                            defaults={
                                'name': row['photographer'],
                            }
                        )
                        if created:
                            photographer_count += 1

                        _, created = Photo.objects.get_or_create(
                            url=row['url'],
                            defaults={
                                'width': row['width'],
                                'height': row['height'],
                                'avg_color': row['avg_color'],
                                'src_original': row['src.original'],
                                'src_large2x': row['src.large2x'],
                                'src_large': row['src.large'],
                                'src_medium': row['src.medium'],
                                'src_small': row['src.small'],
                                'src_portrait': row['src.portrait'],
                                'src_landscape': row['src.landscape'],
                                'src_tiny': row['src.tiny'],
                                'alt': row['alt'],
                                'photographer': photographer,
                            }
                        )
                        if created:
                            photo_count += 1
                    except KeyError as e:
                        self.stderr.write(self.style.ERROR(f'Missing column in CSV: {e}'))
                    except Exception as e:
                        self.stderr.write(self.style.ERROR(f'Error importing row: {e}'))
                self.stdout.write(self.style.SUCCESS(f'Imported {photo_count} photos and {photographer_count} photographers.'))
        except FileNotFoundError:
            raise CommandError('photos.csv file not found.')
        except Exception as e:
            raise CommandError(f'Unexpected error: {e}')
