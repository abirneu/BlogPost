from django.db import models
from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Post(models.Model):
    title = models.CharField(max_length=100)
    content = RichTextField()
    image = models.ImageField(upload_to='blog_images/', null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    tag = models.ManyToManyField(Tag)
    view_count = models.PositiveBigIntegerField(default=0)
    liked_user = models.ManyToManyField(User, related_name='liked_posts')

    def __str__(self):
        return self.title
    
    @property
    def read_time(self):
        """Estimates reading time in minutes"""
        words_per_minute = 200  # Average reading speed
        word_count = len(self.content.split())
        minutes = word_count / words_per_minute
        return max(1, round(minutes))  # Return at least 1 minute
    
class Comment(models.Model):
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile_pics/', default='profile_pics/default.jpg', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    
    def get_image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return '/media/profile_pics/default.jpg'

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        # Handle the old image before saving (if updating)
        if self.pk:
            try:
                old_profile = Profile.objects.get(pk=self.pk)
                if old_profile.image and self.image != old_profile.image:
                    # Delete old image if it's not the default
                    if (old_profile.image.name != 'profile_pics/default.jpg' and 
                        os.path.isfile(old_profile.image.path)):
                        os.remove(old_profile.image.path)
            except Profile.DoesNotExist:
                pass
            except Exception as e:
                print(f"Error handling old image: {e}")

        # Call the parent save() method first
        super().save(*args, **kwargs)

        # Process the image after saving if it's not the default
        if self.image and self.image.name != 'profile_pics/default.jpg':
            try:
                from PIL import Image
                img = Image.open(self.image.path)
                
                # Convert RGBA to RGB if needed
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                # Resize the image while maintaining aspect ratio
                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size)
                    
                # Save the processed image
                img.save(self.image.path, 'JPEG', quality=90)
            except Exception as e:
                print(f"Error processing image: {e}")

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.email
