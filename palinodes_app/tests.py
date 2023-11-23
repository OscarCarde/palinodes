from django.test import Client, TestCase
from .models import *
from .serializers import *

from django.core.files import File
from datetime import datetime, timedelta, timezone

class DirectoryTestCase(TestCase):

    def setUp(self):
        self.time = datetime.now(timezone.utc)

        self.user1 = User.objects.create(id=1000, username = "Alice")

        self.repo = Directory.objects.create(name="repo", owner = self.user1, description="a Test Repository", created= datetime.now(timezone.utc) - timedelta(3))

        self.dir1 = Directory.objects.create(name = "dir1", owner = self.user1, parent = self.repo, created = datetime.now(timezone.utc) - timedelta(days=2))
        self.dir2 = Directory.objects.create(name = "dir11", owner = self.user1, parent = self.dir1, created= datetime.now(timezone.utc) - timedelta(days=2))
        self.dir3 = Directory.objects.create(name = "dir111", owner = self.user1, parent = self.dir2, created= datetime.now(timezone.utc) - timedelta(days=2))

        with open("palinodes_app/testFiles/EvaKCarrots_1.aif", 'rb') as file:
            self.file = FileModel(parent=self.repo, uploaded= datetime.now() - timedelta(days=2))
            self.file.file.save("EvaKCarrots_1.aif", File(file))

        self.comment = Comment.objects.create(user=self.user1, repository=self.repo, comment="Test comment", timestamp=self.time)

    def tearDown(self):
        self.file.file.delete()
        super().tearDown()

    def test_is_repository(self):
        self.assertEquals(True, self.repo.is_repository)

    def test_directory_path(self):
        path1 = self.dir1.path
        self.assertEquals(f"1000/{self.repo.name}/dir1", path1)
        path2 = self.dir2.path
        self.assertEquals(f"1000/{self.repo.name}/dir1/dir11", path2)
        path3 = self.dir3.path
        self.assertEquals(f"1000/{self.repo.name}/dir1/dir11/dir111", path3)

    def test_last_edited(self):
        #check for last edited for file at repository level
        tolerance = timedelta(minutes=1)
        self.assertAlmostEqual(self.time, self.repo.last_edited, delta=tolerance, msg="last_edited property failed at repository level")
        #check for last edited for file at subdirectory level
        now = datetime.now(timezone.utc)
        self.comment2 = Comment.objects.create(user=self.user1, repository=self.dir1, comment="Test comment 2", timestamp=now)
        self.repo.refresh_from_db()
        self.assertAlmostEqual(now, self.repo.last_edited, delta=tolerance, msg="last_edited property failed at subdirectory level")

class FileTestCase(TestCase):
    '''
        Text fixture for File model
    '''

    def setUp(self) -> None:
        self.user = User.objects.create(id=1000, username="Phillip")
        self.repo = Directory.objects.create(name="test_repository", owner = self.user)
        self.dir = Directory.objects.create(name = "test_directory", owner = self.user, parent = self.repo)
        with open("palinodes_app/testFiles/EvaKCarrots_1.aif", 'rb') as file:
            self.file1 = FileModel(parent=self.dir)
            self.file1.file.save("EvaKCarrots_1.aif", File(file))

    def tearDown(self):
        self.file1.file.delete()
        super().tearDown()

    def test_filename(self):
        self.assertEqual("EvaKCarrots_1.aif", self.file1.filename, "The names don't match")


    def test_correct_path(self):
        self.assertEqual("1000/test_repository/test_directory/EvaKCarrots_1.aif", self.file1.file.name, "The paths don't match")

    def test_is_audiofile(self):
        self.assertEquals(True, self.file1.is_audiofile, f"is_audiofile should return True but returns {self.file1.is_audiofile}")

class ProfileTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(id=1000, username = "Alice")
        self.profile = self.user.profile
        self.repo1 = Directory.objects.create(pk=1000, name="test repo1", owner = self.user, description="1 Test Repository", created= datetime.now(timezone.utc) - timedelta(days=1))

        self.repo2 = Directory.objects.create(pk=2000, name="test repo2", owner = self.user, description="2 Test Repository", created= datetime.now(timezone.utc) - timedelta(days=2))

        self.repo3 = Directory.objects.create(pk=3000, name="test repo3", owner = self.user, description="3 Test Repository", created= datetime.now(timezone.utc) - timedelta(days=3))

        self.dir1 = Directory.objects.create(pk=4000, parent=self.repo2, name="test dir1", owner = self.user, description="1 Test Repository", created= datetime.now(timezone.utc))


    def test_repositories(self):

        actual_repositories = [repository.pk for repository in self.profile.repositories]
        self.assertListEqual([2000, 3000, 1000], actual_repositories, "the profile's repositories don't match")

    def test_collaborating_repositories(self):
        self.profile.refresh_from_db()

        actual_repositories = [repository.pk for repository in self.profile.all_repositories]
        self.assertListEqual([2000, 3000, 1000], actual_repositories, "the profile's repositories don't match")

