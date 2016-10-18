import os
import time
import urllib
import sys
import datetime

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from modernomad.backup import BackupManager

class Command(BaseCommand):
    help = "Remove Old Backup Files."
    args = "[backup_count]"
    requires_system_checks = False

    def handle(self, *labels, **options):
        backup_count = settings.BACKUP_COUNT
        if labels or len(labels) > 1:
            backup_count = labels[0]
        
        manager = BackupManager()
        manager.remove_old_files(backup_count)
