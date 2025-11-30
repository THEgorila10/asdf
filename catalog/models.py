from django.db import models
from django.urls import reverse
import uuid
from django.contrib.auth.models import User
from datetime import date

class Genre(models.Model):
    """מודל המייצג סוגה (ז'אנר) של ספר (למשל, מדע בדיוני)."""
    name = models.CharField(
        max_length=200,
        unique=True, # מוודא שלא יהיו שני ז'אנרים עם אותו שם
        help_text="הזן סוגה עבור הספר (למשל, מדע בדיוני, שירה צרפתית וכו')"
    )

    def __str__(self):
        """מחרוזת לייצוג המודל (יחזיר את שם הסוגה)."""
        return self.name

    def get_absolute_url(self):
        """מחזיר את ה-URL כדי לגשת לסוגה ספציפית."""
        return reverse('genre-detail', args=[str(self.id)])

class Book(models.Model):
    """מודל המייצג ספר (אך לא עותק ספציפי)."""
    title = models.CharField(max_length=200)

    # ForeignKey משמש כי לספר יכול להיות רק סופר אחד, אבל לסופר יכולים להיות הרבה ספרים.
    # 'Author' הוא מודל שנגדיר בהמשך.
    author = models.ForeignKey('Author', on_delete=models.RESTRICT, null=True)

    summary = models.TextField(
        max_length=1000, help_text="הזן תיאור קצר של הספר"
    )
    isbn = models.CharField(
        'ISBN', max_length=13,
        unique=True, # מוודא שלכל ספר יש ISBN ייחודי
        help_text='13 תווים <a href="https://www.isbn-international.org/content/what-isbn">מספר ISBN</a>'
    )

    # ManyToManyField משמש כי סוגה יכולה להכיל הרבה ספרים, וספר יכול להשתייך להרבה סוגות.
    genre = models.ManyToManyField(
        Genre, help_text="בחר סוגה (ז'אנר) עבור ספר זה"
    )
    def display_genre(self):
        """Create a string for the Genre. This is required to display genre in Admin."""
        return ', '.join(genre.name for genre in self.genre.all()[:3])

    display_genre.short_description = 'Genre'
    def __str__(self):
        """מחרוזת לייצוג המודל (יחזיר את כותרת הספר)."""
        return self.title

    def get_absolute_url(self):
        """מחזיר את ה-URL כדי לגשת לספר ספציפי."""
        return reverse('book-detail', args=[str(self.id)])
    def get_absolute_url(self):
     """Returns the url to access a detail record for this book."""
     # אנחנו משתמשים בשם 'book-detail' שנגדיר עוד רגע ב-urls.py
     return reverse('book-detail', args=[str(self.id)])
class BookInstance(models.Model):
    """מודל המייצג עותק ספציפי של ספר (עותק שניתן להשאיל מהספרייה)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text="מזהה ייחודי עבור העותק הספציפי הזה בכל הספרייה")
    
    book = models.ForeignKey('Book', on_delete=models.RESTRICT, null=True)
    imprint = models.CharField(max_length=200) # פרטי ההדפסה
    due_back = models.DateField(null=True, blank=True) # תאריך החזרה
    language = models.ForeignKey('Language', on_delete=models.SET_NULL, null=True)
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

   

    @property
    def is_overdue(self):
     """Determines if the book is overdue based on due date and current date."""
     return bool(self.due_back and date.today() > self.due_back)
    # אלו ה-"choices" שדיברנו עליהם.
    LOAN_STATUS = (
        ('m', 'בתחזוקה'), # Maintenance
        ('o', 'מושאל'),  # On loan
        ('a', 'זמין'),    # Available
        ('r', 'שמור'),   # Reserved
    ) 
    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default='m', # ברירת המחדל היא "בתחזוקה"
        help_text='זמינות הספר',
    )
    

class Meta:
        ordering = ['due_back'] # סדר מיון ברירת מחדל: לפי תאריך ההחזרה
        permissions = (("can_mark_returned", "Set book as returned"),)
def __str__(self):
        """מחרוזת לייצוג המודל."""
        return f'{self.id} ({self.book.title})'
  
class Author(models.Model):
    """מודל המייצג סופר."""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('Died', null=True, blank=True)

    class Meta:
        ordering = ['last_name', 'first_name'] # מיון לפי שם משפחה, ואז שם פרטי

    def get_absolute_url(self):
        """מחזיר את ה-URL כדי לגשת לסופר ספציפי."""
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        """מחרוזת לייצוג המודל."""
        return f'{self.last_name}, {self.first_name}'

class Language(models.Model):
     name = models.CharField(max_length=100, help_text="הזן את שפת הספר (למשל, עברית, אנגלית, פרסית)")

     def __str__(self):
        return self.name