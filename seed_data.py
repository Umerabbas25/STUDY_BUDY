import os
import sys
import django

sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studybud.settings')
django.setup()

from django.contrib.auth.models import User
from base.models import Topics, Room, Messages

print(">>> Flushing all existing data...")

Messages.objects.all().delete()
Room.objects.all().delete()
Topics.objects.all().delete()
User.objects.filter(is_superuser=False).delete()

print("[OK] All data cleared!")

print(">>> Creating users...")

users_data = [
    {"username": "alex_dev",    "email": "alex@studybud.io",    "password": "pass1234", "first_name": "Alex",    "last_name": "Johnson"},
    {"username": "priya_codes", "email": "priya@studybud.io",   "password": "pass1234", "first_name": "Priya",   "last_name": "Sharma"},
    {"username": "markus_js",   "email": "markus@studybud.io",  "password": "pass1234", "first_name": "Markus",  "last_name": "Weber"},
    {"username": "sara_ux",     "email": "sara@studybud.io",    "password": "pass1234", "first_name": "Sara",    "last_name": "Kim"},
    {"username": "dev_omar",    "email": "omar@studybud.io",    "password": "pass1234", "first_name": "Omar",    "last_name": "Hassan"},
]

users = []
for u in users_data:
    user = User.objects.create_user(
        username=u["username"],
        email=u["email"],
        password=u["password"],
        first_name=u["first_name"],
        last_name=u["last_name"],
    )
    users.append(user)
    print(f"  [OK] Created user: @{user.username}")

print(">>> Creating topics...")

topics_data = ["Python", "JavaScript", "React", "Django", "Machine Learning", "UI/UX Design", "DevOps", "Next.js"]
topics = {}
for name in topics_data:
    t = Topics.objects.create(name=name)
    topics[name] = t
    print(f"  [OK] Created topic: {name}")

print(">>> Creating rooms...")

rooms_data = [
    {
        "host": users[0],
        "topic": topics["Python"],
        "name": "Python for Beginners",
        "description": "A friendly room for those just starting out with Python. We cover variables, loops, functions, and more. Everyone is welcome!",
    },
    {
        "host": users[0],
        "topic": topics["Django"],
        "name": "Django REST Framework Deep Dive",
        "description": "Advanced discussion on building powerful REST APIs with Django. We cover serializers, viewsets, authentication, and best practices.",
    },
    {
        "host": users[1],
        "topic": topics["Machine Learning"],
        "name": "Intro to Machine Learning with scikit-learn",
        "description": "Let's explore machine learning together! We go through classification, regression, clustering and model evaluation in Python.",
    },
    {
        "host": users[2],
        "topic": topics["JavaScript"],
        "name": "JavaScript ES2024 New Features",
        "description": "Deep dive into the latest ECMAScript features. Discussion on new syntax, performance improvements, and practical use cases.",
    },
    {
        "host": users[2],
        "topic": topics["React"],
        "name": "React Hooks and State Management",
        "description": "Learn how to effectively use useState, useEffect, useContext, and build your own custom hooks. Redux vs Zustand comparison.",
    },
    {
        "host": users[3],
        "topic": topics["UI/UX Design"],
        "name": "Figma to Code: Building Pixel-Perfect UIs",
        "description": "How to translate Figma designs into clean, maintainable CSS and HTML. We look at Flexbox, Grid, and component-driven design.",
    },
    {
        "host": users[4],
        "topic": topics["DevOps"],
        "name": "Docker and Kubernetes for Developers",
        "description": "Containerize your applications and learn to deploy with Kubernetes. From Dockerfile basics to CI/CD pipelines with GitHub Actions.",
    },
    {
        "host": users[3],
        "topic": topics["Next.js"],
        "name": "Building Full-Stack Apps with Next.js 14",
        "description": "Explore App Router, Server Components, and server actions in Next.js 14. Learn how to build production-ready full-stack applications.",
    },
]

