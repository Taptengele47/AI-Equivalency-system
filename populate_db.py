from models import Session, User, University, UniversityCourse, Plan

session = Session()


du = University(name='Dhofar University')
session.add(du)
session.commit()  


courses = [
    UniversityCourse(title="Introduction to Programming", description="Basics of Python programming, loops, functions.", credits=3, department="Computer Science", language="en", university_id=du.id),
    UniversityCourse(title="Database Systems", description="SQL, relational models, normalization.", credits=3, department="Computer Science", language="en", university_id=du.id),
    
    UniversityCourse(title="مقدمة في البرمجة", description="أساسيات برمجة Python، الحلقات، الدوال.", credits=3, department="Computer Science", language="ar", university_id=du.id),
]
for c in courses:
    session.add(c)


plan = Plan(major="Computer Science", university_id=du.id)
session.add(plan)


student = User(username="student1", role="student")
student.set_password("123")
admin = User(username="admin1", role="admin")
admin.set_password("123")
session.add(student)
session.add(admin)

from models import Feedback
sample_feedback = Feedback(user_id=student.id, message="Great tool! Easy to use.")
session.add(sample_feedback)

session.commit()
session.close()
print("Data populated successfully!")