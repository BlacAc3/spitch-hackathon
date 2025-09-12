def setup():
    import os
    import django
    from django.conf import settings

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spitch_hackathon.settings')
    # settings.configure() #Remove settings configure as django.setup does this.  If you call settings.configure after django.setup it will raise an error
    django.setup()

def copy_proverbs_to_db():
    from proverbs.models import Proverb  # Import your Proverb model
    import csv
    csv_file_path = 'spitch_hackathon/proverbs.csv'  # Adjust path if needed

    with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader) # Skip the header row
        for row in reader:
            try:
                # Assuming your CSV has columns named 'proverbs' and 'meaning'
                # Adjust the column names to match your CSV file's headers
                text = row[0]
                translation = row[1]

                # Check if the proverb already exists in the database
                if not Proverb.objects.filter(text=text).exists():

                    # Create a new Proverb object and save it to the database
                    proverb = Proverb(text=text, translation=translation)
                    proverb.save()
                else:
                    print(f"Proverb '{text}' already exists in the database. Skipping.")


            except KeyError as e:
                print(f"Error: Missing column in CSV file - {e}")
            except Exception as e:
                print(f"Error creating Proverb: {e}")

if __name__ == "__main__":
    setup() # Required to configure Django settings and initialize Django
    copy_proverbs_to_db()