class NotificationTestCase(TestCase):
    
    def setUp(self):
        pass

class RepositorySerializerTestCase(TestCase):
    def setUp(self) -> None:
        self.user1 = User.objects.create(id=1000, username = "Alice")
        self.user2 = User.objects.create(id=2000, username = "Bob")
        self.user3 = User.objects.create(id=3000, username = "Claire")
        self.description = "a test description for a test repository"
        self.repo = Directory.objects.create(id=1000, name="repo", description=self.description, owner = self.user1)
        self.repo.collaborators.add(self.user2)
        self.repo.collaborators.add(self.user3)
        self.serializer = RepositorySerializer(self.repo)

    def test_serializer_name(self):
        self.assertEquals('repo', self.serializer.data['name'], "repository names don't match")

    def test_serializer_description(self):
        self.assertEquals(self.description, self.serializer.data['description'], "repository description doesn't match")

    def test_serializer_owner(self):
        self.assertEquals('Alice', self.serializer.data['owner'], "repository owners don't match")

    def test_serializer_collaborators(self):
        self.assertListEqual(['Bob', 'Claire'], self.serializer.data["collaborators_names"], "The repository's collaborators' names don't match")

####__apis_tests__####
class DirectoryApiTestCase(TestCase):
    '''tests for the directory_api in views.py'''
    def setUp(self):
        self.user = User.objects.create(id=1000, username = "Alice", password="1234")
        self.dir = Directory.objects.create(pk=2000, name="test dir", owner = self.user, description="Test Directory")
        self.dir1 = Directory.objects.create(pk=3000, name="test subdir", owner = self.user, parent=self.dir)
        with open("palinodes_app/testFiles/cvt.docx", 'rb') as file:
            self.file = FileModel(pk=1000, parent=self.dir)
            self.file.file.save('cvt.docx', File(file))

    def tearDown(self):
        self.file.file.delete()
        super().tearDown()

    def test_api_endpoint(self):
        c = Client()
        c.login(username= self.user.username, password="1234")
        response = c.get(f"/api/directory?pk={self.dir.pk}")
        subdirectories = response.json()["subdirectories"]
        self.assertListEqual([{"pk":3000, "name":"test subdir", 'path': 'test dir/test subdir'}], subdirectories, "subdirectories don't match")
        files = response.json()["files"]
        self.assertDictEqual({"pk": 1000, "filename": "cvt.docx", "fileurl": "/media/1000/test%20dir/cvt.docx", "is_audiofile": False}, files[0], "files don't match")
        c.logout()

class NewDirectoryApiTestCase(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create(id=1000, username = "Alice", email="alice@alice.com", password="1234")
        self.dir = Directory.objects.create(pk=2000, name="test dir", owner = self.user, description="Test Directory")
        self.dir1 = Directory.objects.create(pk=3000, name="test subdir", owner = self.user, parent=self.dir)
        
    def test_new_directory(self):
        c = Client()
        c.force_login(self.user)
        response = c.post("/api/new-directory", {"name": "test subsubdir", "parent_pk": self.dir1.pk}, content_type="application/json")
        self.assertEquals(200, response.status_code, f"wrong status code, api failed to save new directory, instead gave:\n {response.json()['message']}")
        directory = Directory.objects.get(name="test subsubdir")
        if directory:
            directory.delete()
        c.logout()

class DeleteDirectoryApiTestCase(TestCase):
    def setUp(self):
        pass

class NewFileApiTestCase(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(id=1000, username = "Alice", password="1234")
        self.dir = Directory.objects.create(pk=2000, name="test dir", owner = self.user, description="Test Directory")
        
    
    
    def test_file_upload(self):
        c = Client()
        c.force_login(self.user)
        with open("palinodes_app/testFiles/EvaKCarrots_1.aif", 'rb') as file:
            response = c.post("/api/new-file", {"file": file, "parentpk": self.dir.pk})
        self.assertEquals(200, response.status_code, response.json()["message"])
        instance = FileModel.objects.get(parent=self.dir)
        self.assertIsNotNone(instance, "instance not saved")
        if instance:
            instance.delete()
        c.logout()

class DeleteFileApiTestCase(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create(id=1000, username = "Alice", password="1234")
        self.dir = Directory.objects.create(pk=2000, name="test dir", owner = self.user, description="Test Directory")
        with open("palinodes_app/testFiles/EvaKCarrots_1.aif", 'rb') as file:
            self.file = FileModel(parent=self.dir)
            self.file.file.save("EvaKCarrots_1.aif", File(file))

    def tearDown(self):
        self.file.file.delete()
        super().tearDown()

    def test_delete_file(self):
        c = Client()
        c.force_login(self.user)
        response = c.post("/api/delete-file", {"filepk": self.file.pk}, content_type="application/json")

        self.assertEquals(200, response.status_code, response.json()["message"])


class NotificationsApiTestCase(TestCase):
    #TODO
    pass

class NewCommentApiTestCase(TestCase):
    #TODO
    pass

class GetCommentsApiTestCase(TestCase):
    #TODO
    pass