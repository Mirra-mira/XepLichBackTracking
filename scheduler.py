from simpleai.search import CspProblem, backtrack
import random
import math

def generate_schedule(num_classes, num_teachers, subjects, num_rooms):
    total_sessions = num_classes * len(subjects)
    min_rooms = math.ceil(total_sessions / 24)
    min_teachers = max(math.ceil(total_sessions / 24), len(subjects))
    max_sessions = num_rooms * 24

    if num_teachers < len(subjects):
        return {"error": f"Cần ít nhất {len(subjects)} giáo viên để dạy {len(subjects)} môn học!"}
    if num_rooms < min_rooms:
        return {"error": f"Cần ít nhất {min_rooms} phòng học cho {total_sessions} phiên học!"}
    if num_teachers < min_teachers:
        return {"error": f"Cần ít nhất {min_teachers} giáo viên cho {total_sessions} phiên học và {len(subjects)} môn!"}
    if total_sessions > max_sessions:
        return {"error": f"Với {num_rooms} phòng, tối đa chỉ xếp được {max_sessions} phiên học, nhưng cần {total_sessions} phiên!"}

    rooms = [f'Phòng {i}' for i in range(1, num_rooms + 1)]
    times = []
    days = ['thứ 2', 'thứ 3', 'thứ 4', 'thứ 5', 'thứ 6', 'thứ 7']
    for day in days:
        times.append(f'Sáng {day} (Tiết 1-2)')
        times.append(f'Sáng {day} (Tiết 3-4)')
        times.append(f'Chiều {day} (Tiết 1-2)')
        times.append(f'Chiều {day} (Tiết 3-4)')

    classes = [f'Lớp {i}' for i in range(1, num_classes + 1)]
    teachers = [f'GV{i}' for i in range(1, num_teachers + 1)]

    random.seed(42)
    teacher_subjects = {}
    available_subjects = subjects.copy()
    random.shuffle(available_subjects)
    for i, teacher in enumerate(teachers):
        if i < len(subjects):
            teacher_subjects[teacher] = available_subjects[i]
        else:
            teacher_subjects[teacher] = random.choice(subjects)

    assigned_subjects = set(teacher_subjects.values())
    if len(assigned_subjects) < len(subjects):
        return {"error": "Không thể gán để mỗi môn học có ít nhất một giảng viên!"}

    variables = []
    class_info = {}
    for cls in classes:
        for subject in subjects:
            session = f"{cls}_{subject}"
            variables.append(session)
            valid_teachers = [t for t, s in teacher_subjects.items() if s == subject]
            class_info[session] = {
                'class': cls,
                'subject': subject,
                'teacher': random.choice(valid_teachers)
            }

    domains = {var: [(time, room) for time in times for room in rooms] for var in variables}
    constraints = []

    def constraint_different_time_room(vars, vals):
        time1, room1 = vals[0]
        time2, room2 = vals[1]
        return (time1 != time2) or (room1 != room2)

    def constraint_different_teacher_time(vars, vals):
        var1, var2 = vars
        time1, _ = vals[0]
        time2, _ = vals[1]
        teacher1 = class_info[var1]['teacher']
        teacher2 = class_info[var2]['teacher']
        return time1 != time2 if teacher1 == teacher2 else True

    def constraint_different_time_same_class(vars, vals):
        var1, var2 = vars
        time1, _ = vals[0]
        time2, _ = vals[1]
        class1 = class_info[var1]['class']
        class2 = class_info[var2]['class']
        return time1 != time2 if class1 == class2 else True

    def constraint_spread_subjects(vars, vals):
        var1, var2 = vars
        time1, _ = vals[0]
        time2, _ = vals[1]
        subject1 = class_info[var1]['subject']
        subject2 = class_info[var2]['subject']
        if subject1 == subject2:
            session1 = time1.split(' (')[0]
            session2 = time2.split(' (')[0]
            return session1 != session2
        return True

    for i in range(len(variables)):
        for j in range(i + 1, len(variables)):
            var1, var2 = variables[i], variables[j]
            constraints.append(((var1, var2), constraint_different_time_room))

            if class_info[var1]['teacher'] == class_info[var2]['teacher']:
                constraints.append(((var1, var2), constraint_different_teacher_time))
            if class_info[var1]['class'] == class_info[var2]['class']:
                constraints.append(((var1, var2), constraint_different_time_same_class))
            if class_info[var1]['subject'] == class_info[var2]['subject']:
                constraints.append(((var1, var2), constraint_spread_subjects))

    problem = CspProblem(variables, domains, constraints)
    solution = backtrack(problem)

    if solution:
        result = []
        for var, (time, room) in sorted(solution.items()):
            info = class_info[var]
            result.append({
                "class": info['class'],
                "subject": info['subject'],
                "teacher": info['teacher'],
                "time": time,
                "room": room
            })
        return {"schedule": result}
    else:
        return {"error": "Không tìm được lịch học phù hợp."}