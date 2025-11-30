"""
Quick verification script to check all Django Signals and ORM features.
Run this from Django-signals_orm-0x04 directory: python verify_features.py
"""

print("\n=== Django Signals & ORM Features Verification ===\n")

# Check 1: Models have required fields
print("✓ Checking models.py...")
with open('messaging/models.py', 'r') as f:
    content = f.read()
    checks = [
        ('edited field in Message', 'edited = models.BooleanField'),
        ('parent_message field in Message', 'parent_message = models.ForeignKey'),
        ('read field in Message', 'read = models.BooleanField'),
        ('UnreadMessagesManager class', 'class UnreadMessagesManager'),
        ('MessageHistory model', 'class MessageHistory'),
        ('Notification model', 'class Notification'),
    ]
    for name, pattern in checks:
        if pattern in content:
            print(f"  ✓ {name} - FOUND")
        else:
            print(f"  ✗ {name} - MISSING")

# Check 2: Signals are implemented
print("\n✓ Checking signals.py...")
with open('messaging/signals.py', 'r') as f:
    content = f.read()
    checks = [
        ('post_save signal for notifications', '@receiver(post_save, sender=Message)'),
        ('pre_save signal for edit logging', '@receiver(pre_save, sender=Message)'),
        ('post_delete signal for cleanup', '@receiver(post_delete, sender=User)'),
        ('MessageHistory creation', 'MessageHistory.objects.create'),
        ('Notification creation', 'Notification.objects.create'),
    ]
    for name, pattern in checks:
        if pattern in content:
            print(f"  ✓ {name} - FOUND")
        else:
            print(f"  ✗ {name} - MISSING")

# Check 3: Apps.py imports signals
print("\n✓ Checking apps.py...")
with open('messaging/apps.py', 'r') as f:
    content = f.read()
    if 'import messaging.signals' in content and 'def ready' in content:
        print("  ✓ Signals imported in ready() method - FOUND")
    else:
        print("  ✗ Signals import - MISSING")

# Check 4: Views have required endpoints
print("\n✓ Checking views.py...")
with open('messaging/views.py', 'r') as f:
    content = f.read()
    checks = [
        ('history endpoint', 'def history'),
        ('unread messages endpoint', 'def unread'),
        ('delete_user view', 'def delete_user'),
        ('cached view', '@cache_page'),
        ('thread endpoint', 'def thread'),
    ]
    for name, pattern in checks:
        if pattern in content:
            print(f"  ✓ {name} - FOUND")
        else:
            print(f"  ✗ {name} - MISSING")

# Check 5: Admin registration
print("\n✓ Checking admin.py...")
with open('messaging/admin.py', 'r') as f:
    content = f.read()
    checks = [
        ('MessageHistory admin', '@admin.register(MessageHistory)'),
        ('Notification admin', '@admin.register(Notification)'),
    ]
    for name, pattern in checks:
        if pattern in content:
            print(f"  ✓ {name} - FOUND")
        else:
            print(f"  ✗ {name} - MISSING")

# Check 6: Settings configuration
print("\n✓ Checking settings.py...")
with open('messaging_app/settings.py', 'r') as f:
    content = f.read()
    checks = [
        ('CACHES configuration', 'CACHES'),
        ('LocMemCache backend', 'locmem.LocMemCache'),
        ('messaging app installed', "'messaging'"),
        ('AUTH_USER_MODEL', "AUTH_USER_MODEL = 'messaging.User'"),
    ]
    for name, pattern in checks:
        if pattern in content:
            print(f"  ✓ {name} - FOUND")
        else:
            print(f"  ✗ {name} - MISSING")

# Check 7: Tests are comprehensive
print("\n✓ Checking tests.py...")
with open('messaging/tests.py', 'r') as f:
    content = f.read()
    checks = [
        ('SignalsTestCase', 'class SignalsTestCase'),
        ('ThreadedConversationsTestCase', 'class ThreadedConversationsTestCase'),
        ('UnreadMessagesTestCase', 'class UnreadMessagesTestCase'),
        ('CachingTestCase', 'class CachingTestCase'),
        ('test_notification_created', 'def test_notification_created'),
        ('test_message_history_created', 'def test_message_history_created'),
        ('test_unread_messages_manager', 'def test_unread_messages_manager'),
    ]
    for name, pattern in checks:
        if pattern in content:
            print(f"  ✓ {name} - FOUND")
        else:
            print(f"  ✗ {name} - MISSING")

print("\n=== Verification Complete ===\n")
print("All required files have been checked.")
print("Run 'python manage.py check' to verify Django configuration.")
print("Run 'python manage.py test messaging' to run all tests.\n")
