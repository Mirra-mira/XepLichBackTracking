from simpleai.search import CspProblem, backtrack
import random
import math

def generate_schedule(num_classes, num_teachers, subjects, num_rooms):
    if num_classes <= 0 or num_teachers <= 0 or not subjects or num_rooms <= 0:
        return {"error": "Thông tin nhập vào không hợp lệ."}

    rooms = [f'Phong{i}' for i in range(1, num_rooms + 1)]
    times = [
        'Sáng thứ 2', 'Chiều thứ 2', 'Sáng thứ 3', 'Chiều thứ 3',
        'Sáng thứ 4', 'Chiều thứ 4', 'Sáng thứ 5', 'Chiều thứ 5',
        'Sáng thứ 6', 'Chiều thứ 6', 'Sáng thứ 7', 'Chiều thứ 7'
    ]
    classes = [f'Lop{i}' for i in range(1, num_classes + 1)]
    teachers = [f'GV{i}' for i in range(1, num_teachers + 1)]

    random.seed(42)
    teacher_subjects = {}
    available_subjects = subjects.copy()
    random.shuffle(available_subjects)
    for i, teacher in enumerate(teachers):
        teacher_subjects[teacher] = available_subjects[i % len(subjects)]

    assigned_subjects = set(teacher_subjects.values())
    if len(assigned_subjects) < len(subjects):
        return {"error": "Không thể gán đủ giáo viên cho từng môn học."}

    base_classes_per_subject = num_classes // len(subjects)
    extra_classes = num_classes % len(subjects)
    subject_assignments = []
    for i, subject in enumerate(subjects):
        count = base_classes_per_subject + (1 if i < extra_classes else 0)
        subject_assignments.extend([subject] * count)
    random.shuffle(subject_assignments)

    class_info = {}
    for cls, subject in zip(classes, subject_assignments):
        valid_teachers = [t for t, s in teacher_subjects.items() if s == subject]
        class_info[cls] = {'teacher': random.choice(valid_teachers), 'subject': subject}

    domains = {cls: [(time, room) for time in times for room in rooms] for cls in classes}
    constraints = []

    def constraint_different_time_room(_, vals):
        (time1, room1), (time2, room2) = vals
        return (time1 != time2) or (room1 != room2)

    def constraint_different_teacher_time(vars, vals):
        cls1, cls2 = vars
        (time1, _), (time2, _) = vals
        return class_info[cls1]['teacher'] != class_info[cls2]['teacher'] or time1 != time2

    def constraint_spread_subjects(vars, vals):
        cls1, cls2 = vars
        (time1, _), (time2, _) = vals
        return class_info[cls1]['subject'] != class_info[cls2]['subject'] or time1 != time2

    for i in range(len(classes)):
        for j in range(i + 1, len(classes)):
            constraints.append(((classes[i], classes[j]), constraint_different_time_room))
            if class_info[classes[i]]['teacher'] == class_info[classes[j]]['teacher']:
                constraints.append(((classes[i], classes[j]), constraint_different_teacher_time))
            if class_info[classes[i]]['subject'] == class_info[classes[j]]['subject']:
                constraints.append(((classes[i], classes[j]), constraint_spread_subjects))

    problem = CspProblem(classes, domains, constraints)
    solution = backtrack(problem)

    if solution:
        result = []
        for cls, (time, room) in sorted(solution.items()):
            teacher = class_info[cls]['teacher']
            subject = class_info[cls]['subject']
            result.append({
                "class": cls,
                "subject": subject,
                "teacher": teacher,
                "time": time,
                "room": room
            })
        return {"schedule": result}
    else:
        return {"error": "Không tìm được lịch học phù hợp."}