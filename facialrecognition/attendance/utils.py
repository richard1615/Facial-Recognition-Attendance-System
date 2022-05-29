def message(last_face):
    if last_face[1] == -1:
        return [f"Attendance Marked: {last_face[0]}", ""]
    elif last_face[1] == 0:
        return [f"Attendance Marked: {last_face[0]}", "Try Again"]
    elif last_face[1] == 1:
        return [f"Attendance Marked: {last_face[0]}", "Attendance marked successfully"]
    else:
        return "Error"