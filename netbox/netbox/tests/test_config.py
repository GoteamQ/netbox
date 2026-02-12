from django.core.cache import cache
from django.test import override_settings, TestCase

from core.models import ConfigRevision
from netbox.config import clear_config, get_config


# Prefix cache keys to avoid interfering with the local environment
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'netbox-config-tests',
    }
}


class ConfigTestCase(TestCase):
    def setUp(self):
        super().setUp()
        ConfigRevision.objects.all().delete()
        clear_config()
        cache.clear()

    def tearDown(self):
        ConfigRevision.objects.all().delete()
        clear_config()
        cache.clear()
        super().tearDown()

    @override_settings(CACHES=CACHES)
    def test_config_init_empty(self):
        cache.clear()

        config = get_config()
        self.assertEqual(config.config, {})
        self.assertEqual(config.version, None)

        clear_config()

    @override_settings(CACHES=CACHES)
    def test_config_init_from_db(self):
        CONFIG_DATA = {'BANNER_TOP': 'A'}
        cache.clear()

        # Create a config but don't load it into the cache
        configrevision = ConfigRevision.objects.create(data=CONFIG_DATA)
        self.addCleanup(configrevision.delete)

        config = get_config()
        self.assertEqual(config.config, CONFIG_DATA)
        self.assertEqual(config.version, configrevision.pk)

        clear_config()

    @override_settings(CACHES=CACHES)
    def test_config_init_from_cache(self):
        CONFIG_DATA = {'BANNER_TOP': 'B'}
        cache.clear()

        # Create a config and load it into the cache
        configrevision = ConfigRevision.objects.create(data=CONFIG_DATA)
        self.addCleanup(configrevision.delete)
        configrevision.activate()

        config = get_config()
        self.assertEqual(config.config, CONFIG_DATA)
        self.assertEqual(config.version, configrevision.pk)

        clear_config()

    @override_settings(CACHES=CACHES, BANNER_TOP='Z')
    def test_settings_override(self):
        CONFIG_DATA = {'BANNER_TOP': 'A'}
        cache.clear()

        # Create a config and load it into the cache
        configrevision = ConfigRevision.objects.create(data=CONFIG_DATA)
        self.addCleanup(configrevision.delete)
        configrevision.activate()

        config = get_config()
        self.assertEqual(config.BANNER_TOP, 'Z')
        self.assertEqual(config.version, configrevision.pk)

        clear_config()
