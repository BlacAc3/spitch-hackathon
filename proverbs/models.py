from django.db import models

class Proverb(models.Model):
    text = models.TextField(verbose_name="Yoruba Proverb Text")
    translation = models.TextField(verbose_name="English Translation", blank=True, null=True)
    audio = models.FileField(upload_to='proverb_audio/', verbose_name="Audio (TTS)", blank=True, null=True)

    def __str__(self):
        return self.text[:50] + "..." if len(self.text) > 50 else self.text

    class Meta:
        verbose_name = "Proverb"
        verbose_name_plural = "Proverbs"
