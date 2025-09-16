from django.db import models
class Location(models.Model):
    name=models.CharField(max_length=150,unique=True)
    address=models.CharField(max_length=255,blank=True,null=True)
    def __str__(self): return self.name
