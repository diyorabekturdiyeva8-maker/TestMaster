
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import json
from datetime import datetime

app = Flask(__name__)
DB = "testmaster.db"

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
        "izoh": "To‘g‘ri javob: A) IaaS, PaaS, SaaS. Bulutli hisoblashning uchta asosiy modeli mavjud: IaaS — infratuzilma xizmat sifatida, PaaS — platforma xizmat sifatida, SaaS — dasturiy ta’minot xizmat sifatida. B tarmoq protokollari, C kompyuter apparat qismlari, D esa bulutning joylashish modellari hisoblanadi."
    },
    {
        "savol": "Quyidagilardan qaysi biri SaaS (Software as a Service) ga misol bo‘la oladi?",
        "variantlar": [
            "A) Amazon EC2",
            "B) Google Docs va Microsoft 365",
            "C) Heroku",
            "D) Virtual Mashina (Virtual Machine)"
        ],
        "javob": "B",
        "mavzu": "SaaS modeli",
        "izoh": "To‘g‘ri javob: B) Google Docs va Microsoft 365. SaaS modelida foydalanuvchi dasturga internet brauzeri orqali, uni kompyuterga o‘rnatmasdan kiradi. Amazon EC2 — IaaS, Heroku — PaaS, virtual mashina esa IaaS doirasiga kiradi."
    },
    {
        "savol": "PaaS (Platform as a Service) xizmat modelining asosiy vazifasi nima?",
        "variantlar": [
            "A) Foydalanuvchiga faqat tayyor ofis dasturlarini taqdim etish",
            "B) Dasturchilarga o‘z ilovalarini yaratish, sinovdan o‘tkazish va tarqatish uchun muhit taqdim etish",
            "C) Kompyuterning qattiq diskini (HDD) internetda saqlash",
            "D) Internet tarmog‘ini ulash"
        ],
        "javob": "B",
        "mavzu": "PaaS modeli",
        "izoh": "To‘g‘ri javob: B. PaaS dasturchilarga ilovalar yaratish, sinash va ishga tushirish uchun tayyor platforma beradi. Ular server va tarmoq infratuzilmasini boshqarish bilan kamroq shug‘ullanadi. A — SaaS ga tegishli, C — bulutli saqlash xizmati, D esa PaaS vazifasi emas."
    },
    {
        "savol": "Public Cloud (Ommaviy bulut) nima?",
        "variantlar": [
            "A) Faqat bitta tashkilot yoki korxona uchun maxsus qurilgan bulut",
            "B) Resurslari internet orqali keng jamoatchilikka yoki istalgan foydalanuvchiga taqdim etiladigan bulut muhiti",
            "C) Internetga ulanmagan lokal tarmoq",
            "D) Faqat davlat idoralari foydalana oladigan maxfiy tarmoq"
        ],
        "javob": "B",
        "mavzu": "Bulutni joylashtirish modellari",
        "izoh": "To‘g‘ri javob: B. Public Cloud resurslari internet orqali ko‘plab foydalanuvchilarga taqdim etiladi. Masalan, AWS, Microsoft Azure va Google Cloud. A — Private Cloud ta’rifidir. C va D bulutli hisoblashning Public Cloud ta’rifi emas."
    },
    {
        "savol": "Bulutli hisoblashning asosiy afzalliklaridan biri nima?",
        "variantlar": [
            "A) Internet tezligi doimo 100% kafolatlanishi",
            "B) Ma’lumotlar xavfsizligi 100% ta’minlanib, hech qachon buzilmasligi",
            "C) Resurslarni talabga qarab tezda kengaytirish yoki kamaytirish (Scalability / Elasticity)",
            "D) Barcha xizmatlar mutlaqo bepul bo‘lishi"
        ],
        "javob": "C",
        "mavzu": "Bulutli hisoblash afzalliklari",
        "izoh": "To‘g‘ri javob: C. Bulutli hisoblash resurslarni talabga qarab oshirish yoki kamaytirish imkonini beradi. Bu Scalability va Elasticity deb ataladi. A — internet tezligi provayderga bog‘liq. B — hech qanday tizim 100% xavfsiz emas. D — bulutli xizmatlarning ko‘pchiligi pullik."
    }
]


# MA'LUMOTLAR BAZASI
def database():
    con = sqlite3.connect(DB)
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
        con.close()

        return redirect(url_for("natija", test_id=test_id))

    return render_template("test.html", savollar=savollar)


# O'QUVCHINING NATIJASI
@app.route("/natija/<int:test_id>")
def natija(test_id):

    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row

    natija = con.execute(
        "SELECT * FROM natijalar WHERE id = ?", (test_id,)
    ).fetchone()

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

    natijalar = con.execute(
        "SELECT * FROM natijalar ORDER BY id DESC"
    ).fetchall()

    con.close()

    jami_test = len(natijalar)
    oquvchilar = len(set(n["ism"] for n in natijalar))

    jami_togri = sum(n["togri"] for n in natijalar)
    jami_savol = sum(n["jami"] for n in natijalar)
    jami_xato = jami_savol - jami_togri

    foiz = round(jami_togri / jami_savol * 100, 1) if jami_savol else 0

    # MAVZULAR BO'YICHA TAHLIL
    statistika = {}

    for savol in savollar:
        mavzu = savol["mavzu"]

        if mavzu not in statistika:
            statistika[mavzu] = {"togri": 0, "xato": 0}

    for natija in natijalar:
        javoblar = json.loads(natija["javoblar"])

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
    app.run(debug=True)

