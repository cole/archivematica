# -*- coding: utf8
import os
import shutil
import sys
import tempfile

from django.test import TestCase

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(THIS_DIR, '../lib/clientScripts')))

from main import models

import storeFileModificationDates


class TestStoreFileModification(TestCase):
    """Test storeFileModificationDates."""

    fixture_files = ['transfer.json', 'files-transfer-unicode.json']
    fixtures = [os.path.join(THIS_DIR, 'fixtures', p) for p in fixture_files]

    transfer_uuid = 'e95ab50f-9c84-45d5-a3ca-1b0b3f58d9b6'

    def test_store_file_modification_dates(self):
        """Test storeFileModificationDates.

        It should store file modification dates.
        """

        # Create files
        temp_dir = tempfile.mkdtemp()
        transfer = models.Transfer.objects.get(uuid=self.transfer_uuid)
        transfer_path = transfer.currentlocation.replace('%sharedPath%', temp_dir + '/')

        for f in models.File.objects.filter(transfer_id=self.transfer_uuid):
            path = f.currentlocation.replace('%transferDirectory%', transfer_path)
            dirname = os.path.dirname(path)
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            with open(path, 'w') as f:
                f.write(path.encode('utf8'))
            os.utime(path, (1339485682, 1339485682))

        try:
            # Store file modification dates
            storeFileModificationDates.main(
                self.transfer_uuid,
                temp_dir + '/'
            )

            # Assert files have expected modification times
            assert str(models.File.objects.get(pk='47813453-6872-442b-9d65-6515be3c5aa1').modificationtime) == '2012-06-12 07:21:22+00:00'
            assert str(models.File.objects.get(pk='60e5c61b-14ef-4e92-89ec-9b9201e68adb').modificationtime) == '2012-06-12 07:21:22+00:00'
            assert str(models.File.objects.get(pk='791e07ea-ad44-4315-b55b-44ec771e95cf').modificationtime) == '2012-06-12 07:21:22+00:00'
            assert str(models.File.objects.get(pk='8a1f0b59-cf94-47ef-8078-647b77c8a147').modificationtime) == '2012-06-12 07:21:22+00:00'

        finally:
            # Delete files
            shutil.rmtree(transfer_path)
