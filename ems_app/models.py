from django.db import models
from django.utils import timezone

class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    up_id = models.ForeignKey('User_Project', on_delete=models.CASCADE, null=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    contact = models.CharField(max_length=20)
    password = models.CharField(max_length=128)

    def __str__(self):
        return self.username
    

class Project(models.Model):
    project_id  = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    # hardware_id = models.ForeignKey('Hardware',on_delete=models.CASCADE)
    total_power = models.DecimalField(max_digits=10, decimal_places=2)
    kw = models.DecimalField(max_digits=10, decimal_places=2)
    kva = models.DecimalField(max_digits=10, decimal_places=2)
    power_factor = models.DecimalField(max_digits=10, decimal_places=2)
    frequency = models.DecimalField(max_digits=10, decimal_places=2)
    current_l1 = models.DecimalField(max_digits=10, decimal_places=2)
    current_l2 = models.DecimalField(max_digits=10, decimal_places=2)
    current_l3 = models.DecimalField(max_digits=10, decimal_places=2)
    volt_l1 = models.DecimalField(max_digits=10, decimal_places=2)
    volt_l2 = models.DecimalField(max_digits=10, decimal_places=2)
    volt_l3 = models.DecimalField(max_digits=10, decimal_places=2)
    power_l1 = models.DecimalField(max_digits=10, decimal_places=2)
    power_l2 = models.DecimalField(max_digits=10, decimal_places=2)
    power_l3 = models.DecimalField(max_digits=10, decimal_places=2)
    time = models.TimeField(auto_now=True)
    last_updated = models.DateTimeField(default=timezone.now) 

    def __str__(self):
        return f"Project {self.project_id} by {self.user_id}"
    
    
class User_Project(models.Model):
    up_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User , on_delete=models.CASCADE)
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE)

    

class Hardware(models.Model):
    hardware_id = models.AutoField(primary_key=True)
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100)
    is_connected = models.BooleanField(default=False)
    connected_at = models.DateTimeField(auto_now_add=True)
    
    
class Data(models.Model):
    data_id = models.AutoField(primary_key=True)
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    json_data = models.CharField(max_length=1000)