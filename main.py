import streamlit as st
import hashlib
import json
import os

# Đường dẫn tới file JSON để lưu dữ liệu
DATA_FILE = "data.json"

# Hàm băm mật khẩu
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Hàm đọc dữ liệu từ file JSON
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    else:
        return {"users": {}, "tasks": {}}

# Hàm lưu dữ liệu vào file JSON
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# Tải dữ liệu từ file JSON khi khởi động ứng dụng
data = load_data()

# Khởi tạo session state cho người dùng và nhiệm vụ
if 'users' not in st.session_state:
    st.session_state['users'] = data.get("users", {})
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = None
if 'tasks' not in st.session_state:
    st.session_state['tasks'] = data.get("tasks", {}).get(st.session_state['username'], [])

# Chức năng đăng ký
def register(username, password):
    hashed_password = hash_password(password)
    if username in st.session_state['users']:
        st.error("Username already exists. Please choose a different username.")
    else:
        st.session_state['users'][username] = hashed_password
        save_data({"users": st.session_state['users'], "tasks": data.get("tasks", {})})
        st.success("Registration successful! Please log in.")

# Chức năng đăng nhập
def login(username, password):
    hashed_password = hash_password(password)
    if username in st.session_state['users'] and st.session_state['users'][username] == hashed_password:
        st.session_state['logged_in'] = True
        st.session_state['username'] = username
        st.session_state['tasks'] = data.get("tasks", {}).get(username, [])
        st.success("Login successful!")
    else:
        st.error("Invalid username or password.")

# Chức năng đăng xuất
def logout():
    st.session_state['logged_in'] = False
    st.session_state['username'] = None
    st.session_state['tasks'] = []
    st.info("Logged out successfully!")

# Chức năng ToDo List
def add_task(task):
    st.session_state['tasks'].append(task)
    data["tasks"][st.session_state['username']] = st.session_state['tasks']
    save_data(data)
    st.success("Task added!")

def delete_task(task_index):
    st.session_state['tasks'].pop(task_index)
    data["tasks"][st.session_state['username']] = st.session_state['tasks']
    save_data(data)
    st.success("Task deleted!")

def edit_task(task_index, new_task):
    st.session_state['tasks'][task_index] = new_task
    data["tasks"][st.session_state['username']] = st.session_state['tasks']
    save_data(data)
    st.success("Task updated!")

# Giao diện ứng dụng
st.title("ToDo List App")

# Sidebar điều hướng
st.sidebar.title("Navigation")
st.sidebar.title("Ấn vào LOGIN 2 lần để đăng nhập :)")
if not st.session_state['logged_in']:
    choice = st.sidebar.radio("Go to", ["Login", "Register"])
else:
    choice = st.sidebar.radio("Go to", ["Home", "Logout"])

# Trang đăng ký
if choice == "Register":
    st.subheader("Create a New Account")
    username = st.text_input("Username", key="register_username")
    password = st.text_input("Password", type="password", key="register_password")
    if st.button("Register"):
        if username and password:
            register(username, password)
        else:
            st.error("Please fill in both fields.")

# Trang đăng nhập
elif choice == "Login":
    st.subheader("Login to Your Account")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login"):  # Nút đăng nhập
        if username and password:
            login(username, password)

# Tùy chọn đăng xuất
elif choice == "Logout":
    logout()

# Trang quản lý ToDo List (dành cho người đã đăng nhập)
if st.session_state['logged_in'] and choice == "Home":
    st.subheader(f"Welcome, {st.session_state['username']}! Manage your ToDo List")

    # Nhập nhiệm vụ mới
    new_task = st.text_input("New Task")
    if st.button("Add Task"):
        if new_task:
            add_task(new_task)
        else:
            st.error("Task cannot be empty.")

    # Hiển thị danh sách nhiệm vụ với tùy chọn sửa và xóa
    for i, task in enumerate(st.session_state['tasks']):
        col1, col2, col3 = st.columns([6, 1, 1])
        col1.write(f"{i + 1}. {task}")
        
        # Sửa nhiệm vụ
        if col2.button("Edit", key=f"edit_{i}"):
            edited_task = st.text_input("Edit Task", value=task, key=f"edit_input_{i}")
            if st.button("Save Edit", key=f"save_{i}"):
                if edited_task:
                    edit_task(i, edited_task)
        
        # Xóa nhiệm vụ
        if col3.button("Delete", key=f"delete_{i}"):
            delete_task(i)