rooms = []
for r in rooms_data:
    room = Room.objects.create(**r)
    rooms.append(room)
    print(f"  [OK] Created room: {room.name}")

print(">>> Creating messages...")

messages_data = [
    (users[1], rooms[0], "This room is super helpful! I just learned how list comprehensions work. Mind blown!"),
    (users[2], rooms[0], "Can someone explain the difference between *args and **kwargs? Still a bit confused."),
    (users[0], rooms[0], "@markus_js sure! *args collects extra positional arguments into a tuple, while **kwargs collects keyword arguments into a dict."),
    (users[4], rooms[0], "Great explanation! I struggled with this for weeks until it finally clicked for me."),

    (users[1], rooms[1], "The GenericViewSet vs ModelViewSet distinction was confusing me but this room cleared it up. Thanks!"),
    (users[4], rooms[1], "Can we talk about JWT authentication next? I always get confused about refresh token rotation."),
    (users[0], rooms[1], "Good idea @dev_omar! I will prepare a quick demo on SimpleJWT for the next session."),

    (users[0], rooms[2], "Really excited about this! Can we cover k-means clustering? I am building a recommendation engine."),
    (users[3], rooms[2], "k-means is great for that use case. Have you looked into DBSCAN for noisy datasets?"),
    (users[1], rooms[2], "Just ran my first logistic regression model. The accuracy was only 72%, any tips to improve?"),

    (users[3], rooms[3], "Optional chaining and nullish coalescing are absolute game changers for clean code!"),
    (users[4], rooms[3], "Agreed! Also, the new Array.at(-1) method is so much cleaner than arr[arr.length - 1]"),
    (users[2], rooms[3], "I just wish TypeScript adoption was faster, so many legacy codebases still using var"),

    (users[0], rooms[4], "Is there still a strong use case for Redux in 2024 or is Zustand the new standard?"),
    (users[1], rooms[4], "For large teams with complex state, Redux Toolkit is still solid. Zustand is better for smaller projects."),
    (users[4], rooms[4], "I switched from Redux to Jotai for my last project and never looked back. Much simpler mental model."),

    (users[2], rooms[5], "Figma auto-layout finally makes responsive design much easier to prototype!"),
    (users[0], rooms[5], "CSS Grid has gotten so powerful. I barely touch Flexbox anymore for page-level layouts."),
    (users[4], rooms[5], "The new CSS Container Queries are a total game-changer for truly component-level responsiveness."),

    (users[1], rooms[6], "Got my first Kubernetes cluster running locally with Minikube. It is complex but the docs are solid."),
    (users[3], rooms[6], "Docker Compose is still my go-to for local dev. Kube is overkill unless you really need it."),
    (users[2], rooms[6], "GitHub Actions for CI/CD is so seamless. Replaced my entire Jenkins setup in a weekend."),

    (users[0], rooms[7], "Server Actions in Next.js 14 feel like magic. No more writing separate API routes for simple mutations!"),
    (users[4], rooms[7], "The App Router took some getting used to but now I love it. Nested layouts are so clean."),
    (users[1], rooms[7], "How do you handle auth with Next.js 14? Is NextAuth still the recommended approach?"),
    (users[3], rooms[7], "I use Clerk for auth in Next.js. Super fast setup and handles all the edge cases for you."),
]

for msg_user, msg_room, msg_body in messages_data:
    Messages.objects.create(user=msg_user, room=msg_room, body=msg_body)

print(f"  [OK] Created {len(messages_data)} messages!")

print("\n" + "=" * 50)
print("  DATABASE SEEDED SUCCESSFULLY!")
print("=" * 50)
print(f"  Users:    {User.objects.filter(is_superuser=False).count()}")
print(f"  Topics:   {Topics.objects.count()}")
print(f"  Rooms:    {Room.objects.count()}")
print(f"  Messages: {Messages.objects.count()}")
print("=" * 50)
print("\nLogin credentials for all users: password = pass1234")
for u in users_data:
    print(f"   Username: {u['username']}")
