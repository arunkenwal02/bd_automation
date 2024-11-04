from sqlalchemy import create_engine
from django.conf import settings

db_settings = settings.DATABASES['default']
db_urls = (f"mysql+mysqldb://{db_settings['USER']}:{db_settings['PASSWORD']}@{db_settings['HOST']}:"
           f"{db_settings['PORT']}/{db_settings['NAME']}")
engine = create_engine(db_urls)