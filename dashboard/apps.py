from django.apps import AppConfig

import datetime
from django.apps import AppConfig
from django.core.signals import request_started

def deactivate_expired_sessions_on_start(sender, **kwargs):
    request_started.disconnect(deactivate_expired_sessions_on_start)

    from student.models import AcademicSession
    
    today = datetime.date.today()
    
    try:
        expired = AcademicSession.objects.filter(
            end_date__lt=today, 
            is_active=True
        )
        if expired.exists():
            count = expired.count()
            expired.update(is_active=False)
            print(f"\n[System] Startup check complete: Deactivated {count} expired sessions.")
    except Exception as e:
        print(f"\n[System Warning] Deactivation check skipped: {str(e)}")
        
class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard'
    
    def ready(self):
        request_started.connect(deactivate_expired_sessions_on_start)
