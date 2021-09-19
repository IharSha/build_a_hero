from unittest import mock

from django.test import TestCase

from wwwhero.models import CharacterAttributes, Character, Inventory, User


class CharacterAttributesModelTests(TestCase):
    def setUp(self):
        self.u = User.objects.create_user(username='Bob', password='strong!1')
        self.char = Character.objects.create(user=self.u, name="Dylan")
        self.attrs = CharacterAttributes.objects.create(character=self.char)

    def test_upgrade(self):
        expected_hp_dmg = self.attrs.hp + self.attrs.dmg + self.attrs.LEVEL_UP_POINTS
        expected_luck = [self.attrs.luck, self.attrs.luck + 1]

        self.attrs.upgrade()
        actual_hp_dmg = self.attrs.hp + self.attrs.dmg

        self.assertEqual(actual_hp_dmg, expected_hp_dmg)
        self.assertEqual(self.attrs.max_hp, self.attrs.hp)
        self.assertIn(self.attrs.luck, expected_luck)


class CharacterModelTests(TestCase):
    def setUp(self):
        self.u = User.objects.create_user(username='Bob', password='strong!1')
        self.char = Character.objects.create(user=self.u, name="Dylan")
        self.attrs = CharacterAttributes.objects.create(character=self.char)
        self.inv = Inventory.objects.create(character=self.char)

    @mock.patch('wwwhero.models.CharacterAttributes.upgrade')
    def test_level_up(self, mock_attrs_upgrade):
        expected_level = self.char.level + 1

        self.char.level_up()

        self.assertEqual(expected_level, self.char.level)
        mock_attrs_upgrade.assert_called_once()

    def test_level_up_without_attributes(self):
        CharacterAttributes.objects.all().delete()

        self.char.level_up()
        self.assertEqual(CharacterAttributes.objects.all().count(), 1)
