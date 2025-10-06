from models import Session, User, University, UniversityCourse, Plan

session = Session()

# Add DU (Dhofar University)
du = University(name='Dhofar University')
session.add(du)
session.commit()  # Commit to get ID

# Sample courses for DU
courses = [
    UniversityCourse(title="Introduction to Programming", description="Basics of Python programming, loops, functions.", credits=3, department="Computer Science", language="en", university_id=du.id),
    UniversityCourse(title="Database Systems", description="SQL, relational models, normalization.", credits=3, department="Computer Science", language="en", university_id=du.id),
    # Arabic example
    UniversityCourse(title="مقدمة في البرمجة", description="أساسيات برمجة Python، الحلقات، الدوال.", credits=3, department="Computer Science", language="ar", university_id=du.id),
]
for c in courses:
    session.add(c)

# Sample plan for DU
plan = Plan(major="Computer Science", university_id=du.id)
session.add(plan)

# Sample users
student = User(username="student1", role="student")
student.set_password("123")
admin = User(username="admin1", role="admin")
admin.set_password("123")
session.add(student)
session.add(admin)

session.commit()
session.close()
print("Data populated successfully!")