from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn, csv

app = FastAPI()

students = {
    "Иван": {"age": 20, "grades": [5, 4, 3]},
    "Аня": {"age": 19, "grades": [4, 4, 5]}
}


# Validation
class Student(BaseModel):
    name: str = Field(min_length=2, max_length=20)
    age: int = Field(ge=7, le=30)
    grades: int = Field(ge=1, le=5)

class Grade(BaseModel):
    grade: int = Field(ge=1, le=5)

# 2. Show all students
@app.get('/students', summary='all students🎓')
def get_all_students():
    return students

# 3. Found a student by name
@app.get('/students/{name}', summary='get student👨🏻‍🎓')
def get_student(name: str):
    if name in students:
        return {name: students[name]}
    raise HTTPException(404, 'Not found')

# 1. Add a student
@app.post('/students', summary='add student💾')
def add_student(st: Student):
    if st.name in students:
        raise HTTPException(400, 'Already exists')
    students[st.name] = {"age": st.age, "grades": [st.grades]} # int to list
    return {'ok': True, 'msg': 'Student added'}

# Partially update
@app.put('/students/{name}', summary='update student👩🏻‍💻')
def update_student(name: str, st: Student):
    if name not in students:
        raise HTTPException(404, 'Not found')
    students[name] = {"age": st.age, "grades": [st.grades]}
    return {'ok': True, 'msg': 'Updated'}

# 4. Delete a student
@app.delete('/students/{name}', summary='delete student🗑️')
def delete_student(name: str):
    if name not in students:
        raise HTTPException(404, 'Not found')
    return {'ok': True, 'deleted': students.pop(name)}

# 5. Add a grade
@app.post('/students/{name}/grades', summary='add grade🙋🏻‍♂️')
def add_grade(name: str, g: Grade):
    if name not in students:
        raise HTTPException(404, 'Not found')
    students[name]['grades'].append(g.grade) # Add
    return {'ok': True, 'msg': f'Grade {g.grade} added'}

# 6. Students older then
@app.get('/students/age/{min_age}', summary='older than', tags=['Compare⚖️'])
def older_than(min_age: int):
    res = {name: data for name, data in students.items() if data['age'] > min_age}
    return res or {'msg': 'No students'}

# 7. Stuents with grade above threshold
@app.get('/students/grades/above/{thr}', summary='grade above', tags=['Compare⚖️'])
def grade_above(thr: int):
    res = {name: data for name, data in students.items() if any(g > thr for g in data['grades'])}
    return res or {'msg': 'No students'}

# 8. Export to CSV
@app.get('/students/export', summary='export CSV', tags=['CSV📊'])
def export_csv():
    try:
        with open("students.csv", "w", encoding="utf-8") as f:
            f.write("name;age;grades\n")
            for name, data in students.items():
                grades_str = ",".join(str(g) for g in data["grades"])
                f.write(f"{name};{data['age']};{grades_str}\n")
        return {"ok": True, "msg": "Exported"}
    except Exception as e:
        raise HTTPException(500, f"Export error: {e}")
    finally:
        print("Export attempt finished") 


# 9. Import from CSV
@app.post('/students/import', summary='import CSV', tags=['CSV📊'])
def import_csv():
    try:
        with open("students.csv", "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines[1:]:
                name, age, grades_str = line.strip().split(";")
                grades = [int(g) for g in grades_str.split(",") if g]
                students[name] = {"age": int(age), "grades": grades}

    except FileNotFoundError:
        raise HTTPException(404, "CSV not found")
    except Exception as e:
        raise HTTPException(500, f"Import error: {e}")
    else:
        return {"ok": True, "msg": "Imported"}
    finally:
        print("Import attempt finished")

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)