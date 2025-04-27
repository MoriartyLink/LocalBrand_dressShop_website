from django.db import models

class Dress(models.Model):
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=8,decimal_places=2)
    size = models.CharField(max_length=50)
    image = models.ImageField(upload_to='dresses/')

    def __str__(self):
        return self.name

