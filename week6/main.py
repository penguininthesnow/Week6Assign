from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import mysql.connector
from website import get_connect

app = FastAPI()

# 靜態檔案
app.mount("/static", StaticFiles(directory="static"), name="static")

# 模板引擎
templates = Jinja2Templates(directory="templates")


# Session Middleware 設定
app.add_middleware(SessionMiddleware, secret_key="your-secret-key") # 隨機字母 ，要改?


# Task 1 -- pages build
# Home Page
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/member", response_class=HTMLResponse)
def member(request: Request):
    # 未登入的就回首頁
    if "member_id" not in request.session:
        return RedirectResponse("/", status_code=303)
    
    conn = get_connect()
    cursor = conn.cursor(dictionary = True)
    cursor.execute("""
        SELECT message.id, message.content, member.name, message.member_id 
        FROM message
        JOIN member ON message.member_id = member.id
        ORDER BY message.id DESC
    """)
    messages = cursor.fetchall()

    return templates.TemplateResponse(
        "member.html",
        {
            "request": request,
            "name": request.session["name"],
            "messages": messages,
            "current_user_id": request.session["member_id"],
        }
    )

@app.get("/error", response_class=HTMLResponse)
def error(request: Request, message: str = ""):
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "message": message}
    )

# Sign up
@app.post("/signup")
def signup(name: str = Form(), email: str = Form(), password: str = Form()):
    conn = get_connect()
    cursor = conn.cursor(dictionary=True)
    # 檢查是否有重複的 email
    cursor.execute("SELECT * FROM member WHERE email=%s",(email,))
    exist = cursor.fetchone()

    if exist:
        return RedirectResponse("/error?message=重複的電子郵件", status_code=303)
    #新增資料
    cursor.execute(
        "INSERT INTO member(name, email, password) VALUES (%s, %s, %s)",(name, email, password)
    )
    conn.commit()

    return RedirectResponse("/", status_code=303)

# login verification
@app.post("/login")
def login(request: Request, email: str = Form(), password: str = Form()):
    conn = get_connect()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM member WHERE email=%s AND password=%s",
        (email, password)
    )
    user = cursor.fetchone()

    # 登入失敗
    if not user:
        return RedirectResponse("/error?message=電子郵件或密碼錯誤", status_code=303)
    
    # 登入成功就存入 session
    request.session["member_id"] = user["id"]
    request.session["email"] = user["email"]
    request.session["name"] = user["name"]

    return RedirectResponse("/member", status_code=303)


# 登出
@app.get("/logout")
def logout(request: Request):
    # 清除登入狀態
    request.session.clear()
    return RedirectResponse("/", status_code=303)

# 留言系統建立
@app.post("/createMessage")
def create_message(request: Request, content:str = Form()):
    # 如果沒有登入就送回首頁
    if "member_id" not in request.session:
        return RedirectResponse("/", status_code=303)
    
    conn = get_connect()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO message(member_id, content) VALUES(%s, %s)",
        (request.session["member_id"], content)
    )
    conn.commit()

    return RedirectResponse("/member", status_code=303)

# 刪除留言
@app.post("/deleteMessage")
def delete_message(request: Request, message_id: int = Form()):
    if "member_id" not in request.session:
        return RedirectResponse("/", status_code=303)
    
    conn = get_connect()
    cursor = conn.cursor()

    # 自己只能刪除自己的留言
    cursor.execute(
        "DELETE FROM message WHERE id=%s AND member_id=%s",
        (message_id, request.session["member_id"])
    )
    conn.commit()

    return RedirectResponse("/member", status_code=303)



