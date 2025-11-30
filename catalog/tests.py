from django.test import TestCase
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from catalog.models import Author
import os

from django.conf import settings

class DeploymentConfigurationTest(TestCase):
    """
    בדיקות לוודא שהגדרות הסביבה (Environment Variables)
    נטענות כמו שצריך מקובץ ה-.env
    """

    def test_env_file_is_loaded(self):
        # בדיקה 1: האם המשתנה מהקובץ באמת קיים בזיכרון של המחשב?
        # אנחנו בודקים אם המערכת רואה את המשתנה DJANGO_DEBUG שהגדרנו בקובץ
        env_debug = os.environ.get('DJANGO_DEBUG')
        
        # אנחנו מצפים שזה לא יהיה ריק (None)
        self.assertIsNotNone(env_debug, "Error: The .env file was NOT loaded into os.environ")
        
        # אנחנו מצפים שהערך יהיה 'True' (כמו שכתוב בקובץ שלך)
        self.assertEqual(env_debug, 'True')

    def test_secret_key_is_loaded(self):
        # בדיקה 2: האם הגדרות ג'נגו קיבלו מפתח סודי?
        # אנחנו מוודאים שהמפתח לא ריק
        self.assertTrue(len(settings.SECRET_KEY) > 0)
        
        # בדיקה למתקדמים: לוודא שאנחנו לא רצים עם מפתח ברירת המחדל הלא מאובטח
        # (רק אם שינית את המפתח בקובץ ה-.env למשהו משלך)
        # default_insecure = 'django-insecure-key-for-dev'
        # self.assertNotEqual(settings.SECRET_KEY, default_insecure)
class AuthorCreateViewTest(TestCase):
    """
    בדיקות לאתגר של MDN: בדיקת הדף ליצירת סופר חדש
    """

    def setUp(self):
        # 1. יצירת משתמש לבדיקה
        self.test_user = User.objects.create_user(username='test_user', password='123')
        
        # 2. הוספת הרשאה ספציפית למשתמש הזה (add_author)
        # אנחנו חייבים לתת לו את ההרשאה הזו, אחרת הוא לא יוכל להיכנס לדף
        content_type = ContentType.objects.get_for_model(Author)
        permission = Permission.objects.get(codename='add_author', content_type=content_type)
        self.test_user.user_permissions.add(permission)
        self.test_user.save()

    def test_redirect_if_not_logged_in(self):
        # בדיקה: אם אורח (לא מחובר) מנסה להיכנס - זרוק אותו ללוגין
        response = self.client.get(reverse('author-create'))
        self.assertRedirects(response, '/accounts/login/?next=/catalog/author/create/')

    def test_forbidden_if_logged_in_but_no_permission(self):
        # בדיקה: משתמש מחובר *בלי* הרשאות מנסה להיכנס - קבל שגיאה 403 (אסור)
        # יוצרים משתמש סתמי ללא הרשאות
        self.client.force_login(User.objects.create_user(username='no_perms', password='123'))
        
        response = self.client.get(reverse('author-create'))
        self.assertEqual(response.status_code, 403)

    def test_logged_in_with_permission(self):
        # בדיקה: המשתמש שלנו (עם ההרשאות) נכנס - הכל תקין (200)
        self.client.login(username='test_user', password='123')
        response = self.client.get(reverse('author-create'))
        
        self.assertEqual(response.status_code, 200)
        # מוודאים שמשתמשים בתבנית הנכונה
        self.assertTemplateUsed(response, 'catalog/author_form.html')

    def test_initial_date_of_death(self):
        # --- זה הלב של האתגר ---
        # בדיקה: האם השדה של תאריך הפטירה מכיל את הערך ההתחלתי שביקשו?
        self.client.login(username='test_user', password='123')
        response = self.client.get(reverse('author-create'))
        
        # גישה לטופס ולווידוא הערך ההתחלתי
        form_initial_value = response.context['form'].initial['date_of_death']
        self.assertEqual(form_initial_value, '11/11/2023')

    def test_create_author_success(self):
        # בדיקה: תהליך יצירה מלא (POST)
        self.client.login(username='test_user', password='123')
        
        # שליחת טופס עם נתונים
        response = self.client.post(reverse('author-create'), {
            'first_name': 'New',
            'last_name': 'Author',
            'date_of_birth': '2000-01-01',
            'date_of_death': '', # משאירים ריק
        })
        
        # מצפים להפניה (302) לדף הרשימה או לדף הסופר (תלוי איך הגדרת)
        # כאן אני מניח שזה מפנה לרשימת הסופרים או לפרטי הסופר
        self.assertEqual(response.status_code, 302) 
        
        # בדיקה שהסופר באמת נוצר במסד הנתונים
        self.assertTrue(Author.objects.filter(last_name='Author').exists())