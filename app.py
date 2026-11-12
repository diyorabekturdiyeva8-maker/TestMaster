
import os
import sqlite3
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

DB = os.environ.get("DATABASE_PATH", "testmaster.db")

# TEST SAVOLLARI
savollar = [
    {
        "savol": "Bulutli hisoblashning asosiy xizmat modellari (Service Models) qaysilar?",
        "variantlar": [
            "A) IaaS, PaaS, SaaS",
            "B) HTTP, FTP, SMTP",
            "C) CPU, RAM, HDD",
            "D) Public, Private, Hybrid"
        ],
        "javob": "A",
        "mavzu": "Bulutli xizmat modellari",
        "izoh": "IaaS — infratuzilma, PaaS — platforma, SaaS — dasturiy ta’minot xizmat sifatida."
    },
    {
        "savol": "Quyidagilardan qaysi biri SaaS xizmatiga misol?",
        "variantlar": [
            "A) Amazon EC2",
            "B) Google Docs va Microsoft 365",
            "C) Heroku",
            "D) Virtual Mashina"
        ],
        "javob": "B",
        "mavzu": "SaaS modeli",
        "izoh": "SaaS — internet orqali foydalaniladigan tayyor dasturiy xizmat."
    },
    {
        "savol": "PaaS xizmat modelining asosiy vazifasi nima?",
        "variantlar": [
            "A) Tayyor ofis dasturlarini taqdim etish",
            "B) Ilovalarni yaratish, sinash va tarqatish uchun muhit berish",
            "C) Faqat fayllarni saqlash",
            "D) Internet tarmog‘ini ulash"
        ],
        "javob": "B",
        "mavzu": "PaaS modeli",
        "izoh": "PaaS dasturchilarga ilovalar yaratish va ishga tushirish uchun tayyor platforma beradi."
    },
    {
        "savol": "Public Cloud nima?",
        "variantlar": [
            "A) Faqat bitta tashkilot uchun bulut",
            "B) Internet orqali keng foydalanuvchilarga taqdim etiladigan bulut",
            "C) Internetga ulanmagan lokal tarmoq",
            "D) Faqat davlat idoralari foydalanadigan tarmoq"
        ],
        "javob": "B",
        "mavzu": "Bulutni joylashtirish modellari",
        "izoh": "Public Cloud internet orqali ko‘plab foydalanuvchilarga taqdim etiladi."
    },
    {
        "savol": "Bulutli hisoblashning asosiy afzalliklaridan biri nima?",
        "variantlar": [
            "A) Internet tezligi doimo kafolatlanishi",
            "B) Xavfsizlik 100% bo‘lishi",
            "C) Resurslarni talabga qarab kengaytirish yoki kamaytirish",
            "D) Barcha xizmatlar bepul bo‘lishi"
        ],
        "javob": "C",
        "mavzu": "Bulutli hisoblash afzalliklari",
        "izoh": "Bulutli xizmatlarda resurslarni ehtiyojga qarab oshirish yoki kamaytirish mumkin."
    }
]


# MA'LUMOTLAR BAZASI
def database():
    con = sqlite3.connect(DB)
    try:
        con.execute("""
            CREATE TABLE IF NOT EXISTS natijalar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ism TEXT NOT NULL,
                togri INTEGER,
                jami INTEGER,
                javoblar TEXT,
                sana TEXT
            )
        """)
        con.commit()
    finally:
        con.close()


database()


# BOSH SAHIFA
@app.route("/")
def home():
    return render_template("index.html")


# TEST ISHLASH
@app.route("/test", methods=["GET", "POST"])
def test():
    if request.method == "POST":
        ism = request.form.get("ism", "").strip()

        if not ism:
            return "Ism-familiyangizni kiriting!", 400

        javoblar = {}
        togri = 0

        for i, savol in enumerate(savollar):
            javob = request.form.get(str(i), "")
            javoblar[str(i)] = javob

            if javob == savol["javob"]:
                togri += 1

        con = sqlite3.connect(DB)
        try:
            cursor = con.execute("""
                INSERT INTO natijalar
                (ism, togri, jami, javoblar, sana)
                VALUES (?, ?, ?, ?, ?)
            """, (
                ism,
                togri,
                len(savollar),
                json.dumps(javoblar, ensure_ascii=False),
                datetime.now().strftime("%Y-%m-%d %H:%M")
            ))

            test_id = cursor.lastrowid
            con.commit()
        finally:
            con.close()

        return redirect(url_for("natija", test_id=test_id))

    return render_template("test.html", savollar=savollar)


# O'QUVCHI NATIJASI
@app.route("/natija/<int:test_id>")
def natija(test_id):
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row

    try:
        natija = con.execute(
            "SELECT * FROM natijalar WHERE id = ?",
            (test_id,)
        ).fetchone()
    finally:
        con.close()

    if natija is None:
        return "Natija topilmadi", 404

    javoblar = json.loads(natija["javoblar"])
    tahlil = []

    for i, savol in enumerate(savollar):
        tanlangan = javoblar.get(str(i), "")
        togri_javob = savol["javob"]

        tahlil.append({
            "savol": savol["savol"],
            "tanlangan": tanlangan,
            "togri": togri_javob,
            "mavzu": savol["mavzu"],
            "izoh": savol["izoh"],
            "xato": tanlangan != togri_javob
        })

    return render_template(
        "natija.html",
        natija=natija,
        tahlil=tahlil
    )


# ADMIN BOSHQARUV PANELI
@app.route("/admin")
def admin():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row

    try:
        natijalar = con.execute(
            "SELECT * FROM natijalar ORDER BY id DESC"
        ).fetchall()
    finally:
        con.close()

    jami_test = len(natijalar)
    oquvchilar = len(set(n["ism"] for n in natijalar))

    jami_togri = sum(n["togri"] for n in natijalar)
    jami_savol = sum(n["jami"] for n in natijalar)
    jami_xato = jami_savol - jami_togri

    foiz = round(jami_togri / jami_savol * 100, 1) if jami_savol else 0

    statistika = {}

    for savol in savollar:
        mavzu = savol["mavzu"]
        statistika[mavzu] = {"togri": 0, "xato": 0}

    for natija_item in natijalar:
        javoblar = json.loads(natija_item["javoblar"])

        for i, savol in enumerate(savollar):
            tanlangan = javoblar.get(str(i), "")

            if tanlangan == savol["javob"]:
                statistika[savol["mavzu"]]["togri"] += 1
            else:
                statistika[savol["mavzu"]]["xato"] += 1

    return render_template(
        "admin.html",
        natijalar=natijalar,
        jami_test=jami_test,
        oquvchilar=oquvchilar,
        jami_togri=jami_togri,
        jami_xato=jami_xato,
        foiz=foiz,
        statistika=statistika
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )
