import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

# ---------------- Session State ----------------
if "token" not in st.session_state:
    st.session_state.token = None
if "role" not in st.session_state:
    st.session_state.role = None


def auth_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}


def logout():
    st.session_state.token = None
    st.session_state.role = None
    st.rerun()


# ---------------- Title ----------------
st.title("Student Management System")

# =================================================
# NOT LOGGED IN
# =================================================
if st.session_state.token is None:
    tab1, tab2 = st.tabs(["Register", "Login"])

    # -------- Register --------
    with tab1:
        role = st.selectbox("Register as", ["student", "teacher"])
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Register"):
            res = requests.post(
                f"{API_URL}/register",
                json={
                    "username": username,
                    "password": password,
                    "role": role
                }
            )

            if res.status_code == 200:
                st.success("Registered successfully. Please login.")
            else:
                st.error(res.text)

    # -------- Login --------
    with tab2:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login"):
            res = requests.post(
                f"{API_URL}/login",
                json={"username": username, "password": password}
            )

            if res.status_code == 200:
                st.session_state.token = res.json()["access_token"]

                me = requests.get(
                    f"{API_URL}/me",
                    headers=auth_headers()
                ).json()

                st.session_state.role = me["role"]
                st.rerun()
            else:
                st.error("Invalid credentials")

# =================================================
# LOGGED IN
# =================================================
else:
    st.sidebar.success(f"Logged in as {st.session_state.role}")
    st.sidebar.button("Logout", on_click=logout)

    # =================================================
    # STUDENT DASHBOARD
    # =================================================
    if st.session_state.role == "student":
        st.header("Student Dashboard")

        # ---- Student Profile ----
        profile = requests.get(
            f"{API_URL}/students/me",
            headers=auth_headers()
        )

        if profile.status_code == 200:
            p = profile.json()
            st.info(f"👤 **{p['username']}** | 🎓 Roll No: **{p['roll_no']}**")


        # ---- View Marks ----
        res = requests.get(
            f"{API_URL}/students/marks",
            headers=auth_headers()
        )

        if res.status_code == 200:
            data = res.json()
            st.subheader("My Marks")

            st.write(f"**Subject 1:** {data['s1']}")
            st.write(f"**Subject 2:** {data['s2']}")
            st.write(f"**Subject 3:** {data['s3']}")
            st.write(f"**Subject 4:** {data['s4']}")
            st.write(f"**Subject 5:** {data['s5']}")

            st.divider()
            st.success(f"**Total Marks:** {data['total']}")

        else:
            st.warning("Marks not assigned yet")

        # ---- Leaderboard ----
        st.divider()
        st.subheader("Leaderboard")

        lb = requests.get(
            f"{API_URL}/leaderboard",
            headers=auth_headers()
        )

        if lb.status_code == 200:
            st.table(lb.json())

    # =================================================
    # TEACHER DASHBOARD
    # =================================================
    elif st.session_state.role == "teacher":
        st.header("Teacher Dashboard")

        # ---- Fetch students ----
        students_res = requests.get(
            f"{API_URL}/students/users",
            headers=auth_headers()
        )

        students = students_res.json()

        if not students:
            st.warning("No students registered yet")
            st.stop()

        student_map = {s["username"]: s["id"] for s in students}

        st.subheader("Assign Roll Number & Marks")

        selected_student = st.selectbox(
            "Select Student",
            list(student_map.keys())
        )

        roll_no = st.text_input("Roll Number")

        s1 = st.number_input("Subject 1 Marks", 0, 100)
        s2 = st.number_input("Subject 2 Marks", 0, 100)
        s3 = st.number_input("Subject 3 Marks", 0, 100)
        s4 = st.number_input("Subject 4 Marks", 0, 100)
        s5 = st.number_input("Subject 5 Marks", 0, 100)

        if st.button("Save / Update"):
            payload = {
                "user_id": student_map[selected_student],
                "roll_no": roll_no,
                "s1": s1,
                "s2": s2,
                "s3": s3,
                "s4": s4,
                "s5": s5
            }

            res = requests.post(
                f"{API_URL}/marks",
                headers=auth_headers(),
                json=payload
            )

            if res.status_code == 200:
                st.success("Roll number and marks saved successfully")
            else:
                st.error(res.text)

        # ---- Leaderboard ----
        st.divider()
        st.subheader("Leaderboard")

        lb = requests.get(
            f"{API_URL}/leaderboard",
            headers=auth_headers()
        )

        if lb.status_code == 200:
            st.table(lb.json())
