import unittest
from core.disk_info import DiskBadgeInfo, UserProfileInfo


class TestDiskInfo(unittest.TestCase):
    def test_disk_badge_info_summaries(self):
        """Valida a geração de resumos em texto formatado para o header da UI."""
        badge = DiskBadgeInfo(
            target_path="D:\\",
            mountpoint="D:\\",
            model="Seagate BarraCuda 2TB",
            serial_number="WABC1234",
            total_bytes=2 * 1024 * 1024 * 1024 * 1024,
            used_bytes=1024 * 1024 * 1024 * 1024,
            free_bytes=1024 * 1024 * 1024 * 1024,
            percent_used=50.0,
            smart_status="Healthy",
            power_on_hours=5000,
            power_on_count=320,
            media_type="HDD",
            spindle_speed=7200,
            temperature_c=36,
            detected_users=[
                UserProfileInfo(username="Maria", profile_path="D:\\Users\\Maria"),
                UserProfileInfo(username="Joao", profile_path="D:\\Users\\Joao"),
            ],
        )

        self.assertIn("50.0%", badge.capacity_summary)
        self.assertIn("Maria, Joao", badge.users_summary)
        self.assertIn("5,000h", badge.power_on_summary)
        self.assertIn("320 ligações", badge.power_on_summary)
        self.assertIn("HDD", badge.hardware_media_summary)
        self.assertIn("7200 RPM", badge.hardware_media_summary)
        self.assertIn("36°C", badge.hardware_media_summary)


if __name__ == "__main__":
    unittest.main()
